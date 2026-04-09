import json
import logging
import re
import uuid
from collections.abc import Iterator
from queue import Queue
from threading import Event, Thread

from openai import OpenAI

from harness.memory.conversation import Conversation
from harness.memory.task import Task, get_task_store
from harness.tools import TOOLS
from harness.tools.sub_agent import SubAgentTool
from harness.tools.task_list import ListTasksTool
from harness.tools.task_plan import PlanTaskTool
from harness.tools.task_update import UpdateTaskTool
from harness.utils.enums import EventType, Role

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}
TASK_TOOL_NAMES = {
    PlanTaskTool.name,
    UpdateTaskTool.name,
    ListTasksTool.name,
}

MAX_ITERATIONS = 25

DANGEROUS_SHELL_PATTERNS = [
    (re.compile(r"\brm\b"), "destructive command: rm"),
    (re.compile(r"\brmdir\b"), "destructive command: rmdir"),
    (re.compile(r"\bchmod\b"), "permission change: chmod"),
    (re.compile(r"\bmv\b"), "move/rename command: mv"),
]

SENSITIVE_FILE_PATTERNS = [
    re.compile(r"\.env($|\.)"),
    re.compile(r"credentials", re.IGNORECASE),
    re.compile(r"secrets?\."), re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"id_rsa"),
]


def _check_dangerous(
    name: str, args: dict
) -> str | None:
    if name == "run_shell":
        cmd = args.get("command", "")
        for pattern, reason in DANGEROUS_SHELL_PATTERNS:
            if pattern.search(cmd):
                return reason
    if name in ("read_file", "write_file"):
        path = args.get("path", "")
        for pattern in SENSITIVE_FILE_PATTERNS:
            if pattern.search(path):
                return f"sensitive file: {path}"
    return None


def serialize_tasks(tasks: list[Task]) -> list[dict]:
    return [
        {
            "id": t.id,
            "goal": t.goal,
            "status": t.status,
            "steps": [
                {"description": s.description, "status": s.status}
                for s in t.steps
            ],
        }
        for t in tasks
    ]


class Agent:
    def __init__(
        self,
        config: dict,
        conversation: Conversation,
    ) -> None:
        self.client = OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
        )
        self.model = config["model"]
        self.config = config
        self.conversation = conversation
        self._confirm_queue: Queue[bool] = Queue()
        self._confirm_event = Event()

    def run(self, message: str) -> Iterator[dict]:
        logger.info("User message: %s", message)
        self.conversation.add_user_message(message)

        for _ in range(MAX_ITERATIONS):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation.messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    stream=True,
                    stream_options={"include_usage": True},
                )
            except Exception as e:
                logger.error("Failed to reach model: %s", e)
                yield {"type": EventType.ERROR, "content": str(e)}
                break

            content = ""
            tool_calls = {}
            usage = None
            for chunk in response:
                if chunk.usage:
                    usage = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    content += delta.content
                    yield {
                        "type": EventType.TOKEN,
                        "content": delta.content,
                    }
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index not in tool_calls:
                            tool_calls[tc.index] = {
                                "id": tc.id,
                                "name": tc.function.name,
                                "arguments": "",
                            }
                        if tc.function.arguments:
                            tool_calls[tc.index][
                                "arguments"
                            ] += tc.function.arguments

            if not tool_calls:
                if content:
                    self.conversation.add_assistant_message(
                        {
                            "role": Role.ASSISTANT,
                            "content": content,
                        }
                    )
                yield {"type": EventType.DONE, "usage": usage}
                break

            self._add_tool_call_message(content, tool_calls)
            yield from self._execute_tool_calls(tool_calls)

    def confirm(self, approved: bool) -> None:
        self._confirm_queue.put(approved)

    def run_to_completion(self, message: str) -> str:
        result = ""
        for event in self.run(message):
            if event["type"] == EventType.TOKEN:
                result += event["content"]
        return result or "(no output)"

    def spawn(
        self, role: str, task: str, agent_id: str
    ) -> Iterator[dict]:
        logger.info(
            "Spawning sub-agent %s: role=%s", agent_id, role
        )
        system_prompt = (
            f"You are a {role}. Complete the following task"
            " thoroughly and return your result.\n\n"
            "You have access to tools. Use them as needed."
            " You are in the .workspace/ directory."
        )
        child = Agent(
            self.config, Conversation(system_prompt)
        )

        yield {
            "type": EventType.SUB_AGENT_START,
            "agent_id": agent_id,
            "role": role,
            "task": task,
        }

        result = ""
        for event in child.run(task):
            if event["type"] == EventType.TOKEN:
                result += event["content"]
            yield {
                "type": EventType.SUB_AGENT_UPDATE,
                "agent_id": agent_id,
                "event": event,
            }

        yield {
            "type": EventType.SUB_AGENT_END,
            "agent_id": agent_id,
            "result": result or "(no output)",
        }

    def _add_tool_call_message(
        self, content: str, tool_calls: dict
    ) -> None:
        self.conversation.add_assistant_message(
            {
                "role": Role.ASSISTANT,
                "content": content or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"],
                        },
                    }
                    for tc in tool_calls.values()
                ],
            }
        )

    def _execute_tool_calls(
        self, tool_calls: dict
    ) -> Iterator[dict]:
        yield {"type": EventType.TOOL_START}

        # Separate spawn calls from regular tool calls
        spawn_calls = {}
        regular_calls = {}
        for idx, tc in tool_calls.items():
            try:
                name = tc["name"]
                args = json.loads(tc["arguments"])
            except json.JSONDecodeError:
                yield {
                    "type": EventType.ERROR,
                    "content": "Malformed tool arguments:"
                    f" {tc['arguments']}",
                }
                self.conversation.add_tool_result(
                    tc["id"], "Error: malformed arguments"
                )
                continue

            if name == SubAgentTool.name:
                spawn_calls[idx] = (tc, args)
            else:
                regular_calls[idx] = (tc, args)

        # Execute regular tools sequentially
        for tc, args in regular_calls.values():
            name = tc["name"]
            logger.info("Tool call: %s(%s)", name, args)
            yield {
                "type": EventType.TOOL_CALL,
                "name": name,
                "args": args,
            }

            danger_reason = _check_dangerous(name, args)
            if danger_reason:
                logger.info(
                    "Dangerous tool call: %s — %s",
                    name,
                    danger_reason,
                )
                yield {
                    "type": EventType.TOOL_CONFIRM,
                    "name": name,
                    "args": args,
                    "reason": danger_reason,
                }
                approved = self._confirm_queue.get()
                if not approved:
                    result = (
                        "Tool call denied by user: "
                        + danger_reason
                    )
                    logger.info("Tool call denied: %s", name)
                    yield {
                        "type": EventType.TOOL_RESULT,
                        "result": result,
                    }
                    self.conversation.add_tool_result(
                        tc["id"], result
                    )
                    continue

            result = self._execute_single_tool(name, args)

            logger.info("Tool result: %s", result)
            yield {
                "type": EventType.TOOL_RESULT,
                "result": result,
            }

            self.conversation.add_tool_result(
                tc["id"], str(result)
            )

            if name in TASK_TOOL_NAMES:
                yield {
                    "type": EventType.TASK_UPDATE,
                    "tasks": serialize_tasks(
                        get_task_store().list_all()
                    ),
                }

        # Execute spawn calls in parallel
        if spawn_calls:
            yield from self._execute_parallel_spawns(
                spawn_calls
            )

        yield {"type": EventType.TOOL_END}

    def _execute_parallel_spawns(
        self, spawn_calls: dict
    ) -> Iterator[dict]:
        if len(spawn_calls) == 1:
            # Single spawn — no threading needed
            tc, args = next(iter(spawn_calls.values()))
            agent_id = uuid.uuid4().hex[:8]

            logger.info("Tool call: %s(%s)", tc["name"], args)
            yield {
                "type": EventType.TOOL_CALL,
                "name": tc["name"],
                "args": args,
            }

            result = ""
            for sub_event in self.spawn(
                role=args.get("role", Role.ASSISTANT),
                task=args.get("task", ""),
                agent_id=agent_id,
            ):
                if sub_event["type"] == EventType.SUB_AGENT_END:
                    result = sub_event["result"]
                yield sub_event

            self.conversation.add_tool_result(
                tc["id"], str(result)
            )
            yield {
                "type": EventType.TOOL_RESULT,
                "result": result,
            }
            return

        # Multiple spawns — run in parallel threads
        queue: Queue = Queue()

        def _run_spawn(
            tc: dict, args: dict, agent_id: str
        ) -> None:
            try:
                result = ""
                for sub_event in self.spawn(
                    role=args.get("role", Role.ASSISTANT),
                    task=args.get("task", ""),
                    agent_id=agent_id,
                ):
                    if (
                        sub_event["type"]
                        == EventType.SUB_AGENT_END
                    ):
                        result = sub_event["result"]
                    queue.put(sub_event)
                queue.put(
                    {
                        "_done": True,
                        "agent_id": agent_id,
                        "tc_id": tc["id"],
                        "result": result,
                    }
                )
            except Exception as e:
                queue.put(
                    {
                        "_done": True,
                        "agent_id": agent_id,
                        "tc_id": tc["id"],
                        "result": f"Error: {e}",
                    }
                )

        threads = []
        agent_ids = {}
        for tc, args in spawn_calls.values():
            agent_id = uuid.uuid4().hex[:8]
            agent_ids[agent_id] = tc

            logger.info("Tool call: %s(%s)", tc["name"], args)
            yield {
                "type": EventType.TOOL_CALL,
                "name": tc["name"],
                "args": args,
            }

            t = Thread(
                target=_run_spawn,
                args=(tc, args, agent_id),
                daemon=True,
            )
            threads.append(t)
            t.start()

        # Collect events from all threads
        done_count = 0
        total = len(threads)
        while done_count < total:
            event = queue.get()
            if event.get("_done"):
                done_count += 1
                tc = agent_ids[event["agent_id"]]
                self.conversation.add_tool_result(
                    tc["id"], str(event["result"])
                )
                yield {
                    "type": EventType.TOOL_RESULT,
                    "result": event["result"],
                }
            else:
                yield event

        for t in threads:
            t.join()

    def _execute_single_tool(
        self, name: str, args: dict
    ) -> str:
        if name in TOOL_MAP:
            try:
                return TOOL_MAP[name].execute(**args)
            except TypeError as e:
                return f"Error: {e}"
        return f"Error: tool '{name}' not found"

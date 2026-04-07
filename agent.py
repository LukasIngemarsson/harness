import json
import logging
from collections.abc import Iterator

from openai import OpenAI

from memory.conversation import Conversation
from memory.task import Task, get_task_store
from tools import TOOLS
from tools.sub_agent import SubAgentTool
from tools.task_list import ListTasksTool
from tools.task_plan import PlanTaskTool
from tools.task_update import UpdateTaskTool
from utils.enums import EventType, Role

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}
TASK_TOOL_NAMES = {
    PlanTaskTool.name,
    UpdateTaskTool.name,
    ListTasksTool.name,
}

MAX_ITERATIONS = 25


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
                    yield {"type": EventType.TOKEN, "content": delta.content}
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
                        {"role": Role.ASSISTANT, "content": content}
                    )
                yield {"type": EventType.DONE, "usage": usage}
                break

            self._add_tool_call_message(content, tool_calls)
            yield from self._execute_tool_calls(tool_calls)

    def run_to_completion(self, message: str) -> str:
        result = ""
        for event in self.run(message):
            if event["type"] == EventType.TOKEN:
                result += event["content"]
        return result or "(no output)"

    def spawn(self, role: str, task: str) -> str:
        logger.info("Spawning sub-agent: role=%s", role)
        system_prompt = (
            f"You are a {role}. Complete the following task"
            " thoroughly and return your result.\n\n"
            "You have access to tools. Use them as needed."
            " You are in the .workspace/ directory."
        )
        child = Agent(
            self.config, Conversation(system_prompt)
        )
        return child.run_to_completion(task)

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

        for tc in tool_calls.values():
            name = tc["name"]
            try:
                args = json.loads(tc["arguments"])
            except json.JSONDecodeError:
                yield {
                    "type": "error",
                    "content": "Malformed tool arguments:"
                    f" {tc['arguments']}",
                }
                self.conversation.add_tool_result(
                    tc["id"], "Error: malformed arguments"
                )
                continue

            logger.info("Tool call: %s(%s)", name, args)
            yield {"type": EventType.TOOL_CALL, "name": name, "args": args}

            result = self._execute_single_tool(name, args)

            logger.info("Tool result: %s", result)
            yield {"type": EventType.TOOL_RESULT, "result": result}

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

        yield {"type": EventType.TOOL_END}

    def _execute_single_tool(
        self, name: str, args: dict
    ) -> str:
        if name == SubAgentTool.name:
            return self.spawn(
                role=args.get("role", Role.ASSISTANT),
                task=args.get("task", ""),
            )
        if name in TOOL_MAP:
            try:
                return TOOL_MAP[name].execute(**args)
            except TypeError as e:
                return f"Error: {e}"
        return f"Error: tool '{name}' not found"

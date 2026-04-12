import json
import logging
import re
import time
import uuid
from collections.abc import Iterator
from queue import Queue
from threading import Event, Thread

from openai import OpenAI, Timeout

from harness.enums import EventType, Role
from harness.memory.conversation import (
    RECENT_MESSAGES_TO_KEEP,
    Conversation,
    estimate_tokens,
)
from harness.memory.task import get_task_store, serialize_tasks
from harness.tools import TOOLS
from harness.tools.base import ToolError
from harness.tools.message_agent import MessageAgentTool
from harness.tools.sub_agent import SubAgentTool
from harness.tools.task_list import ListTasksTool
from harness.tools.task_plan import PlanTaskTool
from harness.tools.task_update import UpdateTaskTool

logger = logging.getLogger(__name__)

_TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}
_TASK_TOOL_NAMES = {
    PlanTaskTool.name,
    UpdateTaskTool.name,
    ListTasksTool.name,
}

_MAX_ITERATIONS = 25
_MAX_TOOL_RETRIES = 2
_MAX_LLM_RETRIES = 3
_RETRY_DELAY = 1.0

_DANGEROUS_SHELL_PATTERNS = [
    (re.compile(r"\brm\b"), "destructive command: rm"),
    (re.compile(r"\brmdir\b"), "destructive command: rmdir"),
    (re.compile(r"\bchmod\b"), "permission change: chmod"),
    (re.compile(r"\bmv\b"), "move/rename command: mv"),
]

_SENSITIVE_FILE_PATTERNS = [
    re.compile(r"\.env($|\.)"),
    re.compile(r"credentials", re.IGNORECASE),
    re.compile(r"secrets?\."),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"id_rsa"),
]


class Agent:
    def __init__(
        self,
        config: dict,
        conversation: Conversation,
        tool_cache: dict | None = None,
    ) -> None:
        self.client = OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
            timeout=Timeout(
                connect=30.0,
                read=90.0,
                write=30.0,
                pool=30.0,
            ),
        )
        self.model = config["model"]
        self.config = config
        self.conversation = conversation
        self._confirm_queue: Queue[bool] = Queue()
        self._confirm_event = Event()
        self._tool_cache: dict[tuple, str] = (
            tool_cache if tool_cache is not None else {}
        )
        self._child_agents: dict[str, "Agent"] = {}

    def run(self, message: str) -> Iterator[dict]:
        logger.info("User message: %s", message)
        self.conversation.add_user_message(message)

        for _ in range(_MAX_ITERATIONS):
            yield from self._maybe_compact()

            response = None
            for attempt in range(1, _MAX_LLM_RETRIES + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.conversation.messages,
                        tools=_TOOL_DEFINITIONS,
                        tool_choice="auto",
                        stream=True,
                        stream_options={"include_usage": True},
                    )
                    break
                except Exception as e:
                    logger.warning(
                        "LLM request attempt %d/%d failed: %s",
                        attempt,
                        _MAX_LLM_RETRIES,
                        e,
                    )
                    if attempt >= _MAX_LLM_RETRIES:
                        logger.error(
                            "LLM request failed after %d attempts",
                            _MAX_LLM_RETRIES,
                        )
                        yield {"type": EventType.ERROR, "content": str(e)}
                    else:
                        time.sleep(_RETRY_DELAY * attempt)

            if response is None:
                break

            content = ""
            tool_calls = {}
            usage = None
            last_chunk_time = [time.monotonic()]
            stream_done = Event()

            def _watchdog() -> None:
                while not stream_done.is_set():
                    if stream_done.wait(timeout=10):
                        return
                    elapsed = (
                        time.monotonic() - last_chunk_time[0]
                    )
                    if elapsed > 90:
                        logger.error(
                            "Stream watchdog: no data for"
                            " %.0fs, closing",
                            elapsed,
                        )
                        try:
                            response.close()
                        except Exception:
                            pass
                        return

            watchdog = Thread(
                target=_watchdog, daemon=True
            )
            watchdog.start()

            try:
                for chunk in response:
                    last_chunk_time[0] = time.monotonic()
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
            except Exception as e:
                logger.error("Stream interrupted: %s", e)
                yield {
                    "type": EventType.ERROR,
                    "content": f"Stream interrupted: {e}",
                }
                break
            finally:
                stream_done.set()
                watchdog.join(timeout=1)

            if not tool_calls:
                if content:
                    self.conversation.add_assistant_message(
                        {
                            "role": Role.ASSISTANT,
                            "content": content,
                        }
                    )
                get_task_store().clear()
                yield {"type": EventType.DONE, "usage": usage}
                break

            self._add_tool_call_message(content, tool_calls)
            yield from self._execute_tool_calls(tool_calls)

    def confirm(self, approved: bool) -> None:
        self._confirm_queue.put(approved)

    def reflect(self, output: str) -> Iterator[dict]:
        logger.info("Starting reflection pass")
        reflection_prompt = (
            "Review your previous response and improve it."
            " Fix any errors, fill gaps, improve clarity,"
            " and ensure accuracy. If the response is"
            " already good, return it unchanged.\n\n"
            "Your previous response:\n"
            f"{output}"
        )
        self.conversation.add_user_message(reflection_prompt)

        for attempt in range(1, _MAX_LLM_RETRIES + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation.messages,
                    stream=True,
                    stream_options={"include_usage": True},
                )
                break
            except Exception as e:
                logger.warning(
                    "Reflection LLM attempt %d/%d failed: %s",
                    attempt,
                    _MAX_LLM_RETRIES,
                    e,
                )
                if attempt >= _MAX_LLM_RETRIES:
                    yield {
                        "type": EventType.ERROR,
                        "content": f"Reflection failed: {e}",
                    }
                    return
                time.sleep(_RETRY_DELAY * attempt)

        content = ""
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

        if content:
            self.conversation.add_assistant_message(
                {"role": Role.ASSISTANT, "content": content}
            )

        yield {"type": EventType.DONE, "usage": usage}

    def run_to_completion(self, message: str) -> str:
        result = ""
        for event in self.run(message):
            if event["type"] == EventType.TOKEN:
                result += event["content"]
        return result or "(no output)"

    def spawn(
        self, role: str, task: str, agent_id: str,
        reflect: bool = False,
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
            self.config,
            Conversation(system_prompt),
            tool_cache=self._tool_cache,
        )
        self._child_agents[agent_id] = child

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

        if reflect and result:
            logger.info(
                "Sub-agent %s starting reflection", agent_id
            )
            reflected = ""
            for event in child.reflect(result):
                if event["type"] == EventType.TOKEN:
                    reflected += event["content"]
                yield {
                    "type": EventType.SUB_AGENT_UPDATE,
                    "agent_id": agent_id,
                    "event": event,
                }
            if reflected:
                result = reflected

        yield {
            "type": EventType.SUB_AGENT_END,
            "agent_id": agent_id,
            "result": result or "(no output)",
        }

    def message_child(
        self, agent_id: str, message: str
    ) -> Iterator[dict]:
        child = self._child_agents.get(agent_id)
        if not child:
            yield {
                "type": EventType.ERROR,
                "content": f"No sub-agent with id '{agent_id}'",
            }
            return

        logger.info(
            "Messaging sub-agent %s: %s",
            agent_id,
            message[:100],
        )

        # Reopen the existing card with a labeled message
        yield {
            "type": EventType.SUB_AGENT_UPDATE,
            "agent_id": agent_id,
            "event": {
                "type": EventType.TOKEN,
                "content": (
                    f"\n\n[Coordinator]: {message}\n\n"
                ),
            },
        }

        result = ""
        for event in child.run(message):
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

    def compact(self) -> Iterator[dict]:
        old_messages = (
            self.conversation.get_messages_to_compact()
        )
        if not old_messages:
            yield {
                "type": EventType.SYSTEM_MESSAGE,
                "content": (
                    "Nothing to compact. Need more than"
                    f" {RECENT_MESSAGES_TO_KEEP} messages"
                    " in history (recent messages are"
                    " always kept intact)."
                ),
            }
            return

        fmt = Conversation._format_tokens
        old_count = len(self.conversation.messages)
        old_tokens = fmt(
            estimate_tokens(self.conversation.messages)
        )

        yield {
            "type": EventType.SYSTEM_MESSAGE,
            "content": (
                f"Compacting {len(old_messages)} messages..."
            ),
        }

        summary_prompt = [
            {
                "role": Role.SYSTEM,
                "content": (
                    "Summarize the following conversation"
                    " concisely. Preserve key facts,"
                    " decisions, tool results, and context"
                    " the assistant needs to continue"
                    " helping. Omit greetings and filler."
                ),
            },
            {
                "role": Role.USER,
                "content": json.dumps(
                    old_messages, indent=2
                ),
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=summary_prompt,
            )
            summary = response.choices[0].message.content
            if summary:
                self.conversation.apply_compaction(summary)
                new_tokens = fmt(
                    estimate_tokens(
                        self.conversation.messages
                    )
                )
                yield {
                    "type": EventType.SYSTEM_MESSAGE,
                    "content": (
                        f"Compacted {old_count} messages"
                        f" → {len(self.conversation.messages)}."
                        f" Tokens: {old_tokens}"
                        f" → {new_tokens}"
                    ),
                }
        except Exception as e:
            logger.warning(
                "Compaction failed: %s", e
            )
            yield {
                "type": EventType.SYSTEM_MESSAGE,
                "content": f"Compaction failed: {e}",
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

        # Separate agent calls from regular tool calls
        spawn_calls = {}
        message_calls = {}
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
            elif name == MessageAgentTool.name:
                message_calls[idx] = (tc, args)
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

            danger_reason = self._check_dangerous(name, args)
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

            if name in _TASK_TOOL_NAMES:
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

        # Execute message calls sequentially
        for tc, args in message_calls.values():
            logger.info(
                "Message agent: %s(%s)", tc["name"], args
            )
            yield {
                "type": EventType.TOOL_CALL,
                "name": tc["name"],
                "args": args,
            }

            agent_id = args.get("agent_id", "")
            message = args.get("message", "")
            result = ""
            for event in self.message_child(
                agent_id, message
            ):
                if event["type"] == EventType.SUB_AGENT_END:
                    result = event["result"]
                yield event

            self.conversation.add_tool_result(
                tc["id"], str(result)
            )
            yield {
                "type": EventType.TOOL_RESULT,
                "result": result,
            }

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
                reflect=args.get("reflect", False),
            ):
                if sub_event["type"] == EventType.SUB_AGENT_END:
                    result = sub_event["result"]
                yield sub_event

            tool_result = (
                f"[agent_id={agent_id}]\n\n{result}"
            )
            self.conversation.add_tool_result(
                tc["id"], tool_result
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
                    reflect=args.get("reflect", False),
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
            try:
                event = queue.get(timeout=120)
            except Exception:
                logger.error(
                    "Sub-agent queue timed out, %d/%d done",
                    done_count,
                    total,
                )
                yield {
                    "type": EventType.ERROR,
                    "content": "Sub-agent timed out",
                }
                break
            if event.get("_done"):
                done_count += 1
                tc = agent_ids[event["agent_id"]]
                tool_result = (
                    f"[agent_id={event['agent_id']}]"
                    f"\n\n{event['result']}"
                )
                self.conversation.add_tool_result(
                    tc["id"], tool_result
                )
                yield {
                    "type": EventType.TOOL_RESULT,
                    "result": event["result"],
                }
            else:
                yield event

        for t in threads:
            t.join()

    def _maybe_compact(self) -> Iterator[dict]:
        max_tokens = self.config.get(
            "max_context_tokens", 128_000
        )
        if not self.conversation.needs_compaction(
            max_tokens
        ):
            return
        yield from self.compact()

    @staticmethod
    def _check_dangerous(
        name: str, args: dict
    ) -> str | None:
        if name == "run_shell":
            cmd = args.get("command", "")
            for pattern, reason in _DANGEROUS_SHELL_PATTERNS:
                if pattern.search(cmd):
                    return reason
        if name in ("read_file", "write_file"):
            path = args.get("path", "")
            for pattern in _SENSITIVE_FILE_PATTERNS:
                if pattern.search(path):
                    return f"sensitive file: {path}"
        return None

    @staticmethod
    def _make_cache_key(
        name: str, args: dict
    ) -> tuple:
        return (name, json.dumps(args, sort_keys=True))

    def _execute_single_tool(
        self, name: str, args: dict
    ) -> str:
        if name not in TOOL_MAP:
            return f"Error: tool '{name}' not found"

        tool = TOOL_MAP[name]

        # Check cache for idempotent tools
        if tool.cacheable:
            cache_key = self._make_cache_key(name, args)
            if cache_key in self._tool_cache:
                logger.info(
                    "Cache hit: %s(%s)", name, args
                )
                return self._tool_cache[cache_key]

        # Execute with retry on retryable errors
        last_error = ""
        for attempt in range(1, _MAX_TOOL_RETRIES + 1):
            try:
                result = tool.execute(**args)
            except TypeError as e:
                return f"Error: {e}"
            except ToolError as e:
                last_error = f"Error: {e}"
                if not e.retryable or attempt >= _MAX_TOOL_RETRIES:
                    return last_error
                logger.warning(
                    "Tool %s attempt %d failed (retryable): %s",
                    name,
                    attempt,
                    e,
                )
                time.sleep(_RETRY_DELAY)
                continue

            # Cache successful results for idempotent tools
            if tool.cacheable:
                cache_key = self._make_cache_key(name, args)
                self._tool_cache[cache_key] = result

            return result

        return last_error or "Error: tool execution failed"

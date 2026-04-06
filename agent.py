import json
import logging
from collections.abc import Callable, Iterator

from openai import OpenAI

from memory.conversation import Conversation
from memory.task import Task, get_task_store
from tools import TOOLS
from tools.task_list import ListTasksTool
from tools.task_plan import PlanTaskTool
from tools.task_update import UpdateTaskTool
from utils.enums import Role

TASK_TOOL_NAMES = {PlanTaskTool.name, UpdateTaskTool.name, ListTasksTool.name}


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

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}


def create_agent(config: dict) -> Callable[[Conversation, str], Iterator]:
    client = OpenAI(base_url=config["base_url"], api_key=config["api_key"])
    model = config["model"]

    def run_agent(conversation: Conversation, user_message: str) -> Iterator[dict]:
        logger.info("User message: %s", user_message)
        conversation.add_user_message(user_message)

        while True:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=conversation.messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    stream=True,
                    stream_options={"include_usage": True},
                )
            except Exception as e:
                logger.error("Failed to reach model: %s", e)
                yield {"type": "error", "content": str(e)}
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
                    yield {"type": "token", "content": delta.content}
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.index not in tool_calls:
                            tool_calls[tool_call.index] = {
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "arguments": "",
                            }
                        if tool_call.function.arguments:
                            tool_calls[tool_call.index]["arguments"] += (
                                tool_call.function.arguments
                            )

            if not tool_calls:
                yield {"type": "done", "usage": usage}
                break

            conversation.add_assistant_message(
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
            yield {"type": "tool_start"}
            for tool_call in tool_calls.values():
                name = tool_call["name"]
                try:
                    args = json.loads(tool_call["arguments"])
                except json.JSONDecodeError:
                    yield {
                        "type": "error",
                        "content": "Malformed tool arguments:"
                        f" {tool_call['arguments']}",
                    }
                    conversation.add_tool_result(
                        tool_call["id"], "Error: malformed arguments"
                    )
                    continue

                logger.info("Tool call: %s(%s)", name, args)
                yield {"type": "tool_call", "name": name, "args": args}

                if name in TOOL_MAP:
                    try:
                        result = TOOL_MAP[name].execute(**args)
                    except TypeError as e:
                        result = f"Error: {e}"
                else:
                    result = f"Error: tool '{name}' not found"

                logger.info("Tool result: %s", result)
                yield {"type": "tool_result", "result": result}

                conversation.add_tool_result(tool_call["id"], str(result))

                if name in TASK_TOOL_NAMES:
                    yield {
                        "type": "task_update",
                        "tasks": serialize_tasks(
                            get_task_store().list_all()
                        ),
                    }

            yield {"type": "tool_end"}

    return run_agent

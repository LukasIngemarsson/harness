import json

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL
from memory.conversation import Conversation
from tools import TOOLS
from utils.enums import Role
from utils.io import role_prefix, tool_call_msg, tool_result_msg

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}


def run_agent(conversation: Conversation, user_message: str) -> None:
    conversation.add_user_message(user_message)

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation.get_messages(),
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            stream=True,
        )

        content = ""
        tool_calls = {}
        prefix_printed = False
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                if not prefix_printed:
                    print(role_prefix(Role.ASSISTANT), end="", flush=True)
                    prefix_printed = True
                content += delta.content
                print(delta.content, end="", flush=True)
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
            print("\n")
            break

        conversation.add_assistant_message({
            "role": Role.ASSISTANT,
            "content": content or None,
            "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                for tc in tool_calls.values()
            ],
        })
        for tool_call in tool_calls.values():
            name = tool_call["name"]
            args = json.loads(tool_call["arguments"])

            print('\n' + tool_call_msg(name, args))

            if name in TOOL_MAP:
                result = TOOL_MAP[name].execute(**args)
            else:
                result = f"Error: tool '{name}' not found"

            print(tool_result_msg(result))

            conversation.add_tool_result(tool_call["id"], str(result))

from openai import OpenAI
import json

from tools import TOOLS
from config import MODEL, BASE_URL, API_KEY
from utils.file import load_prompt
from utils.io import wrap_msg
from utils.enums import Role

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
TOOL_DEFINITIONS = [tool.to_api_format() for tool in TOOLS]
TOOL_MAP = {tool.name: tool for tool in TOOLS}


def run_agent(user_message: str) -> None:
    messages = [
        {"role": Role.SYSTEM, "content": load_prompt(Role.SYSTEM)},
        {"role": Role.USER, "content": user_message},
    ]

    print(wrap_msg(user_message, Role.USER))

    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_DEFINITIONS, tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print(wrap_msg(message, Role.SYSTEM))
            break

        messages.append(message)
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"[Tool call] {name}({args})")

            if name in TOOL_MAP:
                result = TOOL_MAP[name].execute(**args)
            else:
                result = f"Error: tool '{name}' not found"

            print(f"[Tool result] {result}\n")

            messages.append(
                {
                    "role": Role.TOOL,
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

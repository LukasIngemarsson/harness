import json

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL
from memory.conversation import Conversation
from tools import TOOLS
from utils.io import wrap_msg

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
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print(wrap_msg(message.content, "agent"))
            break

        conversation.add_assistant_message(message)
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"[Tool call] {name}({args})")

            if name in TOOL_MAP:
                result = TOOL_MAP[name].execute(**args)
            else:
                result = f"Error: tool '{name}' not found"

            print(f"[Tool result] {result}\n")

            conversation.add_tool_result(tool_call.id, str(result))

from datetime import date

from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from tools import TOOLS
from utils.file import load_prompt


def build_system_prompt() -> str:
    template = load_prompt("prompts", "system.txt")
    tool_list = "\n".join(f"- {tool.name}: {tool.description}" for tool in TOOLS)
    return template.format_map({"date": date.today(), "tools": tool_list})


def main() -> None:
    config = load_config()
    run_agent = create_agent(config)

    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)

    print("Agent ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "/clear":
            Conversation.clear_history()
            conversation = Conversation(build_system_prompt())
            print("Conversation cleared.\n")
            continue
        run_agent(conversation, user_input)

    conversation.save()
    print("Conversation saved.")


if __name__ == "__main__":
    main()

from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from prompts import build_system_prompt
from utils.enums import Role
from utils.io import error_msg, role_prefix, tool_call_msg, tool_result_msg
from utils.log import setup_logging


def main() -> None:
    setup_logging("main.log")
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
            conversation = Conversation(system_prompt)
            print("Conversation cleared.\n")
            continue

        prefix_printed = False
        for event in run_agent(conversation, user_input):
            match event["type"]:
                case "token":
                    if not prefix_printed:
                        print(role_prefix(Role.ASSISTANT), end="", flush=True)
                        prefix_printed = True
                    print(event["content"], end="", flush=True)
                case "tool_call":
                    print(tool_call_msg(event["name"], event["args"]))
                case "tool_result":
                    print(tool_result_msg(event["result"]))
                case "error":
                    print(error_msg(event["content"]))
                case "done":
                    print("\n")

    conversation.save()
    print("Conversation saved.")


if __name__ == "__main__":
    main()

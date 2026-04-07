from agent import Agent
from config import load_config
from memory.conversation import Conversation
from prompts import build_system_prompt, list_profiles
from utils.enums import Command, Role
from utils.io import error_msg, role_prefix, tool_call_msg, tool_result_msg
from utils.log import setup_logging


def main() -> None:
    setup_logging("main.log")
    config = load_config()

    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)
    agent = Agent(config, conversation)

    print(f"Agent ready. Type '{Command.EXIT}' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == Command.EXIT:
            break
        if user_input.lower() == Command.CLEAR:
            Conversation.clear_history()
            conversation = Conversation(system_prompt)
            agent = Agent(config, conversation)
            print("Conversation cleared.\n")
            continue
        if user_input.lower().startswith(Command.MODE):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print(f"Available: {', '.join(list_profiles())}\n")
                continue
            name = parts[1].strip().lower()
            if name not in list_profiles():
                print(f"Unknown profile. Available: {', '.join(list_profiles())}\n")
                continue
            system_prompt = build_system_prompt(name)
            conversation = Conversation(system_prompt)
            agent = Agent(config, conversation)
            print(f"Switched to {name} mode.\n")
            continue

        prefix_printed = False
        for event in agent.run(user_input):
            match event["type"]:
                case "token":
                    if not prefix_printed:
                        print(
                            role_prefix(Role.ASSISTANT),
                            end="",
                            flush=True,
                        )
                        prefix_printed = True
                    print(event["content"], end="", flush=True)
                case "tool_call":
                    print(
                        tool_call_msg(
                            event["name"], event["args"]
                        )
                    )
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

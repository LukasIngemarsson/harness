from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from utils.file import load_prompt


def main() -> None:
    config = load_config()
    run_agent = create_agent(config)

    print("Agent ready. Type 'exit' to quit.\n")
    conversation = Conversation(load_prompt("prompts", "system.txt"))
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        run_agent(conversation, user_input)


if __name__ == "__main__":
    main()

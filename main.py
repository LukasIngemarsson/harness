from agent import create_agent
from config import load_config
from memory.conversation import Conversation
from utils.file import load_prompt


def main() -> None:
    config = load_config()
    run_agent = create_agent(config)

    system_prompt = load_prompt("prompts", "system.txt")
    conversation = Conversation.load(system_prompt)

    print("Agent ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        run_agent(conversation, user_input)

    conversation.save()
    print("Conversation saved.")


if __name__ == "__main__":
    main()

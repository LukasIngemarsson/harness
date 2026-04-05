from agent import run_agent


def main() -> None:
    print("Agent ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        run_agent(user_input)


if __name__ == "__main__":
    main()

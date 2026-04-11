from harness.agent import Agent
from harness.config import load_config
from harness.memory.conversation import Conversation
from harness.prompts import build_system_prompt, switch_mode
from harness.utils.enums import Command, EventType, Role
from harness.utils.io import error_msg, role_prefix, tool_call_msg, tool_result_msg
from harness.utils.log import setup_logging


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
        if user_input.lower() == Command.COMPACT:
            for event in agent.compact():
                if event.get("content"):
                    print(event["content"])
            print()
            continue
        if user_input.lower() == Command.CONTEXT:
            print(agent.conversation.context_info())
            print()
            continue
        if user_input.lower().startswith(Command.MODE):
            result = switch_mode(user_input)
            print(f"{result['message']}\n")
            if result["prompt"]:
                system_prompt = result["prompt"]
                conversation = Conversation(system_prompt)
                agent = Agent(config, conversation)
            continue

        prefix_printed = False
        for event in agent.run(user_input):
            match event["type"]:
                case EventType.TOKEN:
                    if not prefix_printed:
                        print(
                            role_prefix(Role.ASSISTANT),
                            end="",
                            flush=True,
                        )
                        prefix_printed = True
                    print(event["content"], end="", flush=True)
                case EventType.TOOL_CALL:
                    print(tool_call_msg(event["name"], event["args"]))
                case EventType.TOOL_RESULT:
                    print(tool_result_msg(event["result"]))
                case EventType.TOOL_CONFIRM:
                    answer = (
                        input(f"\n[confirm] {event['name']}: {event['reason']} (y/n): ")
                        .strip()
                        .lower()
                    )
                    agent.confirm(answer in ("y", "yes"))
                case EventType.SUB_AGENT_START:
                    print(f"\n[sub-agent] {event['role']}: {event['task']}")
                case EventType.SUB_AGENT_UPDATE:
                    inner = event["event"]
                    if inner["type"] == EventType.TOKEN:
                        print(inner["content"], end="", flush=True)
                case EventType.SUB_AGENT_END:
                    print()
                case EventType.ERROR:
                    print(error_msg(event["content"]))
                case EventType.DONE:
                    print("\n")

    conversation.save()
    print("Conversation saved.")


if __name__ == "__main__":
    main()

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from harness.agent import Agent
from harness.config import load_config
from harness.enums import Command, EventType
from harness.memory.conversation import Conversation
from harness.prompts import build_system_prompt, switch_mode
from harness.utils.log import setup_logging

console = Console()


_ARGS_PREVIEW_LEN = 100
_INDENT = " " * 2
_INDENT2 = " " * 4
_COMMANDS = {
    Command.CLEAR: "Clear history",
    Command.MODE: "Switch profile",
    Command.COMPACT: "Compact context",
    Command.CONTEXT: "Show context info",
}


def _format_args(args: dict) -> str:
    parts = []
    for k, v in args.items():
        s = repr(v)
        if len(s) > 70:
            s = s[:70] + "…"
        parts.append(f"{k}={s}")
    result = ", ".join(parts)
    if len(result) > _ARGS_PREVIEW_LEN:
        result = result[:_ARGS_PREVIEW_LEN] + "…"
    return result


def _dim(msg: str) -> None:
    console.print(Text(msg, style="dim"))


def _render_assistant(tokens: str) -> None:
    if not tokens:
        return
    console.print()
    console.print(Text("ASSISTANT", style="bold green"))
    console.print(Markdown(tokens))


def _render_welcome(config: dict) -> None:
    console.print(
        Panel(
            f"[bold]Harness[/]  |  {config['model']}  |  "
            f"Type [green]/[/] for commands",
            border_style="blue",
            expand=False,
        )
    )
    console.print()


def _render_commands() -> None:
    for cmd, desc in _COMMANDS.items():
        console.print(Text(f"{_INDENT}{cmd:<12} {desc}", style="dim"))
    console.print(Text(f"{_INDENT}{'exit':<12} Quit", style="dim"))


def main() -> None:
    setup_logging("tui.log")
    config = load_config()

    system_prompt = build_system_prompt()
    conversation = Conversation.load(system_prompt)
    agent = Agent(config, conversation)

    known_tasks: dict[str, dict] = {}

    _render_welcome(config)

    while True:
        try:
            console.print()
            user_input = console.input("[bold blue]You → [/]").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input == "/":
            _render_commands()
            continue

        if user_input.lower() == Command.EXIT:
            break

        if user_input.lower() == Command.CLEAR:
            Conversation.clear_history()
            conversation = Conversation(system_prompt)
            agent = Agent(config, conversation)
            known_tasks.clear()
            console.clear()
            _render_welcome(config)
            _dim("Conversation cleared.")
            continue

        if user_input.lower() == Command.COMPACT:
            for event in agent.compact():
                if event.get("content"):
                    _dim(event["content"])
            continue

        if user_input.lower() == Command.CONTEXT:
            console.print(
                Panel(
                    agent.conversation.context_info(),
                    title="[bold]Context[/]",
                    border_style="dim",
                    expand=False,
                )
            )
            continue

        if user_input.lower().startswith(Command.MODE):
            result = switch_mode(user_input)
            _dim(result["message"])
            if result["prompt"]:
                system_prompt = result["prompt"]
                conversation = Conversation(system_prompt)
                agent = Agent(config, conversation)
            continue

        # --- Agent run ---
        tokens = ""
        sub_agents: dict[str, dict] = {}
        sub_counter = 0

        try:
            for event in agent.run(user_input):
                match event["type"]:
                    case EventType.TOKEN:
                        tokens += event["content"]

                    case EventType.TOOL_CALL:
                        args_str = _format_args(event["args"])
                        _dim(f"{_INDENT}● {event['name']}({args_str})")

                    case EventType.TOOL_RESULT:
                        pass

                    case EventType.TOOL_CONFIRM:
                        console.print()
                        console.print(
                            Text(
                                f"{_INDENT}⚠ {event['name']}: {event['reason']}",
                                style="bold yellow",
                            )
                        )
                        answer = (
                            console.input(
                                f"{_INDENT}[yellow]Approve? (y/n):[/] "
                            )
                            .strip()
                            .lower()
                        )
                        agent.confirm(answer in ("y", "yes"))

                    case EventType.TASK_UPDATE:
                        for task in event["tasks"]:
                            tid = task["id"]
                            old = known_tasks.get(tid)
                            steps = task.get("steps", [])

                            if old is None:
                                goal = task["goal"]
                                if len(goal) > 100:
                                    goal = goal[:100] + "…"
                                console.print(
                                    Text(
                                        f"{_INDENT}◆ {goal}",
                                        style="yellow",
                                    )
                                )
                            else:
                                old_steps = old.get("steps", [])
                                for i, step in enumerate(steps):
                                    old_s = (
                                        old_steps[i]["status"]
                                        if i < len(old_steps)
                                        else None
                                    )
                                    if step["status"] == old_s:
                                        continue
                                    if step["status"] == "completed":
                                        desc = step["description"]
                                        if len(desc) > 100:
                                            desc = desc[:100] + "…"
                                        console.print(
                                            Text(
                                                f"{_INDENT}✓ {desc}",
                                                style="green",
                                            )
                                        )

                            known_tasks[tid] = task

                    case EventType.SUB_AGENT_START:
                        aid = event["agent_id"]
                        sub_counter += 1
                        label = f"#{sub_counter}"
                        sub_agents[aid] = {
                            "role": event["role"],
                            "label": label,
                        }
                        task_preview = event["task"][:100]
                        if len(event["task"]) > 100:
                            task_preview += "…"
                        console.print(
                            Text(
                                f"{_INDENT}▸ {label} {event['role']}:"
                                f" {task_preview}",
                                style="magenta",
                            )
                        )

                    case EventType.SUB_AGENT_UPDATE:
                        aid = event["agent_id"]
                        sa = sub_agents.get(aid, {})
                        label = sa.get("label", "?")
                        inner = event["event"]
                        if inner["type"] == EventType.TOOL_CALL:
                            args_str = _format_args(inner["args"])
                            _dim(
                                f"{_INDENT2}● {label}"
                                f" {inner['name']}({args_str})"
                            )

                    case EventType.SUB_AGENT_END:
                        aid = event["agent_id"]
                        sa = sub_agents.get(aid, {})
                        label = sa.get("label", "?")
                        console.print(
                            Text(
                                f"{_INDENT}◂ {label}"
                                f" {sa.get('role', '?')}: done",
                                style="magenta",
                            )
                        )

                    case EventType.SYSTEM_MESSAGE:
                        _dim(event["content"])

                    case EventType.ERROR:
                        console.print(
                            Text(
                                f"{_INDENT}✗ {event['content']}",
                                style="bold red",
                            )
                        )

                    case EventType.DONE:
                        _render_assistant(tokens)
                        tokens = ""
                        known_tasks.clear()
        except KeyboardInterrupt:
            conversation.drop_last_incomplete()
            conversation.save()
            console.print()
            console.print(
                Text(f"{_INDENT}Cancelled.", style="dim")
            )

    conversation.save()
    console.print()
    _dim("Conversation saved.")


if __name__ == "__main__":
    main()

from datetime import date
from importlib.resources import files

from tools import TOOLS


def load_prompt(package: str, filename: str) -> str:
    return files(package).joinpath(filename).read_text()


def build_system_prompt() -> str:
    template = load_prompt("prompts", "system.md")
    tool_list = "\n".join(f"- {tool.name}: {tool.description}" for tool in TOOLS)
    return template.format_map({"date": date.today(), "tools": tool_list})

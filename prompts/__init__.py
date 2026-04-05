from datetime import date

from tools import TOOLS
from utils.file import load_prompt


def build_system_prompt() -> str:
    template = load_prompt("prompts", "system.txt")
    tool_list = "\n".join(f"- {tool.name}: {tool.description}" for tool in TOOLS)
    return template.format_map({"date": date.today(), "tools": tool_list})

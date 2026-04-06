from datetime import date
from importlib.resources import files

from config import MEMORY_PATH
from tools import TOOLS


def load_prompt(package: str, filename: str) -> str:
    return files(package).joinpath(filename).read_text()


def load_memory() -> str:
    if not MEMORY_PATH.exists():
        return ""
    content = MEMORY_PATH.read_text().strip()
    if not content:
        return ""
    return f"\n\n## Your memory\n\n{content}"


def build_system_prompt() -> str:
    template = load_prompt("prompts", "system.md")
    tool_list = "\n".join(
        f"- {tool.name}: {tool.description}" for tool in TOOLS
    )
    prompt = template.format_map(
        {"date": date.today(), "tools": tool_list}
    )
    return prompt + load_memory()

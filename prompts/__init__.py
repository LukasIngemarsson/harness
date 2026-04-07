from datetime import date
from importlib.resources import files

from config import MEMORY_PATH
from tools import TOOLS

DEFAULT_PROFILE = "default"


def load_prompt(package: str, filename: str) -> str:
    return files(package).joinpath(filename).read_text()


def load_memory() -> str:
    if not MEMORY_PATH.exists():
        return ""
    content = MEMORY_PATH.read_text().strip()
    if not content:
        return ""
    return f"\n\n## Your memory\n\n{content}"


def list_profiles() -> list[str]:
    profiles_dir = files("prompts").joinpath("profiles")
    return sorted(
        p.name.removesuffix(".md")
        for p in profiles_dir.iterdir()
        if p.name.endswith(".md")
    )


def load_profile(name: str) -> str:
    try:
        return load_prompt("prompts.profiles", f"{name}.md")
    except FileNotFoundError:
        return ""


def build_system_prompt(profile: str = DEFAULT_PROFILE) -> str:
    template = load_prompt("prompts", "system.md")
    tool_list = "\n".join(
        f"- {tool.name}: {tool.description}" for tool in TOOLS
    )
    profile_content = load_profile(profile)
    prompt = template.format_map(
        {
            "date": date.today(),
            "tools": tool_list,
            "profile": profile_content,
        }
    )
    return prompt + load_memory()

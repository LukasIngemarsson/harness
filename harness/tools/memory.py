from harness.config import MEMORY_PATH
from harness.tools.base import Tool, ToolResult


class SaveMemoryTool(Tool):
    name = "save_memory"
    description = (
        "Save important information to persistent memory."
        " This survives across conversations and clears."
        " Use for: user preferences, key facts, project"
        " context, or anything worth remembering."
        " Content is appended to memory."
    )
    parameters = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The information to remember",
            },
        },
        "required": ["content"],
    }

    def execute(self, content: str, **kwargs: object) -> ToolResult:
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing = MEMORY_PATH.read_text() if MEMORY_PATH.exists() else ""
        separator = "\n" if existing.strip() else ""
        MEMORY_PATH.write_text(existing + separator + content + "\n")
        return ToolResult(text="Saved to memory.")


class ReadMemoryTool(Tool):
    name = "read_memory"
    description = (
        "Read your persistent memory. Use this to"
        " recall what you have saved from previous"
        " conversations."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def execute(self, **kwargs: object) -> ToolResult:
        if not MEMORY_PATH.exists():
            return ToolResult(text="Memory is empty.")
        content = MEMORY_PATH.read_text().strip()
        return ToolResult(text=content if content else "Memory is empty.")

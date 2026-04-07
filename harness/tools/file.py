from harness.config import WORKSPACE_DIR
from harness.tools.base import Tool


class FileReadTool(Tool):
    name = "read_file"
    description = (
        "Read a file. Use the filename directly"
        " (e.g. 'notes.txt')."
        " Do NOT include '.workspace/' in the path."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The file path to read",
            },
        },
        "required": ["path"],
    }

    def execute(self, path: str, **kwargs: object) -> str:
        target = (WORKSPACE_DIR / path).resolve()
        if not str(target).startswith(
            str(WORKSPACE_DIR.resolve())
        ):
            return "Error: access denied — path is outside workspace"
        if not target.exists():
            return f"Error: file not found: {path}"
        if not target.is_file():
            return f"Error: not a file: {path}"
        return target.read_text()


class FileWriteTool(Tool):
    name = "write_file"
    description = (
        "Write content to a file. Use the filename"
        " directly (e.g. 'notes.txt')."
        " Do NOT include '.workspace/' in the path."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The file path to write to",
            },
            "content": {
                "type": "string",
                "description": "The content to write",
            },
        },
        "required": ["path", "content"],
    }

    def execute(
        self, path: str, content: str, **kwargs: object
    ) -> str:
        target = (WORKSPACE_DIR / path).resolve()
        if not str(target).startswith(
            str(WORKSPACE_DIR.resolve())
        ):
            return "Error: access denied — path is outside workspace"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {path}"

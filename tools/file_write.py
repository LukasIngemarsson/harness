
from tools.base import WORKSPACE_DIR, Tool


class FileWriteTool(Tool):
    name = "write_file"
    description = (
        "Write content to a file in the workspace."
        " Path is relative to the .workspace/ directory."
        " Creates parent directories if they don't exist."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The file path to write to"},
            "content": {"type": "string", "description": "The content to write"},
        },
        "required": ["path", "content"],
    }

    def execute(self, path: str, content: str, **kwargs: object) -> str:
        target = (WORKSPACE_DIR / path).resolve()
        if not str(target).startswith(str(WORKSPACE_DIR.resolve())):
            return "Error: access denied — path is outside workspace"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {path}"

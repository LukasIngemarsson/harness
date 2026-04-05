
from tools.base import WORKSPACE_DIR, Tool


class FileReadTool(Tool):
    name = "read_file"
    description = "Reads and returns the contents of a file at the given path."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The file path to read"},
        },
        "required": ["path"],
    }

    def execute(self, path: str, **kwargs: object) -> str:
        target = (WORKSPACE_DIR / path).resolve()
        if not str(target).startswith(str(WORKSPACE_DIR.resolve())):
            return "Error: access denied — path is outside workspace"
        if not target.exists():
            return f"Error: file not found: {path}"
        if not target.is_file():
            return f"Error: not a file: {path}"
        return target.read_text()

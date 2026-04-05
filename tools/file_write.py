from pathlib import Path

from tools.base import Tool


class FileWriteTool(Tool):
    name = "write_file"
    description = (
        "Writes content to a file at the given path."
        " Creates the file if it doesn't exist."
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
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {path}"

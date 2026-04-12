from datetime import datetime

from harness.tools.base import Tool, ToolResult


class TimeTool(Tool):
    name = "get_current_time"
    description = "Get the current date and time. Returns YYYY-MM-DD HH:MM:SS format."
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs: object) -> ToolResult:
        return ToolResult(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

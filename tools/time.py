from datetime import datetime

from tools.base import Tool


class TimeTool(Tool):
    name = "get_current_time"
    description = "Get the current date and time. Returns YYYY-MM-DD HH:MM:SS format."
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs: object) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

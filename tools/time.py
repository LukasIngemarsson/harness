from datetime import datetime
from tools.base import Tool


class TimeTool(Tool):
    name = "get_current_time"
    description = "Returns the current date and time."
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

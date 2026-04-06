from memory.task import get_task_store
from tools.base import Tool
from utils.enums import Status


class ListTasksTool(Tool):
    name = "list_tasks"
    description = (
        "List all tasks and their current status."
        " Use this to check progress or remind"
        " yourself what you are working on."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def execute(self, **kwargs: object) -> str:
        tasks = get_task_store().list_all()
        if not tasks:
            return "No tasks."

        lines = []
        for task in tasks:
            lines.append(f"[{task.status}] {task.goal} ({task.id})")
            for i, step in enumerate(task.steps):
                marker = (
                    "x" if step.status == Status.COMPLETED else " "
                )
                lines.append(f"  [{marker}] {i}. {step.description}")
                if step.result:
                    lines.append(f"      -> {step.result}")
        return "\n".join(lines)

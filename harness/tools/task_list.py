from harness.enums import Status
from harness.memory.task import get_task_store
from harness.tools.base import Tool, ToolResult


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

    def execute(self, **kwargs: object) -> ToolResult:
        tasks = get_task_store().list_all()
        if not tasks:
            return ToolResult(text="No tasks.")

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
        return ToolResult(text="\n".join(lines))

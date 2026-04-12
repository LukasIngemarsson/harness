from harness.memory.task import get_task_store
from harness.tools.base import Tool, ToolResult


class PlanTaskTool(Tool):
    name = "plan_task"
    description = (
        "Create a task with a goal and a list of steps."
        " Use this for complex multi-step requests."
        " Returns the task ID. Steps should be concrete"
        " and actionable."
    )
    parameters = {
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "description": "What the user wants done",
            },
            "steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of concrete steps to achieve the goal",
            },
        },
        "required": ["goal", "steps"],
    }

    def execute(self, goal: str, steps: list[str], **kwargs: object) -> ToolResult:
        task = get_task_store().create(goal, steps)
        step_list = "\n".join(
            f"  {i}. {s}" for i, s in enumerate(steps)
        )
        return ToolResult(
            text=f"Task created. task_id={task.id}\n"
            f"Steps (use step_index when calling update_task):\n"
            f"{step_list}"
        )

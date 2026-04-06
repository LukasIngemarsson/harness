from memory.task import get_task_store
from tools.base import Tool


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

    def execute(self, goal: str, steps: list, **kwargs: object) -> str:
        task = get_task_store().create(goal, steps)
        step_list = "\n".join(
            f"  {i}. {s}" for i, s in enumerate(steps)
        )
        return (
            f"Task created. task_id={task.id}\n"
            f"Steps (use step_index when calling update_task):\n"
            f"{step_list}"
        )

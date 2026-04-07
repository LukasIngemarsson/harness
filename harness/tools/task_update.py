from harness.memory.task import get_task_store
from harness.tools.base import Tool
from harness.utils.enums import Status


class UpdateTaskTool(Tool):
    name = "update_task"
    _valid = ", ".join(s.value for s in Status if s != Status.PENDING)
    description = (
        "Update a task step's status. Call this after"
        " completing or starting each step."
        f" Valid statuses: {_valid}."
    )
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The task ID",
            },
            "step_index": {
                "type": "integer",
                "description": "The step number (0-based)",
            },
            "status": {
                "type": "string",
                "enum": [s.value for s in Status if s != Status.PENDING],
                "description": "New status for the step",
            },
            "result": {
                "type": "string",
                "description": "What happened (optional)",
            },
        },
        "required": ["task_id", "step_index", "status"],
    }

    def execute(
        self,
        task_id: str,
        step_index: int,
        status: str,
        result: str = "",
        **kwargs: object,
    ) -> str:
        task = get_task_store().update_step(
            task_id, int(step_index), status, result or None
        )
        if not task:
            return f"Error: task '{task_id}' or step {step_index} not found"
        step = task.steps[int(step_index)]
        return (
            f"Step {step_index} ({step.description}):"
            f" {step.status}. Task: {task.status}"
        )

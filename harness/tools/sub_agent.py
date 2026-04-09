from harness.tools.base import Tool


class SubAgentTool(Tool):
    name = "spawn_agent"
    description = (
        "Spawn a sub-agent with a specific role to"
        " handle a subtask. The sub-agent has its own"
        " conversation context and access to all tools."
        " Returns the sub-agent's final response."
    )
    parameters = {
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "description": (
                    "The sub-agent's role/expertise,"
                    " e.g. 'researcher', 'code reviewer',"
                    " 'technical writer'"
                ),
            },
            "task": {
                "type": "string",
                "description": "The task for the sub-agent",
            },
            "reflect": {
                "type": "boolean",
                "description": (
                    "If true, the sub-agent reviews and"
                    " improves its output before returning."
                    " Use for research or writing tasks"
                    " where quality matters."
                ),
            },
        },
        "required": ["role", "task"],
    }

    def execute(
        self, role: str, task: str, **kwargs: object
    ) -> str:
        # Execution is handled by Agent._execute_single_tool()
        # which calls Agent.spawn() directly. This tool class
        # only exists for the API definition.
        return "Error: spawn_agent must be called via Agent"

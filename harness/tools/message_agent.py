from harness.tools.base import Tool


class MessageAgentTool(Tool):
    name = "message_agent"
    description = (
        "Send a follow-up message to an existing sub-agent."
        " Use this to review a sub-agent's work and ask"
        " for revisions, clarifications, or additional"
        " work. The sub-agent retains its full conversation"
        " context from the original task."
    )
    parameters = {
        "type": "object",
        "properties": {
            "agent_id": {
                "type": "string",
                "description": (
                    "The ID of the sub-agent to message"
                    " (returned by spawn_agent)"
                ),
            },
            "message": {
                "type": "string",
                "description": (
                    "The follow-up message, e.g. feedback,"
                    " revision request, or additional task"
                ),
            },
        },
        "required": ["agent_id", "message"],
    }

    def execute(
        self, agent_id: str, message: str, **kwargs: object
    ) -> str:
        return "Error: message_agent must be called via Agent"

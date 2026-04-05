class Conversation:
    def __init__(self, system_prompt: str) -> None:
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, message: str) -> None:
        self.messages.append(message)

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": content}
        )

    def get_messages(self) -> list:
        return self.messages

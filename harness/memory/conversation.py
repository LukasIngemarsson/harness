import json
from pathlib import Path

from harness.config import HISTORY_PATH
from harness.utils.enums import Role


class Conversation:
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self._messages = [{"role": Role.SYSTEM, "content": system_prompt}]

    @property
    def messages(self) -> list:
        return self._messages

    def add_user_message(self, content: str) -> None:
        self._messages.append({"role": Role.USER, "content": content})

    def add_assistant_message(self, message: str) -> None:
        self._messages.append(message)

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self._messages.append(
            {"role": Role.TOOL, "tool_call_id": tool_call_id, "content": content}
        )

    @staticmethod
    def clear_history(path: Path = HISTORY_PATH) -> None:
        if path.exists():
            path.unlink()

    def save(self, path: Path = HISTORY_PATH) -> None:
        path.write_text(json.dumps(self._messages, indent=2))

    @classmethod
    def load(cls, system_prompt: str, path: Path = HISTORY_PATH) -> "Conversation":
        if not path.exists():
            return cls(system_prompt)
        conv = cls(system_prompt)
        conv._messages = json.loads(path.read_text())
        return conv

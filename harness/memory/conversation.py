import json
import logging
from pathlib import Path

from harness.config import HISTORY_PATH
from harness.utils.enums import Role

logger = logging.getLogger(__name__)

CHARS_PER_TOKEN = 4
RECENT_MESSAGES_TO_KEEP = 10


def estimate_tokens(messages: list[dict]) -> int:
    total_chars = sum(
        len(json.dumps(msg)) for msg in messages
    )
    return total_chars // CHARS_PER_TOKEN


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

    def needs_compaction(self, max_tokens: int) -> bool:
        token_count = estimate_tokens(self._messages)
        threshold = int(max_tokens * 0.75)
        min_messages = RECENT_MESSAGES_TO_KEEP + 2
        return (
            token_count > threshold
            and len(self._messages) > min_messages
        )

    def can_compact(self) -> bool:
        return len(self._messages) > RECENT_MESSAGES_TO_KEEP + 1

    def get_messages_to_compact(self) -> list[dict]:
        if not self.can_compact():
            return []
        cut = len(self._messages) - RECENT_MESSAGES_TO_KEEP
        return self._messages[1:cut]

    def apply_compaction(self, summary: str) -> None:
        cut = len(self._messages) - RECENT_MESSAGES_TO_KEEP
        recent = self._messages[cut:]
        self._messages = [
            self._messages[0],
            {
                "role": Role.SYSTEM,
                "content": (
                    "Summary of earlier conversation:\n\n"
                    + summary
                ),
            },
            *recent,
        ]
        logger.info(
            "Conversation compacted. Messages: %d, tokens: ~%d",
            len(self._messages),
            estimate_tokens(self._messages),
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

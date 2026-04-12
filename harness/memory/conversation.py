import json
import logging
from pathlib import Path

from harness.config import HISTORY_PATH
from harness.enums import Role
from harness.tools.base import ToolResult

logger = logging.getLogger(__name__)

_CHARS_PER_TOKEN = 4
RECENT_MESSAGES_TO_KEEP = 10


def estimate_tokens(messages: list[dict]) -> int:
    total_chars = sum(
        len(json.dumps(msg)) for msg in messages
    )
    return total_chars // _CHARS_PER_TOKEN


class Conversation:
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self._messages = [{"role": Role.SYSTEM, "content": system_prompt}]

    @property
    def messages(self) -> list[dict]:
        return self._messages

    def add_user_message(self, content: str) -> None:
        self._messages.append({"role": Role.USER, "content": content})

    def add_assistant_message(self, message: str) -> None:
        self._messages.append(message)

    def add_tool_result(
        self, tool_call_id: str, result: ToolResult
    ) -> None:
        if result.image_base64:
            content: str | list = [
                {"type": "text", "text": result.text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:{result.media_type}"
                            f";base64,{result.image_base64}"
                        ),
                    },
                },
            ]
        else:
            content = result.text

        self._messages.append(
            {
                "role": Role.TOOL,
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

    def drop_last_incomplete(self) -> None:
        while self._messages and self._messages[-1].get("role") in (
            Role.ASSISTANT,
            Role.TOOL,
        ):
            self._messages.pop()

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
    def _format_tokens(n: int) -> str:
        if n >= 1000:
            return f"~{n / 1000:.1f}k"
        return f"~{round(n, -2)}" if n >= 100 else f"~{n}"

    def context_info(self) -> str:
        total_tokens = estimate_tokens(self._messages)
        counts: dict[str, int] = {}
        has_summary = False

        for msg in self._messages:
            role = msg.get("role", "unknown")
            counts[role] = counts.get(role, 0) + 1
            if (
                role == Role.SYSTEM
                and "Summary of earlier conversation"
                in msg.get("content", "")
            ):
                has_summary = True

        lines = [
            f"Messages: {len(self._messages)}",
            f"Tokens: {self._format_tokens(total_tokens)}",
            "",
            "Breakdown:",
        ]
        for role, count in sorted(counts.items()):
            lines.append(f"  {role}: {count}")

        if has_summary:
            # Find the summary and show a preview
            for msg in self._messages:
                content = msg.get("content", "")
                if "Summary of earlier conversation" in content:
                    summary_text = content.replace(
                        "Summary of earlier conversation:\n\n",
                        "",
                    )
                    preview = summary_text[:300]
                    if len(summary_text) > 300:
                        preview += "..."
                    lines.append("")
                    lines.append("Compaction summary:")
                    lines.append(preview)
                    break
        else:
            lines.append("")
            lines.append("No compaction applied.")

        return "\n".join(lines)

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
        conv._repair_incomplete()
        return conv

    def _repair_incomplete(self) -> None:
        tool_result_ids = {
            m.get("tool_call_id")
            for m in self._messages
            if m.get("role") == Role.TOOL
        }
        cleaned = []
        skip_until_user = False
        for msg in self._messages:
            role = msg.get("role")
            if skip_until_user:
                if role == Role.USER:
                    skip_until_user = False
                    cleaned.append(msg)
                continue
            if role == Role.ASSISTANT and msg.get("tool_calls"):
                if any(
                    tc["id"] not in tool_result_ids
                    for tc in msg["tool_calls"]
                ):
                    skip_until_user = True
                    continue
            cleaned.append(msg)
        if len(cleaned) != len(self._messages):
            self._messages = cleaned
            self.save()

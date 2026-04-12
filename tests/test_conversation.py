from harness.memory.conversation import (
    RECENT_MESSAGES_TO_KEEP,
    Conversation,
)


class TestCompaction:
    def _build_long_conversation(self, n_messages: int) -> Conversation:
        conv = Conversation("You are a helpful assistant.")
        for i in range(n_messages):
            conv.add_user_message(f"Message {i}: " + "x" * 100)
            conv.add_assistant_message(
                {"role": "assistant", "content": f"Reply {i}: " + "y" * 100}
            )
        return conv

    def test_short_conversation_does_not_need_compaction(self):
        conv = Conversation("system prompt")
        conv.add_user_message("hello")
        conv.add_assistant_message(
            {"role": "assistant", "content": "hi"}
        )
        assert not conv.needs_compaction(128_000)

    def test_long_conversation_needs_compaction(self):
        conv = self._build_long_conversation(100)
        assert conv.needs_compaction(500)

    def test_can_compact_short_conversation(self):
        conv = Conversation("system prompt")
        conv.add_user_message("hello")
        assert not conv.can_compact()

    def test_can_compact_long_conversation(self):
        conv = self._build_long_conversation(20)
        assert conv.can_compact()

    def test_get_messages_to_compact_preserves_recent(self):
        conv = self._build_long_conversation(20)
        old = conv.get_messages_to_compact()
        total = len(conv.messages)
        assert len(old) == total - 1 - RECENT_MESSAGES_TO_KEEP

    def test_apply_compaction_keeps_structure(self):
        conv = self._build_long_conversation(20)
        original_recent = conv.messages[-RECENT_MESSAGES_TO_KEEP:]
        conv.apply_compaction("This is a summary of the conversation.")

        assert conv.messages[0]["role"] == "system"
        assert "helpful assistant" in conv.messages[0]["content"]
        assert conv.messages[1]["role"] == "system"
        assert "Summary" in conv.messages[1]["content"]
        assert conv.messages[2:] == original_recent

    def test_apply_compaction_reduces_message_count(self):
        conv = self._build_long_conversation(20)
        original_count = len(conv.messages)
        conv.apply_compaction("Summary.")
        assert len(conv.messages) == 2 + RECENT_MESSAGES_TO_KEEP
        assert len(conv.messages) < original_count

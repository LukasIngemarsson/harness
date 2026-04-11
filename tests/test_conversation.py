from harness.memory.conversation import (
    RECENT_MESSAGES_TO_KEEP,
    Conversation,
    estimate_tokens,
)


class TestEstimateTokens:
    def test_empty_messages(self):
        assert estimate_tokens([]) == 0

    def test_basic_estimate(self):
        msgs = [{"role": "user", "content": "a" * 400}]
        tokens = estimate_tokens(msgs)
        assert tokens > 0


class TestSummarization:
    def _build_long_conversation(self, n_messages: int) -> Conversation:
        conv = Conversation("You are a helpful assistant.")
        for i in range(n_messages):
            conv.add_user_message(f"Message {i}: " + "x" * 100)
            conv.add_assistant_message(
                {"role": "assistant", "content": f"Reply {i}: " + "y" * 100}
            )
        return conv

    def test_short_conversation_does_not_need_summarization(self):
        conv = Conversation("system prompt")
        conv.add_user_message("hello")
        conv.add_assistant_message(
            {"role": "assistant", "content": "hi"}
        )
        assert not conv.needs_summarization(128_000)

    def test_long_conversation_needs_summarization(self):
        conv = self._build_long_conversation(100)
        # With a very small token limit, it should trigger
        assert conv.needs_summarization(500)

    def test_get_messages_to_summarize_preserves_recent(self):
        conv = self._build_long_conversation(20)
        old = conv.get_messages_to_summarize()
        total = len(conv.messages)
        # Should leave system prompt + RECENT_MESSAGES_TO_KEEP
        assert len(old) == total - 1 - RECENT_MESSAGES_TO_KEEP

    def test_apply_summary_keeps_structure(self):
        conv = self._build_long_conversation(20)
        original_recent = conv.messages[-RECENT_MESSAGES_TO_KEEP:]
        conv.apply_summary("This is a summary of the conversation.")

        # System prompt is first
        assert conv.messages[0]["role"] == "system"
        assert "helpful assistant" in conv.messages[0]["content"]

        # Summary is second
        assert conv.messages[1]["role"] == "system"
        assert "Summary" in conv.messages[1]["content"]

        # Recent messages preserved
        assert conv.messages[2:] == original_recent

    def test_apply_summary_reduces_message_count(self):
        conv = self._build_long_conversation(20)
        original_count = len(conv.messages)
        conv.apply_summary("Summary.")
        # Should be: system + summary + RECENT_MESSAGES_TO_KEEP
        assert len(conv.messages) == 2 + RECENT_MESSAGES_TO_KEEP
        assert len(conv.messages) < original_count

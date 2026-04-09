from unittest.mock import MagicMock, patch

from harness.agent import Agent, TOOL_MAP


class TestToolCache:
    def setup_method(self):
        self.agent = Agent.__new__(Agent)
        self.agent._tool_cache = {}

    def test_cacheable_tool_returns_cached_result(self):
        mock_tool = MagicMock()
        mock_tool.cacheable = True
        mock_tool.execute.return_value = "search results"

        with patch.dict(TOOL_MAP, {"web_search": mock_tool}):
            result1 = self.agent._execute_single_tool(
                "web_search", {"query": "test"}
            )
            result2 = self.agent._execute_single_tool(
                "web_search", {"query": "test"}
            )

        assert result1 == "search results"
        assert result2 == "search results"
        assert mock_tool.execute.call_count == 1

    def test_non_cacheable_tool_always_executes(self):
        mock_tool = MagicMock()
        mock_tool.cacheable = False
        mock_tool.execute.return_value = "result"

        with patch.dict(TOOL_MAP, {"run_shell": mock_tool}):
            self.agent._execute_single_tool(
                "run_shell", {"command": "ls"}
            )
            self.agent._execute_single_tool(
                "run_shell", {"command": "ls"}
            )

        assert mock_tool.execute.call_count == 2

    def test_different_args_not_cached(self):
        mock_tool = MagicMock()
        mock_tool.cacheable = True
        mock_tool.execute.side_effect = ["result A", "result B"]

        with patch.dict(TOOL_MAP, {"web_search": mock_tool}):
            r1 = self.agent._execute_single_tool(
                "web_search", {"query": "foo"}
            )
            r2 = self.agent._execute_single_tool(
                "web_search", {"query": "bar"}
            )

        assert r1 == "result A"
        assert r2 == "result B"
        assert mock_tool.execute.call_count == 2

    def test_error_result_not_cached(self):
        mock_tool = MagicMock()
        mock_tool.cacheable = True
        mock_tool.execute.side_effect = [
            "Error: timeout",
            "Error: timeout",
            "actual result",
        ]

        with patch.dict(TOOL_MAP, {"web_search": mock_tool}):
            r1 = self.agent._execute_single_tool(
                "web_search", {"query": "test"}
            )
            r2 = self.agent._execute_single_tool(
                "web_search", {"query": "test"}
            )

        # First call retries and eventually fails
        assert r1 == "Error: timeout"
        # Second call should execute again (not cached)
        assert r2 == "actual result"


class TestToolRetry:
    def setup_method(self):
        self.agent = Agent.__new__(Agent)
        self.agent._tool_cache = {}

    @patch("harness.agent.time.sleep")
    def test_retries_on_error_result(self, mock_sleep):
        mock_tool = MagicMock()
        mock_tool.cacheable = False
        mock_tool.execute.side_effect = [
            "Error: connection timeout",
            "success",
        ]

        with patch.dict(TOOL_MAP, {"read_url": mock_tool}):
            result = self.agent._execute_single_tool(
                "read_url", {"url": "http://example.com"}
            )

        assert result == "success"
        assert mock_tool.execute.call_count == 2
        mock_sleep.assert_called_once()

    @patch("harness.agent.time.sleep")
    def test_retries_on_exception(self, mock_sleep):
        mock_tool = MagicMock()
        mock_tool.cacheable = False
        mock_tool.execute.side_effect = [
            ConnectionError("timeout"),
            "success",
        ]

        with patch.dict(TOOL_MAP, {"read_url": mock_tool}):
            result = self.agent._execute_single_tool(
                "read_url", {"url": "http://example.com"}
            )

        assert result == "success"
        assert mock_tool.execute.call_count == 2

    @patch("harness.agent.time.sleep")
    def test_returns_last_error_after_max_retries(self, mock_sleep):
        mock_tool = MagicMock()
        mock_tool.cacheable = False
        mock_tool.execute.return_value = "Error: server down"

        with patch.dict(TOOL_MAP, {"read_url": mock_tool}):
            result = self.agent._execute_single_tool(
                "read_url", {"url": "http://example.com"}
            )

        assert result == "Error: server down"
        assert mock_tool.execute.call_count == 2

    def test_no_retry_on_type_error(self):
        mock_tool = MagicMock()
        mock_tool.cacheable = False
        mock_tool.execute.side_effect = TypeError("bad args")

        with patch.dict(TOOL_MAP, {"read_url": mock_tool}):
            result = self.agent._execute_single_tool(
                "read_url", {"url": "http://example.com"}
            )

        assert "Error:" in result
        assert mock_tool.execute.call_count == 1

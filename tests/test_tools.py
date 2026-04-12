import pytest

from harness.config import WORKSPACE_DIR
from harness.tools import TOOLS
from harness.tools.base import ToolError
from harness.tools.calculator import CalculatorTool
from harness.tools.file import FileReadTool, FileWriteTool
from harness.tools.shell import ShellTool


class TestCalculatorTool:
    def setup_method(self):
        self.calc = CalculatorTool()

    def test_string_args_rejected(self):
        with pytest.raises(ToolError):
            self.calc.execute(a="hello", b=2, operation="add")

    def test_divide_by_zero(self):
        with pytest.raises(ToolError, match="division by zero"):
            self.calc.execute(a=5, b=0, operation="divide")

    def test_unknown_operation(self):
        with pytest.raises(ToolError, match="unknown operation"):
            self.calc.execute(a=1, b=1, operation="power")


class TestFileReadTool:
    def setup_method(self):
        self.reader = FileReadTool()

    def test_read_existing_file(self):
        f = WORKSPACE_DIR / "_test_read.txt"
        f.write_text("hello")
        assert self.reader.execute(path="_test_read.txt").text == "hello"
        f.unlink()

    def test_path_traversal_blocked(self):
        with pytest.raises(ToolError, match="access denied"):
            self.reader.execute(path="../../config.py")


class TestFileWriteTool:
    def setup_method(self):
        self.writer = FileWriteTool()

    def test_write_and_read_back(self):
        result = self.writer.execute(path="_test_write.txt", content="hello")
        assert "Successfully" in result.text
        f = WORKSPACE_DIR / "_test_write.txt"
        assert f.read_text() == "hello"
        f.unlink()

    def test_path_traversal_blocked(self):
        with pytest.raises(ToolError, match="access denied"):
            self.writer.execute(path="../../evil.txt", content="bad")


class TestShellTool:
    def setup_method(self):
        self.shell = ShellTool()

    def test_blocked_command(self):
        with pytest.raises(ToolError, match="not allowed"):
            self.shell.execute(command="curl http://example.com")


def test_tool_api_format():
    for tool in TOOLS:
        fmt = tool.to_api_format()
        assert fmt["type"] == "function"
        assert "name" in fmt["function"]
        assert "parameters" in fmt["function"]

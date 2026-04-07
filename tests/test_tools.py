from harness.config import WORKSPACE_DIR
from harness.tools import TOOLS
from harness.tools.calculator import CalculatorTool
from harness.tools.file import FileReadTool, FileWriteTool
from harness.tools.shell import ShellTool


class TestCalculatorTool:
    def setup_method(self):
        self.calc = CalculatorTool()

    def test_add(self):
        assert self.calc.execute(a=2, b=3, operation="add") == "5.0"

    def test_subtract(self):
        assert self.calc.execute(a=10, b=4, operation="subtract") == "6.0"

    def test_multiply(self):
        assert self.calc.execute(a=3, b=7, operation="multiply") == "21.0"

    def test_string_args_rejected(self):
        assert "Error" in self.calc.execute(a="hello", b=2, operation="add")

    def test_divide(self):
        assert self.calc.execute(a=10, b=4, operation="divide") == "2.5"

    def test_divide_by_zero(self):
        assert (
            self.calc.execute(a=5, b=0, operation="divide")
            == "Error: division by zero"
        )

    def test_unknown_operation(self):
        assert self.calc.execute(a=1, b=1, operation="power") == "Unknown operation"


class TestFileReadTool:
    def setup_method(self):
        self.reader = FileReadTool()

    def test_read_existing_file(self):
        f = WORKSPACE_DIR / "_test_read.txt"
        f.write_text("hello")
        assert self.reader.execute(path="_test_read.txt") == "hello"
        f.unlink()

    def test_read_missing_file(self):
        assert "Error: file not found" in self.reader.execute(
            path="_nonexistent.txt"
        )

    def test_path_traversal_blocked(self):
        assert "access denied" in self.reader.execute(path="../../config.py")


class TestFileWriteTool:
    def setup_method(self):
        self.writer = FileWriteTool()

    def test_write_new_file(self):
        result = self.writer.execute(path="_test_write.txt", content="hello")
        assert "Successfully" in result
        f = WORKSPACE_DIR / "_test_write.txt"
        assert f.read_text() == "hello"
        f.unlink()

    def test_write_creates_parents(self):
        self.writer.execute(path="_test_dir/nested.txt", content="nested")
        f = WORKSPACE_DIR / "_test_dir" / "nested.txt"
        assert f.read_text() == "nested"
        f.unlink()
        (WORKSPACE_DIR / "_test_dir").rmdir()

    def test_path_traversal_blocked(self):
        assert "access denied" in self.writer.execute(
            path="../../evil.txt", content="bad"
        )


class TestShellTool:
    def setup_method(self):
        self.shell = ShellTool()

    def test_allowed_command(self):
        result = self.shell.execute(command="echo hello")
        assert "hello" in result

    def test_blocked_command(self):
        result = self.shell.execute(command="rm -rf /")
        assert "not allowed" in result

    def test_timeout(self):
        result = self.shell.execute(command="echo fast")
        assert "fast" in result


def test_tool_api_format():
    for tool in TOOLS:
        fmt = tool.to_api_format()
        assert fmt["type"] == "function"
        assert "name" in fmt["function"]
        assert "parameters" in fmt["function"]

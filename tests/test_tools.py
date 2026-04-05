from tools.calculator import CalculatorTool
from tools.time import TimeTool


class TestCalculatorTool:
    def setup_method(self):
        self.calc = CalculatorTool()

    def test_add(self):
        assert self.calc.execute(a=2, b=3, operation="add") == "5"

    def test_subtract(self):
        assert self.calc.execute(a=10, b=4, operation="subtract") == "6"

    def test_multiply(self):
        assert self.calc.execute(a=3, b=7, operation="multiply") == "21"

    def test_divide(self):
        assert self.calc.execute(a=10, b=4, operation="divide") == "2.5"

    def test_divide_by_zero(self):
        assert (
            self.calc.execute(a=5, b=0, operation="divide") == "Error: division by zero"
        )

    def test_unknown_operation(self):
        assert self.calc.execute(a=1, b=1, operation="power") == "Unknown operation"


def test_tool_api_format():
    for tool in [CalculatorTool(), TimeTool()]:
        fmt = tool.to_api_format()
        assert fmt["type"] == "function"
        assert "name" in fmt["function"]
        assert "parameters" in fmt["function"]

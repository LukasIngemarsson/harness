from harness.tools.base import Tool, ToolError


class CalculatorTool(Tool):
    name = "calculate"
    description = (
        "Basic arithmetic on two numbers"
        " (add, subtract, multiply, divide)."
        " For complex math use python_eval."
    )
    parameters = {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "The operation to perform",
            },
        },
        "required": ["a", "b", "operation"],
    }

    def execute(self, a: float, b: float, operation: str) -> str:
        try:
            a, b = float(a), float(b)
        except (TypeError, ValueError):
            raise ToolError("a and b must be numbers")
        match operation:
            case "add":
                return str(a + b)
            case "subtract":
                return str(a - b)
            case "multiply":
                return str(a * b)
            case "divide":
                if b == 0:
                    raise ToolError("division by zero")
                return str(a / b)
        raise ToolError(f"unknown operation: {operation}")

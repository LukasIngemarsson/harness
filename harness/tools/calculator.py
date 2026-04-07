from harness.tools.base import Tool


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
            return "Error: a and b must be numbers"
        match operation:
            case "add":
                return str(a + b)
            case "subtract":
                return str(a - b)
            case "multiply":
                return str(a * b)
            case "divide":
                return str(a / b) if b != 0 else "Error: division by zero"
        return "Unknown operation"

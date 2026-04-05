import shlex
import subprocess

from tools.base import WORKSPACE_DIR, Tool

TIMEOUT_SECONDS = 30
ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "echo",
    "head",
    "tail",
    "grep",
    "find",
    "wc",
    "sort",
    "pwd",
}


class ShellTool(Tool):
    name = "run_shell"
    description = (
        "Run a shell command in the workspace directory."
        " Only safe commands are allowed: ls, cat, echo, head, tail,"
        " grep, find, wc, sort, pwd."
        " For unrestricted execution, use python_eval instead."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
        },
        "required": ["command"],
    }

    def execute(self, command: str, **kwargs: object) -> str:
        try:
            parts = shlex.split(command)
        except ValueError as e:
            return f"Error: invalid command syntax: {e}"

        base_command = parts[0] if parts else ""
        if base_command not in ALLOWED_COMMANDS:
            return (
                f"Error: '{base_command}' is not allowed. "
                f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
            )

        try:
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=WORKSPACE_DIR,
            )
            output = result.stdout + result.stderr
            return output.strip() if output.strip() else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {TIMEOUT_SECONDS}s"

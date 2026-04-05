import shlex
import subprocess
from pathlib import Path

from tools.base import Tool

TIMEOUT_SECONDS = 30
WORKING_DIR = Path.cwd()
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
    description = "Executes a shell command and returns its output."
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
                cwd=WORKING_DIR,
            )
            output = result.stdout + result.stderr
            return output.strip() if output.strip() else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {TIMEOUT_SECONDS}s"

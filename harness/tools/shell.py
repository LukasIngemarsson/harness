import shlex
import subprocess

from harness.config import WORKSPACE_DIR
from harness.tools.base import Tool, ToolError

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
    "python",
    "python3",
    "rm",
    "rmdir",
    "mv",
    "cp",
    "chmod",
    "mkdir",
    "touch",
}


class ShellTool(Tool):
    name = "run_shell"
    description = (
        "Run a shell command. Allowed: ls, cat,"
        " echo, head, tail, grep, find, wc, sort,"
        " pwd, python, python3, rm, rmdir, mv, cp,"
        " chmod, mkdir, touch."
        " Destructive commands (rm, rmdir, chmod)"
        " require user confirmation."
        " To run Python code, first save it with"
        " write_file, then run: python3 script.py"
        " For quick expressions: python3 -c 'print(1+1)'"
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
            raise ToolError(f"invalid command syntax: {e}")

        base_command = parts[0] if parts else ""
        if base_command not in ALLOWED_COMMANDS:
            raise ToolError(
                f"'{base_command}' is not allowed. "
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
            raise ToolError(
                f"command timed out after {TIMEOUT_SECONDS}s",
                retryable=True,
            )

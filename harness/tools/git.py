import shlex
import subprocess

from harness.config import WORKSPACE_DIR
from harness.tools.base import Tool, ToolError

TIMEOUT_SECONDS = 30
ALLOWED_SUBCOMMANDS = {
    "status",
    "log",
    "diff",
    "show",
    "blame",
    "branch",
    "tag",
    "stash",
    "remote",
    "rev-parse",
}
MAX_OUTPUT_CHARS = 10000


class GitTool(Tool):
    name = "git"
    description = (
        "Run read-only git commands in the workspace."
        " Allowed: status, log, diff, show, blame,"
        " branch, tag, stash, remote, rev-parse."
        " Use this for inspecting repos, reading diffs,"
        " viewing history, and code review."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": (
                    "The git command to run (without the"
                    " 'git' prefix), e.g. 'log --oneline -10'"
                    " or 'diff HEAD~1'"
                ),
            },
        },
        "required": ["command"],
    }

    def execute(self, command: str, **kwargs: object) -> str:
        try:
            parts = shlex.split(command)
        except ValueError as e:
            raise ToolError(f"invalid command syntax: {e}")

        if not parts:
            raise ToolError("empty command")

        subcommand = parts[0]
        if subcommand not in ALLOWED_SUBCOMMANDS:
            raise ToolError(
                f"'{subcommand}' is not allowed. "
                f"Allowed: {', '.join(sorted(ALLOWED_SUBCOMMANDS))}"
            )

        full_cmd = ["git"] + parts
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=WORKSPACE_DIR,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            raise ToolError(
                f"command timed out after {TIMEOUT_SECONDS}s",
                retryable=True,
            )
        except FileNotFoundError:
            raise ToolError("git is not installed")

        output = output.strip() if output.strip() else "(no output)"

        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n\n[truncated]"

        return output

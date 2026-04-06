import io
import logging
import os
from contextlib import redirect_stderr, redirect_stdout

from config import WORKSPACE_DIR
from tools.base import Tool

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30


# NOTE: exec() is unrestricted — the agent can run arbitrary Python code.
# The cwd is set to .workspace/ but this is not a security boundary.
# Only suitable for local, single-user use. Multi-user deployments
# would need proper sandboxing (e.g. Docker, seccomp).
class PythonEvalTool(Tool):
    name = "python_eval"
    description = (
        "Run Python code. You MUST use print()"
        " to see output. You are already in the"
        " workspace directory."
    )
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute",
            },
        },
        "required": ["code"],
    }

    def execute(self, code: str, **kwargs: object) -> str:
        logger.info("Executing Python code:\n%s", code)
        stdout = io.StringIO()
        stderr = io.StringIO()
        original_dir = os.getcwd()
        try:
            os.chdir(WORKSPACE_DIR)
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(code, {"__builtins__": __builtins__})
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"
        finally:
            os.chdir(original_dir)

        output = stdout.getvalue() + stderr.getvalue()
        return output.strip() if output.strip() else "(no output)"

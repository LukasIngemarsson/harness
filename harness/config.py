import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path.cwd() / ".workspace"
HISTORY_PATH = WORKSPACE_DIR / "history.json"
TASKS_PATH = WORKSPACE_DIR / "tasks.json"
MEMORY_PATH = WORKSPACE_DIR / "memory.md"
LOG_DIR = Path.cwd() / ".logs"

WORKSPACE_DIR.mkdir(exist_ok=True)

REQUIRED_VARS = ["MODEL", "BASE_URL", "API_KEY"]


def load_config() -> dict:
    load_dotenv()

    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        logger.critical(
            "Missing required environment variables: %s", ", ".join(missing)
        )
        sys.exit(1)

    ctx = os.getenv("MAX_CONTEXT_TOKENS")

    return {
        "model": os.getenv("MODEL"),
        "base_url": os.getenv("BASE_URL"),
        "api_key": os.getenv("API_KEY"),
        "max_context_tokens": int(ctx) if ctx else 128_000,
    }

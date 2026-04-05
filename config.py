import logging
import os
import sys

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_VARS = ["MODEL", "BASE_URL", "API_KEY"]


def load_config() -> dict:
    load_dotenv()

    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        logger.critical(
            "Missing required environment variables: %s", ", ".join(missing)
        )
        sys.exit(1)

    return {
        "model": os.getenv("MODEL"),
        "base_url": os.getenv("BASE_URL"),
        "api_key": os.getenv("API_KEY"),
    }

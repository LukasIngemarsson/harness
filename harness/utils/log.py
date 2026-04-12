import logging

from harness.config import LOG_DIR

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(filename: str | None = None) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=_LOG_FORMAT,
        filename=str(LOG_DIR / filename) if filename else None,
    )

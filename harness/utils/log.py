import logging

from harness.config import LOG_DIR

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_MAX_LOG_VALUE_LEN = 200


class _OneLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record).replace("\n", " ")
        if len(msg) > _MAX_LOG_VALUE_LEN:
            msg = msg[:_MAX_LOG_VALUE_LEN] + "…"
        return msg


def setup_logging(filename: str | None = None) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    handler = (
        logging.FileHandler(str(LOG_DIR / filename))
        if filename
        else logging.StreamHandler()
    )
    handler.setFormatter(_OneLineFormatter(_LOG_FORMAT))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

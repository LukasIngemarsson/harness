import logging
import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from harness.tools.base import Tool

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/120.0.0.0 Safari/537.36"
)
MAX_CHARS = 10000


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._text: list[str] = []
        self._skip = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._text.append(data)

    def get_text(self) -> str:
        raw = " ".join(self._text)
        return re.sub(r"\s+", " ", raw).strip()


class UrlReadTool(Tool):
    name = "read_url"
    cacheable = True
    description = (
        "Fetch a webpage and return its text content."
        " Give it any URL. Returns readable text,"
        " not HTML. Use this for reading articles,"
        " docs, or any web page."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch",
            },
        },
        "required": ["url"],
    }

    def execute(self, url: str, **kwargs: object) -> str:
        logger.info("Fetching URL: %s", url)
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            return f"Error: failed to fetch URL: {e}"

        extractor = _TextExtractor()
        extractor.feed(html)
        text = extractor.get_text()

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "\n\n[truncated]"

        return text if text else "Error: no readable text found"

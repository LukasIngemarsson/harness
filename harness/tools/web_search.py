import gzip
import json
import logging
import os
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from harness.tools.base import Tool, ToolError, ToolResult

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5
_TIMEOUT = 10


class WebSearchTool(Tool):
    name = "web_search"
    cacheable = True
    description = (
        "Search the web for any query. Returns titles,"
        " snippets, and URLs from search results."
        " Use read_url to get full page content from"
        " any of the returned URLs."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
        },
        "required": ["query"],
    }

    def execute(self, query: str, **kwargs: object) -> ToolResult:
        logger.info("Searching: %s", query)

        api_key = os.getenv("BRAVE_API_KEY", "")

        url = (
            f"https://api.search.brave.com/res/v1/web/search"
            f"?q={quote_plus(query)}"
            f"&count={_MAX_RESULTS}"
        )
        req = Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key,
            },
        )

        try:
            with urlopen(req, timeout=_TIMEOUT) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise ToolError(f"search failed: {e}", retryable=True)

        results = data.get("web", {}).get("results", [])
        if not results:
            return ToolResult(text="No results found.")

        lines = []
        for r in results[:_MAX_RESULTS]:
            title = r.get("title", "")
            snippet = r.get("description", "")
            result_url = r.get("url", "")
            lines.append(title)
            if snippet:
                lines.append(snippet)
            lines.append(f"URL: {result_url}")
            lines.append("")

        return ToolResult(text="\n".join(lines).strip())

"""
NOTE:
This is a lightweight implementation using urlopen to avoid
third-party libraries with internal threading issues (e.g. ddgs).
For more robust querying:
- Brave Search API (free tier, proper REST API)
- SerpAPI / Serper (Google results via API)
- Tavily (purpose-built for AI agents)
- SearXNG (self-hosted metasearch engine)
"""

import logging
import re
from html import unescape
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from harness.tools.base import Tool, ToolError, ToolResult

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5
_TIMEOUT = 10
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/120.0.0.0 Safari/537.36"
)


def _search(query: str) -> list[dict[str, str]]:
    url = "https://html.duckduckgo.com/html/"
    data = urlencode({"q": query}).encode()
    req = Request(
        url,
        data=data,
        headers={
            "User-Agent": _USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urlopen(req, timeout=_TIMEOUT) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    results = []
    seen: set[str] = set()

    # Extract hrefs from result links
    hrefs = re.findall(
        r'<a[^>]*class="result__a"[^>]*'
        r'href="(https?://[^"]+)"',
        html,
    )
    # Try alternate attribute order
    if not hrefs:
        hrefs = re.findall(
            r'<a[^>]*href="(https?://[^"]+)"[^>]*'
            r'class="result__a"',
            html,
        )

    # Extract titles
    titles = re.findall(
        r'<a[^>]*class="result__a"[^>]*>(.*?)</a>',
        html,
        re.DOTALL,
    )

    # Extract snippets
    snippets = re.findall(
        r'class="result__snippet"[^>]*>(.*?)</',
        html,
        re.DOTALL,
    )

    for i, link_url in enumerate(hrefs):
        link_url = unescape(link_url)
        if "duckduckgo.com/y.js" in link_url:
            continue
        if link_url in seen:
            continue
        seen.add(link_url)

        title = ""
        if i < len(titles):
            title = re.sub(
                r"<[^>]+>", "", titles[i]
            ).strip()

        body = ""
        if i < len(snippets):
            body = re.sub(
                r"<[^>]+>", "", snippets[i]
            ).strip()

        results.append(
            {"title": title, "body": body, "url": link_url}
        )

    return results


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
        try:
            results = _search(query)
        except Exception as e:
            raise ToolError(
                f"search failed: {e}", retryable=True
            )

        if not results:
            return ToolResult(text="No results found.")

        lines = []
        for r in results[:_MAX_RESULTS]:
            lines.append(r["title"])
            if r["body"]:
                lines.append(r["body"])
            lines.append(f"URL: {r['url']}")
            lines.append("")

        return ToolResult(text="\n".join(lines).strip())

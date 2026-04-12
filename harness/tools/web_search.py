# NOTE: Uses the ddgs metasearch library (Google backend).
# Intended for personal/educational use only.
import logging

from ddgs import DDGS

from harness.tools.base import Tool, ToolError, ToolResult

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5


class WebSearchTool(Tool):
    name = "web_search"
    cacheable = True
    description = (
        "Search the web for any query. Returns titles,"
        " snippets, and URLs from real search results."
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
            results = DDGS().text(
                query, max_results=_MAX_RESULTS
            )
        except Exception as e:
            raise ToolError(
                f"search failed: {e}", retryable=True
            )

        if not results:
            return ToolResult(text="No results found.")

        lines = []
        for r in results:
            lines.append(r.get("title", ""))
            lines.append(r.get("body", ""))
            lines.append(f"URL: {r.get('href', '')}")
            lines.append("")

        return ToolResult(text="\n".join(lines).strip())

# NOTE: Uses the ddgs metasearch library (Google backend).
# Intended for personal/educational use only.
import logging

from ddgs import DDGS

from harness.tools.base import Tool

logger = logging.getLogger(__name__)

MAX_RESULTS = 5


class WebSearchTool(Tool):
    name = "web_search"
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

    def execute(self, query: str, **kwargs: object) -> str:
        logger.info("Searching: %s", query)
        try:
            results = DDGS().text(
                query, max_results=MAX_RESULTS, backend="google"
            )
        except Exception as e:
            return f"Error: search failed: {e}"

        if not results:
            return "No results found."

        lines = []
        for r in results:
            lines.append(r.get("title", ""))
            lines.append(r.get("body", ""))
            lines.append(f"URL: {r.get('href', '')}")
            lines.append("")

        return "\n".join(lines).strip()

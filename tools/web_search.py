import json
import logging
from urllib.parse import quote_plus
from urllib.request import urlopen

from tools.base import Tool

logger = logging.getLogger(__name__)

SEARCH_URL = "https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
MAX_RESULTS = 5


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web and return top results."
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
            url = SEARCH_URL.format(query=quote_plus(query))
            with urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            return f"Error: search failed: {e}"

        results = []

        if data.get("Abstract"):
            results.append(data["Abstract"])

        for topic in data.get("RelatedTopics", [])[:MAX_RESULTS]:
            if "Text" in topic:
                results.append(topic["Text"])

        if not results:
            return "No results found."

        return "\n\n".join(results)

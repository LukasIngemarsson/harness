import json
import logging
from urllib.request import Request, urlopen

from harness.tools.base import Tool, ToolError

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 30
_MAX_RESPONSE_CHARS = 10000
_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


class HttpRequestTool(Tool):
    name = "http_request"
    description = (
        "Make an HTTP request to any URL. Supports GET,"
        " POST, PUT, PATCH, DELETE. Use this for calling"
        " APIs, webhooks, or any HTTP endpoint. Returns"
        " the response status and body."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to request",
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                "description": "HTTP method (default: GET)",
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers as key-value pairs (optional)",
            },
            "body": {
                "type": "string",
                "description": "Request body for POST/PUT/PATCH (optional)",
            },
        },
        "required": ["url"],
    }

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: dict | None = None,
        body: str | None = None,
        **kwargs: object,
    ) -> str:
        method = method.upper()
        if method not in _ALLOWED_METHODS:
            raise ToolError(f"unsupported method: {method}")

        logger.info("HTTP %s %s", method, url)

        req_headers = {"User-Agent": "Harness/1.0"}
        if headers:
            req_headers.update(headers)

        data = None
        if body:
            data = body.encode("utf-8")
            if "Content-Type" not in req_headers:
                try:
                    json.loads(body)
                    req_headers["Content-Type"] = "application/json"
                except (json.JSONDecodeError, TypeError):
                    req_headers["Content-Type"] = "text/plain"

        req = Request(
            url,
            data=data,
            headers=req_headers,
            method=method,
        )

        try:
            with urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
                status = resp.status
                resp_body = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            raise ToolError(str(e), retryable=True)

        if len(resp_body) > _MAX_RESPONSE_CHARS:
            resp_body = resp_body[:_MAX_RESPONSE_CHARS] + "\n\n[truncated]"

        return f"HTTP {status}\n\n{resp_body}"

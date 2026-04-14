import base64
import logging

from harness.config import WORKSPACE_DIR
from harness.tools.base import Tool, ToolError, ToolResult

logger = logging.getLogger(__name__)

_SUPPORTED_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
_MAX_SIZE_BYTES = 20 * 1024 * 1024


class ReadImageTool(Tool):
    name = "read_image"
    description = (
        "Read and view an image file. Use this to look"
        " at charts, plots, screenshots, or any image"
        " in the workspace. Returns the image for visual"
        " inspection. Supported formats: PNG, JPEG, GIF,"
        " WebP."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The image file path to read",
            },
        },
        "required": ["path"],
    }

    def execute(self, path: str, **kwargs: object) -> ToolResult:
        target = (WORKSPACE_DIR / path).resolve()
        if not str(target).startswith(str(WORKSPACE_DIR.resolve())):
            raise ToolError("access denied — path is outside workspace")
        if not target.exists():
            raise ToolError(f"file not found: {path}")
        if not target.is_file():
            raise ToolError(f"not a file: {path}")

        suffix = target.suffix.lower()
        if suffix not in _SUPPORTED_TYPES:
            raise ToolError(
                f"unsupported image format: {suffix}. "
                f"Supported: {', '.join(_SUPPORTED_TYPES)}"
            )

        size = target.stat().st_size
        if size > _MAX_SIZE_BYTES:
            raise ToolError(
                f"image too large: {size / 1024 / 1024:.1f}MB "
                f"(max {_MAX_SIZE_BYTES / 1024 / 1024:.0f}MB)"
            )

        logger.info("Reading image: %s", path)
        data = base64.b64encode(target.read_bytes()).decode()
        media_type = _SUPPORTED_TYPES[suffix]

        return ToolResult(
            text=f"Image loaded: {path}",
            image_base64=data,
            media_type=media_type,
        )

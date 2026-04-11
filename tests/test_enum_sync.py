import re
from pathlib import Path

from harness.enums import Command, EventType, Role, Status

TYPES_TS = Path(__file__).parent.parent / "frontend" / "src" / "types.ts"


def parse_ts_enum(content: str, enum_name: str) -> set[str]:
    pattern = rf"export enum {enum_name}\s*\{{(.*?)\}}"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return set()
    body = match.group(1)
    return set(re.findall(r'"([^"]+)"', body))


def test_event_type_sync():
    ts = TYPES_TS.read_text()
    ts_values = parse_ts_enum(ts, "EventType")
    py_values = {e.value for e in EventType}
    assert py_values == ts_values, (
        f"EventType mismatch.\n"
        f"  Python only: {py_values - ts_values}\n"
        f"  TypeScript only: {ts_values - py_values}"
    )


def test_role_sync():
    ts = TYPES_TS.read_text()
    ts_values = parse_ts_enum(ts, "MessageRole")
    py_values = {e.value for e in Role}
    assert py_values == ts_values, (
        f"Role/MessageRole mismatch.\n"
        f"  Python only: {py_values - ts_values}\n"
        f"  TypeScript only: {ts_values - py_values}"
    )


def test_status_sync():
    ts = TYPES_TS.read_text()
    ts_values = parse_ts_enum(ts, "TaskStatus")
    py_values = {e.value for e in Status}
    assert py_values == ts_values, (
        f"Status/TaskStatus mismatch.\n"
        f"  Python only: {py_values - ts_values}\n"
        f"  TypeScript only: {ts_values - py_values}"
    )

def test_command_sync():
    ts = TYPES_TS.read_text()
    ts_values = parse_ts_enum(ts, "Command")
    py_values = {e.value for e in Command}
    assert py_values == ts_values, (
        f"Command mismatch.\n"
        f"  Python only: {py_values - ts_values}\n"
        f"  TypeScript only: {ts_values - py_values}"
    )

from enum import StrEnum


class Role(StrEnum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"
    SUB_AGENT = "sub_agent"


class Status(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EventType(StrEnum):
    TOKEN = "token"
    TOOL_START = "tool_start"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_END = "tool_end"
    ERROR = "error"
    DONE = "done"
    CLEARED = "cleared"
    TASK_UPDATE = "task_update"
    SYSTEM_MESSAGE = "system_message"
    SUB_AGENT_START = "sub_agent_start"
    SUB_AGENT_EVENT = "sub_agent_event"
    SUB_AGENT_END = "sub_agent_end"


class Command(StrEnum):
    CLEAR = "/clear"
    MODE = "/mode"
    EXIT = "exit"

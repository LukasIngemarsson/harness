from harness.utils.enums import Role


def role_prefix(role: Role) -> str:
    return f"\n{role.capitalize()}: "


def tool_call_msg(name: str, args: dict) -> str:
    return f"\n[call] {name}({args})"


def tool_result_msg(result: str) -> str:
    return f"[result] {result}\n"


def error_msg(message: str) -> str:
    return f"\n[error] {message}\n"

def wrap_msg(message: str, role: str) -> str:
    return f"{role.upper()}:\n{message}\n"

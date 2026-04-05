def wrap_msg(message: str, role: str) -> str:
    return f"\n{role.capitalize()}: {message}\n"

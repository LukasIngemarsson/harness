import importlib
import pkgutil

from tools.base import Tool

TOOLS: list[Tool] = []

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name == "base":
        continue
    module = importlib.import_module(f"tools.{module_name}")
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, Tool) and obj is not Tool:
            TOOLS.append(obj())

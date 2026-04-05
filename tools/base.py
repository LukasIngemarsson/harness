from abc import ABC, abstractmethod
from pathlib import Path

WORKSPACE_DIR = Path.cwd() / ".workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)


class Tool(ABC):
    name: str
    description: str
    parameters: dict

    @abstractmethod
    def execute(self, **kwargs: object) -> str:
        raise NotImplementedError

    def to_api_format(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

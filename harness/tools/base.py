from abc import ABC, abstractmethod


class ToolError(Exception):
    def __init__(
        self, message: str, *, retryable: bool = False
    ) -> None:
        super().__init__(message)
        self.retryable = retryable


class Tool(ABC):
    name: str
    description: str
    parameters: dict
    cacheable: bool = False

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

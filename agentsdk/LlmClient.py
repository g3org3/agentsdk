from abc import ABC, abstractmethod
from typing import Literal, TypedDict


class LlmMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LlmClient(ABC):
    provider: str
    model: str

    @abstractmethod
    def request(self, messages: list[LlmMessage]) -> str:
        pass

    @abstractmethod
    def get_models(self) -> list[str]:
        pass

    def test(self) -> None:
        answer = self.request([{"role": "user", "content": "Hello!, be concise"}])
        print(f"assistant: {answer}")
        models = self.get_models()
        print("models:")
        print(" - " + "\n - ".join(models))

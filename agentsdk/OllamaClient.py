import os
from typing import Literal

import requests as r
from typing_extensions import override

from agentsdk.Chalk import chalk
from agentsdk.LlmClient import LlmClient, LlmMessage


class OllamaClient(LlmClient):
    provider: str = "Ollama"
    model: str
    host: str = "http://localhost:11434"
    headers: dict[str, str] = {}

    def __init__(
        self,
        model: Literal[
            "gpt-oss:120b-cloud",
            "gpt-oss:20b-cloud",
            "kimi-k2:1t-cloud",
            "qwen3-coder:480b-cloud",
            "qwen3-v1:235b-cloud",
            "deepseek-v3.1:671b-cloud",
            "qwen2.5-coder:1.5b",
            "qwen2.5-coder:0.5b",
            "qwen3:4b",
            "gemma3:1b",
        ],
    ) -> None:
        self.model = model
        if "cloud" in self.model:
            self.headers = {
                "Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"
            }
            self.host = "https://ollama.com"

    @override
    def get_models(self) -> list[str]:
        res = r.get(f"{self.host}/api/tags", headers=self.headers)
        return [m.get("name") for m in res.json().get("models")]

    @override
    def request(self, messages: list[LlmMessage]) -> str:
        """
        Example:
            curl http://localhost:11434/api/chat -d '{
            "model": "qwen2.5-coder:1.5b",
            "messages": [{
                "role": "user",
                "content": "Hello there!"
            }],
            "stream": false
            }'
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        res = r.post(f"{self.host}/api/chat", json=payload, headers=self.headers)
        if res.status_code != 200:
            print(chalk.red(f"[{res.status_code}] '{res.text}'"))
            res.raise_for_status()
        # TODO: validate with pydantic
        return res.json().get("message").get("content")  # pyright: ignore[reportAny]


def run():
    # client = OllamaClient(model="gemma3:1b")
    # client.test()
    client = OllamaClient(model="deepseek-v3.1:671b-cloud")
    client.test()


if __name__ == "__main__":
    run()

from typing import Literal

import requests as r
from typing_extensions import override

from agentsdk.Chalk import chalk
from agentsdk.LlmClient import LlmClient, LlmMessage


class LmStudioClient(LlmClient):
    provider: str = "LmStudio"
    model: str
    host: str = "http://localhost:1234"
    headers: dict[str, str] = {}

    def __init__(
        self,
        model: Literal["openai/gpt-oss-20b"],
    ) -> None:
        self.model = model

    @override
    def get_models(self) -> list[str]:
        res = r.get(f"{self.host}/api/v0/models", headers=self.headers)
        return [m.get("id") for m in res.json().get("data")]

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
        res = r.post(
            f"{self.host}/api/v0/chat/completions", json=payload, headers=self.headers
        )
        if res.status_code != 200:
            print(chalk.red(f"[{res.status_code}] '{res.text}'"))
            res.raise_for_status()
        # TODO: validate with pydantic
        return (
            res.json().get("choices")[0].get("message").get("content")
        )  # pyright: ignore[reportAny]


def run():
    client = LmStudioClient(model="openai/gpt-oss-20b")
    client.test()


if __name__ == "__main__":
    run()

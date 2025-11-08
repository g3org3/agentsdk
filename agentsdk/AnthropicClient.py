import os
from typing import Literal

import requests as r
from typing_extensions import override

from agentsdk.Chalk import chalk
from agentsdk.LlmClient import LlmClient, LlmMessage


class AnthropicClient(LlmClient):
    provider: str = "Anthropic"
    model: str
    host: str = "https://api.anthropic.com"
    headers: dict[str, str] = {}

    def __init__(
        self,
        model: Literal["claude-sonnet-4-5",],
    ) -> None:
        self.model = model
        self.headers = {
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        }

    @override
    def get_models(self) -> list[str]:
        res = r.get(f"{self.host}/v1/models", headers=self.headers)
        return [m.get("id") for m in res.json().get("data")]

    @override
    def request(self, messages: list[LlmMessage]) -> str:
        """
        Example:
            curl https://api.anthropic.com/v1/messages \
                --header "x-api-key: $ANTHROPIC_API_KEY" \
                --header "anthropic-version: 2023-06-01" \
                --header "content-type: application/json" \
                --data \
            '{
                "model": "claude-sonnet-4-5",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hello, world"}
                ]
            }'
        """
        system = [msg.get("content") for msg in messages if msg.get("role") == "system"]
        non_system = [msg for msg in messages if msg.get("role") != "system"]
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "system": "\n".join(system),
            "messages": non_system,
        }
        res = r.post(f"{self.host}/v1/messages", json=payload, headers=self.headers)
        if res.status_code != 200:
            print(chalk.red(f"[{res.status_code}] '{res.text}'"))
            res.raise_for_status()
        return res.json().get("content")[0].get("text")  # pyright: ignore[reportAny]


def run():
    client = AnthropicClient(model="claude-sonnet-4-5")
    client.test()


if __name__ == "__main__":
    run()

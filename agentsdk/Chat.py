#!/usr/bin/env python
import urllib3
from agents import Tool, function_tool

from agentsdk.Agent import Agent
from agentsdk.AnthropicClient import AnthropicClient
from agentsdk.Chalk import chalk
from agentsdk.LlmClient import LlmClient
from agentsdk.LmstudioClient import LmStudioClient
from agentsdk.OllamaClient import OllamaClient

urllib3.disable_warnings()


class Chat:
    agent: Agent
    tools: list[Tool]
    provider: str
    model: str
    client_by_name: dict[str, LlmClient]

    def __init__(
        self, tools: list[Tool], provider: str, model: str
    ) -> None:
        self.tools = tools
        self.provider = provider
        self.model = model
        self.client_by_name = {  # pyright: ignore[reportAttributeAccessIssue]
            "ollama": OllamaClient,
            "athropic": AnthropicClient,
            "lmstudio": LmStudioClient,
        }
        self.initAgent(self.provider, self.model)

    def initAgent(self, provider: str, model: str):
        Client = self.client_by_name.get(provider)
        if not Client:
            print("Did not found any provider")
            return
        self.agent = self.agent = Agent(
            name="Agent",
            model=Client(model=model),  # pyright: ignore[reportCallIssue, reportUnknownArgumentType]
            openai_tools=self.tools,
            instructions="You are a helpful agent",
        )
        self.provider = provider
        self.model = model

    def get_providers(self):
        return list(self.client_by_name.keys())

    def run(self):
        try:
            while True:
                user_input = input("---\n> ")
                if "/model " in user_input:
                    if self.provider == "claude":
                        model = user_input.split(" ")[1]
                        self.agent = Agent(
                            name="Agent",
                            model=AnthropicClient(model=model),
                            openai_tools=self.tools,
                            instructions="You are a helpful agent",
                        )
                        self.model = model
                        print("Changed agent")
                        continue
                    if self.provider == "ollama":
                        model = user_input.split(" ")[1]
                        self.agent = Agent(
                            name="Agent",
                            model=OllamaClient(model=model),
                            openai_tools=self.tools,
                            instructions="You are a helpful agent",
                        )
                        self.model = model
                        print("Changed agent")
                        continue

                if "/provider " in user_input:
                    if "claude" in user_input:
                        self.agent = Agent(
                            name="Agent",
                            model=AnthropicClient(model="claude-sonnet-4-5"),
                            openai_tools=self.tools,
                            instructions="You are a helpful agent",
                        )
                        self.provider = "claude"
                        print("Changed agent")
                        continue
                    if "ollama" in user_input:
                        self.agent = Agent(
                            name="Agent",
                            model=OllamaClient(model="deepseek-v3.1:671b-cloud"),
                            openai_tools=self.tools,
                            instructions="You are a helpful agent",
                        )
                        self.provider = "ollama"
                        print("Changed agent")
                        continue
                    if "lmstudio" in user_input:
                        self.agent = Agent(
                            name="Agent",
                            model=LmStudioClient(model="openai/gpt-oss-20b"),
                            openai_tools=self.tools,
                            instructions="You are a helpful agent",
                        )
                        self.provider = "lmstudio"
                        print("Changed agent lmstudio")
                        continue
                    print(f"Provider doesn't exist {user_input}")
                    continue
                if user_input == "/models":
                    models = self.agent.client.get_models()
                    print("Available models:")
                    for model in models:
                        print(f" - {model}")
                    continue
                if user_input == "clear":
                    print(chr(27) + "[2J")
                answer = self.agent.run_sync(user_input)
                print(
                    f"Assistant({self.agent.client.provider}/{self.agent.client.model}): {chalk.blue(answer)}"
                )
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")


@function_tool
def get_weahter(city: str):
    return f"Sunny in {city}"


def run():
    tools: list[Tool] = [get_weahter]
    print(f"Detected Tools: [{len(tools)}]")
    for tool in tools:
        print(f"  • {tool.name}")
    chat = Chat(tools, provider="ollama", model="qwen3-coder:480b-cloud")
    chat.run()


if __name__ == "__main__":
    run()

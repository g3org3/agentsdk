#!/usr/bin/env python
from agents import Tool, function_tool

from agentsdk.Agent import Agent
from agentsdk.Chalk import chalk
from agentsdk.OllamaClient import OllamaClient


class Chat:
    agent: Agent

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    def run(self):
        try:
            while True:
                user_input = input("---\n> ")
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

    agent = Agent(
        name="Agent",
        model=OllamaClient(model="qwen3-coder:480b-cloud"),
        openai_tools=tools,
        instructions="You are a helpful agent",
    )
    chat = Chat(agent)
    chat.run()


if __name__ == "__main__":
    run()

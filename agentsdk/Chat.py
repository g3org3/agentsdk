from agentsdk.LlmClient import Agent


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

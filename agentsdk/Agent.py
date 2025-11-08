import asyncio
import json

from agents import Tool
from agents.tool_context import ToolContext

from agentsdk.agent_types import AgentAction, ToolDef
from agentsdk.Chalk import chalk
from agentsdk.LlmClient import LlmClient, LlmMessage


class Agent:
    agent_name: str
    client: LlmClient
    instructions: str = ""
    tools: list[Tool] = []
    tool_by_name: dict[str, Tool] = {}
    tool_def_by_name: dict[str, ToolDef] = {}
    history: list[LlmMessage] = []
    sytem_promp_tool_resolver: str = ""
    system_prompt_interpret_answer: str = ""

    def __init__(
        self,
        name: str,
        model: LlmClient,
        instructions: str = "",
        openai_tools: list[Tool] | None = None,
    ) -> None:
        self.client = model
        self.agent_name = name
        self.tools = openai_tools or []
        self.instructions = instructions
        self.tool_by_name = {}
        for tool in self.tools:
            self.tool_by_name[tool.name] = tool
        self.parse_openai_tools(openai_tools or [])
        with open("./agentsdk/agent_pick_tool_prompt.md") as fh:
            self.sytem_promp_tool_resolver = "".join(fh.readlines()).strip()
        with open("./agentsdk/assistant_prompt.md") as fh:
            self.system_prompt_interpret_answer = "".join(fh.readlines()).strip()

    def agent_ask(self, prompt: str) -> AgentAction:
        messages: list[LlmMessage] = [
            {"role": "system", "content": self.sytem_promp_tool_resolver},
            {"role": "system", "content": self.instructions.strip()},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_question": prompt,
                        "context": self.history,
                        "tools": list(self.tool_def_by_name.values()),
                    }
                ),
            },
        ]
        answer = self.client.request(messages)
        print(f"{chalk.yellow('[DEBUG]')} {chalk.purple(answer)}")
        tools_to_call = answer.replace("```json", "").replace("```", "").strip()
        tools_to_call = tools_to_call.replace('<|channel|>final <|constrain|>JSON<|message|>', '')
        tools_to_call = tools_to_call.replace('<|channel|>final <|constrain|>json<|message|>', '')

        # TODO: validate with pydantic
        return json.loads(tools_to_call)  # pyright: ignore[reportAny]

    def run_sync(self, prompt: str):
        return asyncio.run(self.run(prompt))

    async def run(self, prompt: str):
        if prompt == "clear":
            self.history = []
            return "cleared"
        print(chalk.grey("  [thinking_which_tool_to_use]"))
        action = self.agent_ask(prompt)
        print(chalk.grey("  [calling_the_tools]"))
        answers = await self.tool_resolver(action)
        print(chalk.grey("  [interpreting_the_answer]"))
        messages: list[LlmMessage] = [
            {"role": "system", "content": self.system_prompt_interpret_answer},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_question": prompt,
                        "tool_results": answers,
                        "context": self.history,
                    }
                ),
            },
        ]
        res = self.client.request(messages)
        self.history.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        self.history.append(
            {
                "role": "assistant",
                "content": res,
                "tools_results": answers,
            }
        )
        print(f"CONTEXT: {chalk.yellow(json.dumps(self.history, indent=2))}")
        return res

    async def tool_resolver(self, agent_action: AgentAction):
        action = agent_action.get("action")
        if action != "use_tools":
            return []
        answers = []
        tools_to_call = agent_action.get("tools_selected")
        for tool_call in tools_to_call:
            name = tool_call.get("name")
            tool: Tool | None = self.tool_by_name.get(name)
            if not isinstance(tool, Tool):
                continue

            # TODO: fix id
            ctx = ToolContext("", tool_name=tool.name, tool_call_id="123123")
            agent_action = await tool.on_invoke_tool(  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                ctx, json.dumps(tool_call.get("parameters") or {})
            )
            answers.append(
                {
                    "name": name,
                    "parameters": tool_call.get("parameters") or {},
                    "description": tool_call.get("description"),
                    "result": str(agent_action),
                }
            )
        return answers

    def parse_openai_tools(self, openai_tools: list[Tool]) -> None:
        for tool in openai_tools:
            params: dict[str, str] = {}
            json_params: dict[str, dict[str, str]] = (
                tool.params_json_schema.get(  # pyright: ignore[reportAttributeAccessIssue, reportAssignmentType, reportUnknownMemberType]
                    "properties"
                )
            )
            for param_name in json_params.keys():
                param = json_params.get(param_name)
                assert param
                param_type = param.get("type")
                if param_type:
                    if param_type == "array":
                        params.setdefault(
                            param_name, "arrray<string>"
                        )  # pyright: ignore[reportUnusedCallResult]
                    else:
                        params.setdefault(
                            param_name, param_type
                        )  # pyright: ignore[reportUnusedCallResult]
                else:
                    param_type = [
                        p
                        for p in param.get(
                            "anyOf"
                        )  # pyright: ignore[reportOptionalIterable]
                        if p.get(
                            "type"
                        )  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                        != "null"
                    ][0]
                    params.setdefault(
                        param_name, param_type
                    )  # pyright: ignore[reportUnusedCallResult]
            tool_def: ToolDef = {
                "name": tool.name,
                "description": tool.description,  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                "parameters": params,
            }
            self.tool_def_by_name[tool.name] = tool_def

    def clear(self):
        self.history = []

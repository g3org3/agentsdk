from typing import Literal, TypedDict


class ToolDef(TypedDict):
    name: str
    description: str
    parameters: dict[str, str]


class ActionTool(TypedDict):
    name: str
    reason: str
    parameters: dict[str, dict[str, str]]


class AgentAction(TypedDict):
    action: Literal["use_tools"]
    tools_selected: list[ActionTool]

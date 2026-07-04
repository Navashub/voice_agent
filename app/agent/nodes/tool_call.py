from app.agent.state import AgentState
from app.agent.tools.registry import get_tool

INTENT_TO_TOOL = {
    "book_callback": "book_callback",
}


def run(state: AgentState) -> AgentState:
    intent = state["intent"]
    tool_name = INTENT_TO_TOOL.get(intent, "check_availability")
    tool_fn = get_tool(tool_name)
    state["tool_result"] = tool_fn(state)
    return state

from app.agent.state import AgentState
from app.agent.tools.registry import get_tool

INTENT_TO_TOOL = {
    "book_callback": "book_callback",
}


def run(state: AgentState) -> AgentState:
    intent = state["intent"]
    wants_callback = intent == "book_callback" or state.get("awaiting_phone")

    if wants_callback:
        lead_info = state.get("lead_info", {})

        if not lead_info.get("phone"):
            # Don't book yet — a callback with no phone number is useless.
            # Ask for it, and remember we're waiting so the next reply
            # (which may just be digits, not clearly "book_callback"
            # phrasing) still routes back here instead of derailing.
            state["awaiting_phone"] = True
            state["intent"] = "book_callback"
            state["tool_result"] = {
                "status": "need_phone",
                "message": "Sure — what's the best phone number to reach you on for that callback?",
            }
            return state

        state["awaiting_phone"] = False
        state["intent"] = "book_callback"
        tool_fn = get_tool("book_callback")
        state["tool_result"] = tool_fn(state)
        return state

    tool_fn = get_tool("check_availability")
    state["tool_result"] = tool_fn(state)
    return state

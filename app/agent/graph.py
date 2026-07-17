from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import classify_and_extract, retrieve, tool_call, escalate, respond


def _route_after_classify(state: AgentState) -> str:
    if state.get("awaiting_phone"):
        # We just asked for a phone number — whatever the caller says next
        # (often just digits, which won't classify cleanly) goes straight
        # back to tool_call to check whether we got it.
        return "tool_call"

    intent = state.get("intent")
    if intent == "info_question":
        return "retrieve"
    if intent in ("book_callback", "check_availability"):
        return "tool_call"
    if intent == "escalate":
        return "escalate"
    return "respond"  # "other" — greetings/small talk, no KB lookup needed


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_and_extract", classify_and_extract.run)
    graph.add_node("retrieve", retrieve.run)
    graph.add_node("tool_call", tool_call.run)
    graph.add_node("escalate", escalate.run)
    graph.add_node("respond", respond.run)

    graph.set_entry_point("classify_and_extract")

    graph.add_conditional_edges(
        "classify_and_extract",
        _route_after_classify,
        {
            "retrieve": "retrieve",
            "tool_call": "tool_call",
            "escalate": "escalate",
            "respond": "respond",
        },
    )

    graph.add_edge("retrieve", "respond")
    graph.add_edge("tool_call", "respond")
    graph.add_edge("escalate", "respond")
    graph.add_edge("respond", END)

    return graph.compile()

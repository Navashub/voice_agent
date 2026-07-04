from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import classify_intent, extract_lead_info, retrieve, tool_call, escalate, respond


def _route_after_classify(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "info_question":
        return "retrieve"
    if intent in ("book_callback", "check_availability"):
        return "tool_call"
    if intent == "escalate":
        return "escalate"
    return "retrieve"  # "other" falls through to a best-effort informational answer


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent.run)
    graph.add_node("extract_lead_info", extract_lead_info.run)
    graph.add_node("retrieve", retrieve.run)
    graph.add_node("tool_call", tool_call.run)
    graph.add_node("escalate", escalate.run)
    graph.add_node("respond", respond.run)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "extract_lead_info")

    graph.add_conditional_edges(
        "extract_lead_info",
        _route_after_classify,
        {
            "retrieve": "retrieve",
            "tool_call": "tool_call",
            "escalate": "escalate",
        },
    )

    graph.add_edge("retrieve", "respond")
    graph.add_edge("tool_call", "respond")
    graph.add_edge("escalate", "respond")
    graph.add_edge("respond", END)

    return graph.compile()

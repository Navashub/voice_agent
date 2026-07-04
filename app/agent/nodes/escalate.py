from app.agent.state import AgentState
from app.agent.tools.log_lead import run as log_lead


def run(state: AgentState) -> AgentState:
    log_lead(state)
    state["escalate"] = True
    state["tool_result"] = {
        "status": "escalated",
        "message": (
            "I'm connecting you with a member of our team who can help further. "
            "They'll reach out to you shortly."
        ),
    }
    return state

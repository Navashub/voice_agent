from app.agent.state import AgentState
from app.knowledge_base.retriever import retrieve_context
from app.agent.tools.log_unknown_question import run as log_unknown_question


def run(state: AgentState) -> AgentState:
    query = state["user_input"]
    tenant_id = state["tenant_id"]
    context = retrieve_context(tenant_id, query)
    state["retrieved_context"] = context

    if not context:
        # Nothing relevant was found — this is a gap in the knowledge base,
        # not just a one-off unanswered question. Log it for review.
        log_unknown_question(state)

    return state

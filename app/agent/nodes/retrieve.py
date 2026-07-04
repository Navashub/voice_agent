from app.agent.state import AgentState
from app.knowledge_base.retriever import retrieve_context


def run(state: AgentState) -> AgentState:
    query = state["user_input"]
    tenant_id = state["tenant_id"]
    state["retrieved_context"] = retrieve_context(tenant_id, query)
    return state

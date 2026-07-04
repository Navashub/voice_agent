from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.tenants.config_loader import get_tenant_config

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)


def run(state: AgentState) -> AgentState:
    tenant_config = get_tenant_config(state["tenant_id"])

    tool_result = state.get("tool_result") or {}
    context = state.get("retrieved_context") or ""
    grounding = tool_result.get("message") or context or (
        "No specific information was found — offer to have someone follow up."
    )

    prompt = f"""{tenant_config.system_prompt}

Caller said: {state["user_input"]}

Relevant information to use in your reply: {grounding}

Rules:
- Only state facts that appear in the relevant information above.
- If the relevant information does not answer the caller's question, say
  clearly that you don't have that information and offer to have someone
  follow up. Do not guess and do not make up an answer.
- Never contradict yourself mid-answer. Decide the correct answer first,
  then say it once, cleanly.

Respond naturally as the receptionist, 2-3 sentences max."""

    result = llm.invoke(prompt)
    state["response"] = result.content.strip()
    return state

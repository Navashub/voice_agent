from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.tenants.config_loader import get_tenant_config

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)


def run(state: AgentState) -> AgentState:
    tenant_config = get_tenant_config(state["tenant_id"])
    intent = state.get("intent")
    lead_info = state.get("lead_info") or {}

    known_info = ", ".join(f"{k}: {v}" for k, v in lead_info.items() if v) or "nothing yet"

    tool_result = state.get("tool_result") or {}
    context = state.get("retrieved_context") or ""

    if intent == "info_question":
        grounding = tool_result.get("message") or context or (
            "No matching information was found in the knowledge base."
        )
        grounding_block = f"""Relevant information to use in your reply: {grounding}

Rules:
- Only state facts that appear in the relevant information above.
- If the relevant information does not answer the caller's question, say
  clearly that you don't have that information right now. Then invite them
  to ask for a callback if they'd like someone to follow up — do NOT say
  "let me take your details" or imply you're already arranging a callback,
  since that only happens if the caller actually asks for one.
- Never invent a fact, number, or promise that isn't in the relevant
  information above."""
    elif intent in ("book_callback", "escalate"):
        grounding_block = f"Relevant information to use in your reply: {tool_result.get('message', '')}"
    else:
        # "other" — greetings, small talk, unclear input. No KB lookup was done
        # for this turn, so don't force in grounding rules that don't apply.
        grounding_block = (
            "This is casual conversation — no specific institute information "
            "is needed here. Respond naturally and warmly. Only mention "
            "programs, fees, or location if the caller actually brought it up "
            "or it clearly helps move the conversation forward — don't recite "
            "it by default."
        )

    prompt = f"""{tenant_config.system_prompt}

What you already know about this caller so far: {known_info}

Caller said: {state["user_input"]}

{grounding_block}

General rules:
- Never contradict yourself mid-answer. Decide the correct answer first,
  then say it once, cleanly.
- If the caller asks whether you know something about them (like their
  name) and it appears above, confirm it naturally — don't say you don't
  have it.
- Don't recite caller details, location, or contact information unless the
  caller actually asked for it or it's clearly relevant right now.

Respond naturally as the receptionist, 2-3 sentences max."""

    result = llm.invoke(prompt)
    state["response"] = result.content.strip()
    return state

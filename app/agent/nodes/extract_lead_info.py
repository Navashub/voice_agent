import json

from langchain_groq import ChatGroq

from app.agent.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

EXTRACT_PROMPT = """Extract any of the following details mentioned in the caller's message, if present:
- name
- phone
- interest (the program/course they're asking about or interested in)

Respond ONLY with a JSON object with keys "name", "phone", "interest".
Use null for any field not mentioned. No other text, no markdown formatting.

Message: {message}
"""


def run(state: AgentState) -> AgentState:
    message = state["user_input"]
    prompt = EXTRACT_PROMPT.format(message=message)
    result = llm.invoke(prompt)

    raw = result.content.strip().strip("`")
    if raw.lower().startswith("json"):
        raw = raw[4:].strip()

    try:
        extracted = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        extracted = {}

    lead_info = state.get("lead_info") or {}
    for key in ("name", "phone", "interest"):
        value = extracted.get(key)
        if value:
            lead_info[key] = value

    state["lead_info"] = lead_info
    return state

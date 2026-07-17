"""
Combines what used to be two separate nodes (classify_intent + extract_lead_info)
into a single LLM call. They never depended on each other's output, so running
them as two sequential network round trips was pure wasted latency — this
alone should noticeably speed up every turn.
"""

import json
import re

from langchain_groq import ChatGroq

from app.agent.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

VALID_INTENTS = {"info_question", "book_callback", "escalate", "other"}

# Deterministic override — if the agent's last message offered a callback and
# the caller gives a short affirmative, it's book_callback, no LLM guessing
# needed. Cheaper and more reliable than trusting classification every time.
AFFIRMATIVE_PATTERN = re.compile(
    r"^\s*(yes|yeah|yep|yup|sure|okay|ok|please|kindly|go ahead|alright|"
    r"sounds good|that works|please do|yes please|sure please)\b",
    re.IGNORECASE,
)

PROMPT = """Analyze the caller's LATEST message and respond with ONLY a JSON object with these keys:

- intent: one of "info_question", "book_callback", "escalate", "other"
  - info_question: asking about programs, fees, deadlines, requirements, location, general info
  - book_callback: wants a human to call them back, wants to book an appointment
  - escalate: angry, urgent, a complaint, or explicitly asking for a human
  - other: greetings, unclear, anything not covered above
- name: the caller's name if mentioned in this message, else null
- phone: a phone number if mentioned in this message, else null
- interest: the program/course they're asking about or interested in, if mentioned, else null
- preferred_callback_time: when they want a callback if specified (e.g. "tomorrow morning"), else null

Previous agent message (if any): {last_agent_message}
Caller's latest message: {message}

Respond with ONLY the JSON object — no other text, no markdown formatting.
"""


def _last_agent_message(state: AgentState) -> str:
    for msg in reversed(state.get("messages", [])):
        if msg["role"] == "assistant":
            return msg["content"]
    return "(none — this is the first message)"


def run(state: AgentState) -> AgentState:
    message = state["user_input"]
    last_agent_message = _last_agent_message(state)

    prompt = PROMPT.format(last_agent_message=last_agent_message, message=message)
    result = llm.invoke(prompt)

    raw = result.content.strip().strip("`")
    if raw.lower().startswith("json"):
        raw = raw[4:].strip()

    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        parsed = {}

    intent = str(parsed.get("intent", "")).lower()
    if intent not in VALID_INTENTS:
        intent = "info_question"  # safe default

    if "callback" in last_agent_message.lower() and AFFIRMATIVE_PATTERN.match(message.strip()):
        intent = "book_callback"

    state["intent"] = intent

    lead_info = state.get("lead_info") or {}
    for key in ("name", "phone", "interest", "preferred_callback_time"):
        value = parsed.get(key)
        if value:
            lead_info[key] = value
    state["lead_info"] = lead_info

    return state

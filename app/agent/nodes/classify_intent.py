import re

from langchain_groq import ChatGroq

from app.agent.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

VALID_INTENTS = {"info_question", "book_callback", "escalate", "other"}

# If the agent's last message offered a callback and the caller replies with
# a short affirmative, treat it as book_callback directly — don't rely on
# the LLM to catch this every time. This is one of the most common patterns
# in a real call, so it needs to be reliable, not probabilistic.
AFFIRMATIVE_PATTERN = re.compile(
    r"^\s*(yes|yeah|yep|yup|sure|okay|ok|please|kindly|go ahead|alright|"
    r"sounds good|that works|please do|yes please|sure please)\b",
    re.IGNORECASE,
)

INTENT_PROMPT = """Classify the caller's LATEST message into exactly one category:
- info_question: asking about programs, fees, deadlines, requirements, location, general info
- book_callback: wants a human to call them back, wants to book an appointment or consultation
  (including a short confirmation like "yes" or "sure" if the previous agent message offered a callback)
- escalate: angry, urgent, a complaint, or explicitly asking for a human/agent
- other: greetings, unclear, or anything not covered above

Use the previous agent message only to interpret short/ambiguous replies
("yes", "sure", "please do") — classify based on what the caller wants, not
what the agent said.

Previous agent message (if any): {last_agent_message}

Caller's latest message: {message}

Respond with only the category word, nothing else.
"""


def _last_agent_message(state: AgentState) -> str:
    for msg in reversed(state.get("messages", [])):
        if msg["role"] == "assistant":
            return msg["content"]
    return "(none — this is the first message)"


def run(state: AgentState) -> AgentState:
    message = state["user_input"]
    last_agent_message = _last_agent_message(state)

    if "callback" in last_agent_message.lower() and AFFIRMATIVE_PATTERN.match(message.strip()):
        state["intent"] = "book_callback"
        return state

    prompt = INTENT_PROMPT.format(last_agent_message=last_agent_message, message=message)
    result = llm.invoke(prompt)
    intent = result.content.strip().lower()

    if intent not in VALID_INTENTS:
        intent = "info_question"  # safe default

    state["intent"] = intent
    return state

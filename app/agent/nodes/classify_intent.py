# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from app.agent.state import AgentState

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

VALID_INTENTS = {"info_question", "book_callback", "escalate", "other"}

INTENT_PROMPT = """Classify the caller's message into exactly one category:
- info_question: asking about programs, fees, deadlines, requirements, location, general info
- book_callback: wants a human to call them back, wants to book an appointment or consultation
- escalate: angry, urgent, a complaint, or explicitly asking for a human/agent
- other: greetings, unclear, or anything not covered above

Respond with only the category word, nothing else.

Message: {message}
"""


def run(state: AgentState) -> AgentState:
    message = state["user_input"]
    prompt = INTENT_PROMPT.format(message=message)
    result = llm.invoke(prompt)
    intent = result.content.strip().lower()

    if intent not in VALID_INTENTS:
        intent = "info_question"  # safe default

    state["intent"] = intent
    return state

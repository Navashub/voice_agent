"""
Test the agent brain in plain text before wiring up any telephony.

Usage:
    python chat_cli.py
"""
from dotenv import load_dotenv
load_dotenv()

from app.agent.graph import build_graph

TENANT_ID = "example_institute"


def main():
    graph = build_graph()
    print("Voice Agent CLI — type 'quit' to exit\n")

    while True:
        user_input = input("Caller: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        state = {
            "tenant_id": TENANT_ID,
            "messages": [],
            "user_input": user_input,
            "intent": None,
            "retrieved_context": None,
            "tool_result": None,
            "response": None,
            "lead_info": {},
            "escalate": False,
        }

        result = graph.invoke(state)
        print(f"[intent: {result['intent']}]")
        print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    main()

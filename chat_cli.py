"""
Test the agent brain in plain text before wiring up any telephony.

State now persists across the whole session (one run = one simulated call),
so lead_info and conversation history accumulate turn to turn — the same way
it will behave on a real phone call.

Usage:
    python chat_cli.py
"""

from dotenv import load_dotenv
load_dotenv()

from app.agent.graph import build_graph

TENANT_ID = "luxdev"


def fresh_state():
    return {
        "tenant_id": TENANT_ID,
        "messages": [],
        "user_input": "",
        "intent": None,
        "retrieved_context": None,
        "tool_result": None,
        "response": None,
        "lead_info": {},
        "escalate": False,
    }


def main():
    graph = build_graph()
    state = fresh_state()

    print("Voice Agent CLI — type 'quit' to exit, 'newcall' to reset session\n")

    while True:
        user_input = input("Caller: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "newcall":
            state = fresh_state()
            print("(new call session started — lead_info cleared)\n")
            continue
        if not user_input:
            continue

        # Persist lead_info and messages across the whole call.
        # Reset everything that's specific to THIS turn, so a leftover
        # tool_result or context from a previous question can't leak in.
        state["user_input"] = user_input
        state["intent"] = None
        state["retrieved_context"] = None
        state["tool_result"] = None
        state["response"] = None
        state["escalate"] = False
        state["messages"].append({"role": "user", "content": user_input})

        state = graph.invoke(state)

        state["messages"].append({"role": "assistant", "content": state["response"]})

        print(f"[intent: {state['intent']}]  [lead_info: {state['lead_info']}]")
        print(f"Agent: {state['response']}\n")


if __name__ == "__main__":
    main()
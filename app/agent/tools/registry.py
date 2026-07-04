from app.agent.tools import log_lead, book_callback, check_availability

TOOL_MAP = {
    "log_lead": log_lead.run,
    "book_callback": book_callback.run,
    "check_availability": check_availability.run,
}


def get_tool(name: str):
    if name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_MAP[name]

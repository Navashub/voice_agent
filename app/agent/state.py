"""
AgentState - what flows through every node in the LangGraph.

Keep this the same across ALL tenants. Tenant-specific behavior comes from
config (system prompt, enabled tools, kb namespace) looked up by tenant_id,
never from new fields bolted onto this schema per client.
"""

from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict):
    tenant_id: str

    # Conversation
    messages: List[Dict[str, str]]   # [{"role": "user"/"assistant", "content": "..."}]
    user_input: str                   # latest caller utterance (from STT, or typed in CLI)

    # Routing
    intent: Optional[str]             # "info_question" | "book_callback" | "escalate" | "other"

    # Working data
    retrieved_context: Optional[str]  # RAG chunks relevant to the query
    tool_result: Optional[Dict[str, Any]]
    lead_info: Dict[str, Any]         # accumulated info about the caller (name, phone, interest)
    escalate: bool

    # Output
    response: Optional[str]           # final natural-language reply (goes to TTS in production)

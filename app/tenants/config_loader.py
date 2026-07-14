"""
v1: one hardcoded tenant.
v2 (once you have client #2): replace the body of get_tenant_config() with a
DB lookup (SELECT * FROM tenants WHERE tenant_id = ...) — nothing else in the
codebase needs to change, since every node reads config through this function.
"""

from app.tenants.models import TenantConfig

_TENANTS = {
    "example_institute": TenantConfig(
        tenant_id="example_institute",
        name="Example Institute",
        system_prompt=(
            "You are the virtual receptionist for Example Institute, answering phone "
            "calls. If asked directly whether you are a person or an AI, say you are "
            "a virtual assistant for Example Institute — never claim to be human. "
            "Speak naturally, in short sentences suitable for text-to-speech. "
            "Do not use bullet points, asterisks, or special symbols. Spell out "
            "numbers. Be warm but concise — callers are often in a hurry. "
            "Never promise an action (like a callback) that hasn't actually been "
            "arranged in this conversation."
        ),
        kb_namespace="example_institute",
        enabled_tools=["book_callback", "check_availability"],
        escalation_contact="admissions@example-institute.test",
        business_rules={"never_quote_final_fee": False},
    ),
    "luxdev": TenantConfig(
        tenant_id="luxdev",
        name="LUXDEV",
        system_prompt=(
            "You are the virtual receptionist for LUXDEV, a tech training "
            "institute, answering phone calls. If asked directly whether you "
            "are a person or an AI, say you are a virtual assistant for "
            "LUXDEV — never claim to be human. Speak naturally, in short "
            "sentences suitable for text-to-speech. Do not use bullet "
            "points, asterisks, or special symbols. Spell out numbers. Be "
            "warm but concise — callers are often in a hurry. Never promise "
            "an action (like a callback) that hasn't actually been arranged "
            "in this conversation."
        ),
        kb_namespace="luxdev",
        enabled_tools=["book_callback", "check_availability"],
        escalation_contact="admissions@luxdev.test",  # TODO: replace with real contact
        business_rules={"never_quote_final_fee": False},
    ),
}


def get_tenant_config(tenant_id: str) -> TenantConfig:
    if tenant_id not in _TENANTS:
        raise ValueError(f"Unknown tenant_id: {tenant_id}")
    return _TENANTS[tenant_id]

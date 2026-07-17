"""
Local leads.json is always written first — it's the reliable source of
truth even if Airtable is briefly down. The Airtable push is best-effort
on top of that, so your boss/team can see leads live in Airtable without
you needing to build any dashboard.

Airtable table expected: "Leads" with fields:
    Tenant, Name, Phone, Interest, Intent, Message, Timestamp
"""

import json
import os
from datetime import datetime, timezone

from app.integrations.airtable_client import push_record

LEADS_FILE = "leads.json"


def run(state: dict) -> dict:
    lead_info = state.get("lead_info", {})
    # Prefer the original message that actually triggered this callback
    # (set in tool_call.py) over the current turn's input, which by the
    # time we're logging might just be "0715623803" from confirming a
    # phone number — not useful on its own in a Leads table.
    message = lead_info.get("_original_request") or state.get("user_input")

    lead = {
        "tenant_id": state.get("tenant_id"),
        "message": message,
        "intent": state.get("intent"),
        "lead_info": lead_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    leads = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            try:
                leads = json.load(f)
            except json.JSONDecodeError:
                leads = []

    leads.append(lead)

    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    push_record("Leads", {
        "Tenant": lead["tenant_id"],
        "Name": lead_info.get("name"),
        "Phone": lead_info.get("phone"),
        "Interest": lead_info.get("interest"),
        "Intent": lead["intent"],
        "Message": lead["message"],
        "Timestamp": lead["timestamp"],
    })

    return {"status": "logged", "lead": lead}

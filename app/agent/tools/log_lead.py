"""
v1: appends to a local leads.json file so you can see captured leads immediately.
v2: swap the body for an INSERT into the `leads` table (see architecture doc) —
callers of this function don't need to change.
"""

import json
import os
from datetime import datetime, timezone

LEADS_FILE = "leads.json"


def run(state: dict) -> dict:
    lead = {
        "tenant_id": state.get("tenant_id"),
        "message": state.get("user_input"),
        "intent": state.get("intent"),
        "lead_info": state.get("lead_info", {}),
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

    return {"status": "logged", "lead": lead}

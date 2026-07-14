"""
Every time retrieval comes back empty for an info_question, that question
gets logged here — separate from leads.json. This is your "what does the
agent not know yet" queue. Also pushed to Airtable so review can happen
there directly instead of opening raw JSON.

Airtable table expected: "KnowledgeGaps" with fields:
    Tenant, Question, Timestamp, Status

Workflow: periodically review the KnowledgeGaps table (or knowledge_gaps.json
locally), add real answers to the tenant's markdown docs in
tenants_data/{tenant_id}/, then re-run ingest.py. Next time someone asks the
same thing, it's answered without a human.
"""

import json
import os
from datetime import datetime, timezone

from app.integrations.airtable_client import push_record

GAPS_FILE = "knowledge_gaps.json"


def run(state: dict) -> dict:
    entry = {
        "tenant_id": state.get("tenant_id"),
        "question": state.get("user_input"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unanswered",  # flip to "added_to_kb" once you've resolved it
    }

    gaps = []
    if os.path.exists(GAPS_FILE):
        with open(GAPS_FILE, "r", encoding="utf-8") as f:
            try:
                gaps = json.load(f)
            except json.JSONDecodeError:
                gaps = []

    gaps.append(entry)

    with open(GAPS_FILE, "w", encoding="utf-8") as f:
        json.dump(gaps, f, indent=2)

    push_record("KnowledgeGaps", {
        "Tenant": entry["tenant_id"],
        "Question": entry["question"],
        "Timestamp": entry["timestamp"],
        "Status": entry["status"],
    })

    return entry

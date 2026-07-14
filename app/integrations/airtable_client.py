"""
Thin wrapper around Airtable's REST API. Kept generic (table name + fields
dict) so any future integration (Leads, KnowledgeGaps, or something new
later) can reuse it without new code — just call push_record with a
different table name.

Requires in .env:
    AIRTABLE_API_KEY   (Personal Access Token, needs data.records:write scope)
    AIRTABLE_BASE_ID    (starts with "app...")
"""

import os

import requests

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

BASE_URL = "https://api.airtable.com/v0"


def push_record(table_name: str, fields: dict) -> bool:
    """Pushes one record to Airtable. Returns True on success, False on
    failure — callers should treat this as best-effort and keep their local
    JSON log as the source of truth, since a call shouldn't fail just
    because Airtable is briefly unreachable."""
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("[Airtable] Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID — skipping push.")
        return False

    url = f"{BASE_URL}/{AIRTABLE_BASE_ID}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, headers=headers, json={"fields": fields}, timeout=5)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[Airtable] push to '{table_name}' failed: {e}")
        return False

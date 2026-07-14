"""
Quick way to see what your agent doesn't know yet.

Usage:
    python review_gaps.py
"""

import json
import os
from collections import Counter

GAPS_FILE = "knowledge_gaps.json"


def main():
    if not os.path.exists(GAPS_FILE):
        print("No knowledge gaps logged yet.")
        return

    with open(GAPS_FILE, "r", encoding="utf-8") as f:
        gaps = json.load(f)

    unresolved = [g for g in gaps if g.get("status") == "unanswered"]

    if not unresolved:
        print("No unresolved gaps — everything logged has been addressed.")
        return

    print(f"{len(unresolved)} unanswered question(s):\n")
    for g in unresolved:
        print(f"  [{g['tenant_id']}] {g['timestamp']}")
        print(f"    \"{g['question']}\"\n")

    print("Most common phrasing patterns worth checking:")
    counts = Counter(g["question"].lower().strip() for g in unresolved)
    for question, count in counts.most_common(5):
        if count > 1:
            print(f"  ({count}x) {question}")

    print(
        "\nOnce you've added answers to the relevant tenant's markdown docs "
        "and re-run ingest.py, mark these resolved manually in "
        "knowledge_gaps.json (status: 'added_to_kb') so they stop showing up here."
    )


if __name__ == "__main__":
    main()

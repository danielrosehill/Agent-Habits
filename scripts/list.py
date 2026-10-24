#!/usr/bin/env python3
"""List the habits from assembled/habits.json.

    python3 scripts/list.py            # active habits: id, stance, summary
    python3 scripts/list.py --all      # include retired
    python3 scripts/list.py --json     # the same, as JSON
"""

import argparse
import json
from pathlib import Path

ASSEMBLED = Path(__file__).resolve().parent.parent / "assembled" / "habits.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    habits = json.loads(ASSEMBLED.read_text(encoding="utf-8"))["habits"]
    if not args.all:
        habits = [h for h in habits if h.get("status", "active") == "active"]
    rows = [{k: h.get(k) for k in ("id", "status", "stance", "order", "title", "summary")}
            for h in habits]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for r in rows:
        flag = "" if r["status"] == "active" else f" [{r['status']}]"
        print(f"{r['order']:>3}  {r['id']}{flag} ({r['stance']})\n     {r['summary']}")
    print(f"\n{len(rows)} habits")


if __name__ == "__main__":
    main()

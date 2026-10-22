#!/usr/bin/env python3
"""Install or update the habits block inside a system prompt file.

The block is delimited by markers so it can be rewritten idempotently without
touching anything the user wrote by hand:

    <!-- habits-of-claude:begin -->
    ...generated...
    <!-- habits-of-claude:end -->

Dry-run by default; --write is required to touch the file, and a timestamped backup
is made first. Existing hand-written prose covering the same ground is NOT removed —
that is a judgement call, so it is reported and left alone. Use the
reconcile-habits skill for that.

    python3 scripts/install.py                          # dry run against ~/CLAUDE.md
    python3 scripts/install.py --write
    python3 scripts/install.py --only agent-first,verify-dont-infer --write
    python3 scripts/install.py --target ./AGENTS.md --write
    python3 scripts/install.py --set APPROVAL_LIMIT='$20' --write

Habits that declare variables are rendered from their template. A value comes from
--set if given, else from the values recorded in the block already installed in the
target (so a reinstall keeps your tuning), else from the habit's default. The values
used are recorded in a comment inside the block.
"""

import argparse
import datetime as dt
import difflib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSEMBLED = ROOT / "assembled" / "habits.json"

BEGIN = "<!-- habits-of-claude:begin -->"
END = "<!-- habits-of-claude:end -->"
VARS = re.compile(r"<!-- habits-of-claude:variables (\{.*?\}) -->")
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def installed_values(text):
    """Variable values recorded in an already-installed block, keyed by NAME."""
    match = VARS.search(text.partition(BEGIN)[2].partition(END)[0]) if BEGIN in text else None
    return json.loads(match.group(1)) if match else {}


def resolve(habits, recorded, overrides):
    """Render each templated habit; return the values actually used."""
    declared = {name for h in habits for name in h.get("variables", {})}
    unknown = overrides.keys() - declared
    if unknown:
        sys.exit(f"unknown variable(s): {', '.join(sorted(unknown))}")
    used = {}
    for habit in habits:
        if "template" not in habit:
            continue
        values = {
            name: overrides.get(name, recorded.get(name, default))
            for name, default in habit["variables"].items()
        }
        habit["snippet"] = PLACEHOLDER.sub(lambda m: values[m.group(1)], habit["template"])
        used.update(values)
    return used


def build_block(habits, values):
    lines = [
        BEGIN,
        f"<!-- Generated from Habits-Of-Claude on {dt.date.today().isoformat()}."
        " Edit habits/*.md there, then re-run scripts/install.py. -->",
    ]
    if values:
        lines.append(
            f"<!-- habits-of-claude:variables {json.dumps(values, ensure_ascii=False)} -->"
        )
    lines += [
        "",
        "## Habits",
        "",
        "Standing habits, in force before the task is known.",
        "",
    ]
    for habit in habits:
        lines += [f"### {habit['title']}", "", habit["snippet"], ""]
    lines.append(END)
    return "\n".join(lines)


def splice(text, block):
    if BEGIN in text and END in text:
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        return head + block + tail, "updated existing block"
    sep = "" if text.endswith("\n\n") or not text.strip() else "\n"
    return text.rstrip("\n") + "\n\n" + block + "\n", "appended new block"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(Path.home() / "CLAUDE.md"))
    ap.add_argument("--only", default="", help="comma-separated habit ids")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a habit variable; repeatable")
    args = ap.parse_args()
    overrides = {}
    for item in args.set:
        name, sep, value = item.partition("=")
        if not sep:
            sys.exit(f"--set expects NAME=VALUE, got '{item}'")
        overrides[name.strip()] = value

    if not ASSEMBLED.exists():
        sys.exit("assembled/habits.json missing — run scripts/assemble.py first")
    habits = json.loads(ASSEMBLED.read_text(encoding="utf-8"))["habits"]

    if args.only:
        wanted = [h.strip() for h in args.only.split(",") if h.strip()]
        known = {h["id"] for h in habits}
        unknown = [w for w in wanted if w not in known]
        if unknown:
            sys.exit(f"unknown habit id(s): {', '.join(unknown)}")
        habits = [h for h in habits if h["id"] in wanted]

    target = Path(args.target).expanduser()
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    values = resolve(habits, installed_values(original), overrides)
    updated, action = splice(original, build_block(habits, values))

    if updated == original:
        print(f"{target}: already up to date ({len(habits)} habits)")
        return

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=str(target),
        tofile=f"{target} (proposed)",
    )
    sys.stdout.writelines(diff)

    if not args.write:
        print(f"\n-- dry run: {action}, {len(habits)} habits. Re-run with --write.")
        return

    if original:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_suffix(target.suffix + f".bak-{stamp}")
        shutil.copy2(target, backup)
        print(f"\nbackup: {backup}")
    target.write_text(updated, encoding="utf-8")
    print(f"{target}: {action}, {len(habits)} habits")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build assembled/habits.md and assembled/habits.json from habits/*.md.

Each habit file is frontmatter (including a one-line `summary`, which is what the
installed index block carries), then a `## Snippet` section (the text destined for a
system prompt) and a `## Why` section (rationale, for me, excluded from output).

A habit may declare tunable values in a nested `variables:` block and reference them
in its snippet as `{{NAME}}`. The assembled snippet carries the defaults; the raw
template and the defaults are also written to habits.json so install.py can render
other values.

No third-party dependencies on purpose — this has to run anywhere without a venv, so
the frontmatter parser handles only the scalar, inline-list and one-level
`variables:` mapping forms actually used.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HABITS = ROOT / "habits"
OUT = ROOT / "assembled"

SCALARS = ("id", "title", "summary", "stance", "added", "revised", "status", "source")
STATUSES = ("active", "retired")
SUMMARY_MAX = 320  # characters; the summary sits in every session's context
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def unquote(value):
    return value.strip().strip('"').strip("'")


def render(template, values):
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def parse(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        sys.exit(f"{path.name}: missing frontmatter")
    _, fm, body = text.split("---\n", 2)

    meta = {}
    block = None
    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":
            if block != "variables":
                sys.exit(f"{path.name}: indented line outside a variables block")
            name, _, value = line.strip().partition(":")
            # values are quoted, so a trailing '# comment' is safe to strip
            value = re.sub(r"\s+#.*$", "", value.strip())
            meta["variables"][name.strip()] = unquote(value)
            continue
        block = None
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip() for v in inner.split(",") if v.strip()]
        elif key == "order":
            meta[key] = int(value)
        elif key == "variables" and not value:
            meta[key] = {}
            block = "variables"
        else:
            meta[key] = value.strip('"').strip("'")

    for key in ("id", "title", "stance", "order"):
        if key not in meta:
            sys.exit(f"{path.name}: frontmatter missing '{key}'")
    if meta["id"] != path.stem:
        sys.exit(f"{path.name}: id '{meta['id']}' does not match filename")
    if meta["stance"] not in ("practice", "prohibition"):
        sys.exit(f"{path.name}: stance must be practice or prohibition")
    meta.setdefault("status", "active")
    if meta["status"] not in STATUSES:
        sys.exit(f"{path.name}: status must be one of {', '.join(STATUSES)}")
    if meta["status"] == "active" and not meta.get("summary"):
        sys.exit(f"{path.name}: active habit needs a 'summary'")
    if len(meta.get("summary", "")) > SUMMARY_MAX:
        sys.exit(f"{path.name}: summary is {len(meta['summary'])} chars, max {SUMMARY_MAX}")

    sections = {}
    for match in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", body, re.S | re.M):
        sections[match.group(1).strip().lower()] = match.group(2).strip()
    if "snippet" not in sections:
        sys.exit(f"{path.name}: no '## Snippet' section")

    template = sections["snippet"]
    variables = meta.get("variables", {})
    used = set(PLACEHOLDER.findall(template)) | set(PLACEHOLDER.findall(meta.get("summary", "")))
    if used - variables.keys():
        sys.exit(f"{path.name}: undeclared variable(s): {', '.join(sorted(used - variables.keys()))}")
    if variables.keys() - used:
        sys.exit(f"{path.name}: unused variable(s): {', '.join(sorted(variables.keys() - used))}")
    if variables:
        meta["template"] = template
        meta["summary_template"] = meta.get("summary", "")
    meta["snippet"] = render(template, variables)
    if "summary" in meta:
        meta["summary"] = render(meta["summary"], variables)
    meta["why"] = sections.get("why", "")
    return meta


def main():
    files = sorted(HABITS.glob("*.md"))
    if not files:
        sys.exit(f"no habit files found in {HABITS}")
    habits = sorted((parse(p) for p in files), key=lambda h: h["order"])

    ids = [h["id"] for h in habits]
    for habit in habits:
        for ref in habit.get("related", []):
            if ref not in ids:
                sys.exit(f"{habit['id']}: related habit '{ref}' does not exist")

    OUT.mkdir(exist_ok=True)

    md = [
        "# Habits",
        "",
        "<!-- Generated by scripts/assemble.py — edit habits/*.md, not this file. -->",
        "",
        "Standing habits, in force before the task is known.",
        "",
    ]
    for habit in habits:
        if habit["status"] == "active":
            md += [f"## {habit['title']}", "", habit["snippet"], ""]
    (OUT / "habits.md").write_text("\n".join(md), encoding="utf-8")

    payload = {
        "generated_by": "scripts/assemble.py",
        "count": len(habits),
        "active": sum(h["status"] == "active" for h in habits),
        "habits": [
            {k: h[k] for k in ("id", "title", "summary", "stance", "order", "snippet") if k in h}
            | {k: h[k] for k in ("added", "revised", "status", "source", "related") if k in h}
            | {k: h[k] for k in ("variables", "template", "summary_template") if k in h}
            for h in habits
        ],
    }
    (OUT / "habits.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    active = sum(h["status"] == "active" for h in habits)
    print(f"{active} active of {len(habits)} habits -> assembled/habits.md, assembled/habits.json")


if __name__ == "__main__":
    main()

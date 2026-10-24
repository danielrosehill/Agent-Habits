#!/usr/bin/env python3
"""Install or update the habits in a system prompt file.

Two modes.

index (default): the full habit texts are written as one file each into a habits
folder (default ~/.config/agent-habits/), and the system prompt gets only a short
block: one line per habit carrying its summary, and a pointer to the folder. This is
what keeps ~/CLAUDE.md small — the summaries are always in context, the full texts
are read on demand.

inline: the full snippets go into the block itself, as before. Use it for a project
CLAUDE.md or AGENTS.md that other people read, where a pointer into one user's home
directory means nothing.

The block is delimited by markers so it can be rewritten idempotently without
touching anything the user wrote by hand:

    <!-- habits-of-claude:begin -->
    ...generated...
    <!-- habits-of-claude:end -->

Dry-run by default; --write is required to touch anything, and the target file is
backed up first. Existing hand-written prose covering the same ground is NOT removed
— that is a judgement call. Use the reconcile-habits skill for that.

    python3 scripts/install.py                          # dry run, index mode, ~/CLAUDE.md
    python3 scripts/install.py --write
    python3 scripts/install.py --mode inline --only agent-first,verify-dont-infer \\
        --target ./CLAUDE.md --write
    python3 scripts/install.py --set APPROVAL_LIMIT='$20' --write

Habits that declare variables are rendered from their template. A value comes from
--set if given, else from the values recorded in the block already installed in the
target (so a reinstall keeps your tuning), else from the habit's default. The values
used are recorded in a comment inside the block, and in the folder's index.json.

Only habits with status: active are installed. In index mode, generated files in the
folder for habits that are no longer installed are removed; files without the
generated header are never touched.
"""

import argparse
import datetime as dt
import difflib
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSEMBLED = ROOT / "assembled" / "habits.json"
DEFAULT_DIR = "~/.config/agent-habits"

BEGIN = "<!-- habits-of-claude:begin -->"
END = "<!-- habits-of-claude:end -->"
VARS = re.compile(r"<!-- habits-of-claude:variables (\{.*?\}) -->")
DIR_MARK = re.compile(r"<!-- habits-of-claude:dir (.+?) -->")
FILE_MARK = "<!-- habits-of-claude:generated"
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def block_of(text):
    return text.partition(BEGIN)[2].partition(END)[0] if BEGIN in text else ""


def installed_values(text):
    """Variable values recorded in an already-installed block, keyed by NAME."""
    match = VARS.search(block_of(text))
    return json.loads(match.group(1)) if match else {}


def installed_dir(text):
    """Habits folder recorded in an already-installed block, as written (with ~)."""
    match = DIR_MARK.search(block_of(text))
    return match.group(1) if match else None


def tilde(path):
    """Display form of a path, with $HOME as ~, so the block is machine-portable."""
    home = str(Path.home())
    s = str(path)
    return "~" + s[len(home):] if s == home or s.startswith(home + os.sep) else s


def load_habits(only=""):
    if not ASSEMBLED.exists():
        sys.exit("assembled/habits.json missing — run scripts/assemble.py first")
    habits = json.loads(ASSEMBLED.read_text(encoding="utf-8"))["habits"]
    habits = [h for h in habits if h.get("status", "active") == "active"]
    if only:
        wanted = [h.strip() for h in only.split(",") if h.strip()]
        known = {h["id"] for h in habits}
        unknown = [w for w in wanted if w not in known]
        if unknown:
            sys.exit(f"unknown or inactive habit id(s): {', '.join(unknown)}")
        habits = [h for h in habits if h["id"] in wanted]
    return habits


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
        sub = lambda t: PLACEHOLDER.sub(lambda m: values[m.group(1)], t)
        habit["snippet"] = sub(habit["template"])
        if habit.get("summary_template"):
            habit["summary"] = sub(habit["summary_template"])
        used.update(values)
    return used


def header(values, extra=()):
    lines = [
        BEGIN,
        f"<!-- Generated from Habits-Of-Claude on {dt.date.today().isoformat()}."
        " Edit habits/*.md there, then re-run scripts/install.py. -->",
    ]
    if values:
        lines.append(
            f"<!-- habits-of-claude:variables {json.dumps(values, ensure_ascii=False)} -->"
        )
    return lines + list(extra)


def build_inline(habits, values):
    lines = header(values) + [
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


def build_index(habits, values, shown_dir):
    lines = header(values, [f"<!-- habits-of-claude:dir {shown_dir} -->"]) + [
        "",
        "## Habits",
        "",
        "Standing habits, in force before the task is known. Each line is the rule. The",
        f"full text, with its exceptions, is `{shown_dir}/<id>.md`. Read it when a task",
        "falls squarely under a habit, or when the line leaves you unsure.",
        "",
    ]
    for habit in habits:
        lines.append(f"- **{habit['title']}** (`{habit['id']}`): {habit['summary']}")
    lines += ["", END]
    return "\n".join(lines)


def habit_file(habit):
    return "\n".join([
        f"{FILE_MARK} from Habits-Of-Claude habits/{habit['id']}.md on"
        f" {dt.date.today().isoformat()}. Do not edit here. -->",
        "",
        f"# {habit['title']}",
        "",
        f"> {habit['summary']}",
        "",
        habit["snippet"],
        "",
    ])


def folder_plan(habits, values, habits_dir, prune):
    """Files to write into the habits folder, and generated files to remove."""
    files = {f"{h['id']}.md": habit_file(h) for h in habits}
    index = {
        "generated_by": "Habits-Of-Claude scripts/install.py",
        "source_repo": str(ROOT),
        "generated": dt.date.today().isoformat(),
        "variables": values,
        "habits": [
            {k: h[k] for k in ("id", "title", "stance", "summary")} | {"file": f"{h['id']}.md"}
            for h in habits
        ],
    }
    files["index.json"] = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    stale = []
    if prune and habits_dir.is_dir():
        for path in sorted(habits_dir.glob("*.md")):
            if path.name not in files and path.read_text(encoding="utf-8").startswith(FILE_MARK):
                stale.append(path)
    return files, stale


def same_ignoring_dates(a, b):
    """Compare generated text without the generation dates, so a rebuild on a new
    day with identical content does not count as a change."""
    strip = lambda s: re.sub(r"\d{4}-\d{2}-\d{2}", "", s)
    return strip(a) == strip(b)


def splice(text, block):
    if BEGIN in text and END in text:
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        return head + block + tail, "updated existing block"
    return text.rstrip("\n") + "\n\n" + block + "\n", "appended new block"


def plan(target, mode="index", habits_dir=None, only="", overrides=None):
    """Everything install would change, without changing it. Used by check.py too."""
    target = Path(target).expanduser()
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    habits = load_habits(only)
    values = resolve(habits, installed_values(original), overrides or {})
    result = {"target": target, "original": original, "habits": habits,
              "files": {}, "stale": [], "dir": None}
    if mode == "inline":
        block = build_inline(habits, values)
    else:
        chosen = habits_dir or installed_dir(original) or DEFAULT_DIR
        folder = Path(chosen).expanduser()
        result["dir"] = folder
        block = build_index(habits, values, tilde(folder))
        result["files"], result["stale"] = folder_plan(habits, values, folder, prune=not only)
    result["updated"], result["action"] = splice(original, block)
    if same_ignoring_dates(result["updated"], original):
        result["updated"] = original
    return result


def changed_files(p):
    out = []
    for name, content in p["files"].items():
        path = p["dir"] / name
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old is None or not same_ignoring_dates(old, content):
            out.append((path, old, content))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(Path.home() / "CLAUDE.md"))
    ap.add_argument("--mode", choices=("index", "inline"), default="index")
    ap.add_argument("--habits-dir", default=None,
                    help=f"index mode: where the full habit files go (default: the folder"
                         f" recorded in the target's block, else {DEFAULT_DIR})")
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

    p = plan(args.target, args.mode, args.habits_dir, args.only, overrides)
    target, original, updated = p["target"], p["original"], p["updated"]
    files = changed_files(p) if p["dir"] else []
    count = len(p["habits"])

    if updated == original and not files and not p["stale"]:
        print(f"{target}: already up to date ({count} habits, {args.mode} mode)")
        return

    if updated != original:
        sys.stdout.writelines(difflib.unified_diff(
            original.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile=str(target), tofile=f"{target} (proposed)"))
    for path, old, _ in files:
        print(f"{'update' if old is not None else 'create'}: {path}")
    for path in p["stale"]:
        print(f"remove: {path}")

    if not args.write:
        print(f"\n-- dry run: {p['action'] if updated != original else 'block unchanged'},"
              f" {count} habits, {args.mode} mode. Re-run with --write.")
        return

    if p["dir"]:
        p["dir"].mkdir(parents=True, exist_ok=True)
        for path, _, content in files:
            path.write_text(content, encoding="utf-8")
        for path in p["stale"]:
            path.unlink()
    if updated != original:
        if original:
            stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = target.with_suffix(target.suffix + f".bak-{stamp}")
            shutil.copy2(target, backup)
            print(f"\nbackup: {backup}")
        target.write_text(updated, encoding="utf-8")
    print(f"{target}: {p['action'] if updated != original else 'block unchanged'},"
          f" {count} habits, {args.mode} mode")


if __name__ == "__main__":
    main()

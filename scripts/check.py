#!/usr/bin/env python3
"""Validate the habits, and validate what is installed from them.

    python3 scripts/check.py source     # habits/*.md build cleanly and assembled/ is current
    python3 scripts/check.py context    # the installed block and habits folder are correct
    python3 scripts/check.py            # both
    python3 scripts/check.py --json     # machine-readable report

`context` checks the target (default ~/CLAUDE.md) has exactly one managed block, in
index mode, under the size budget, with one line per active habit; that the habits
folder it points at holds exactly the generated files install.py would write now;
and that nothing outside the block is headed `## Habits`. Exits 1 if any check fails.
Warnings do not fail the run.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install  # noqa: E402

ROOT = install.ROOT
BLOCK_BUDGET = 6000  # characters; roughly 1,500 tokens resident in every session


def check_source():
    fails, warns = [], []
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "assemble.py")],
                         capture_output=True, text=True)
    if run.returncode:
        return [f"assemble.py failed: {(run.stderr or run.stdout).strip()}"], warns
    diff = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "assembled/"],
                          capture_output=True, text=True).stdout.strip()
    if diff:
        warns.append("assembled/ changed on rebuild — it was stale or habits are uncommitted")
    habits = json.loads(install.ASSEMBLED.read_text(encoding="utf-8"))["habits"]
    titles = [h["title"].lower() for h in habits]
    for t in {t for t in titles if titles.count(t) > 1}:
        fails.append(f"duplicate title: {t}")
    status = {h["id"]: h["status"] for h in habits}
    for h in habits:
        if h["status"] == "active":
            for ref in h.get("related", []):
                if status.get(ref) == "retired":
                    warns.append(f"{h['id']}: related to retired habit {ref}")
    return fails, warns


def check_context(target, habits_dir=None):
    fails, warns = [], []
    target = Path(target).expanduser()
    if not target.exists():
        return [f"{target} does not exist"], warns
    text = target.read_text(encoding="utf-8")
    n_begin, n_end = text.count(install.BEGIN), text.count(install.END)
    if (n_begin, n_end) != (1, 1):
        return [f"expected one managed block, found {n_begin} begin / {n_end} end markers"], warns
    block = install.block_of(text)
    outside = text.replace(install.BEGIN + block + install.END, "")
    if re.search(r"^#{1,3} Habits\s*$", outside, re.M):
        fails.append("a hand-written '## Habits' heading exists outside the managed block")
    if not install.installed_dir(text):
        fails.append("block is inline mode (no habits-of-claude:dir marker); reinstall in index mode")
        return fails, warns
    if len(block) > BLOCK_BUDGET:
        fails.append(f"block is {len(block)} chars, budget {BLOCK_BUDGET}")

    p = install.plan(target, "index", habits_dir)
    for h in p["habits"]:
        if f"(`{h['id']}`)" not in block:
            fails.append(f"block has no line for active habit {h['id']}")
    for listed in re.findall(r"\(`([a-z0-9-]+)`\)", block):
        if listed not in {h["id"] for h in p["habits"]}:
            fails.append(f"block lists {listed}, which is not an active habit")
    if p["updated"] != p["original"]:
        fails.append("block text is stale; run install.py --write")
    if not p["dir"].is_dir():
        fails.append(f"habits folder {p['dir']} does not exist")
    else:
        for path, old, _ in install.changed_files(p):
            fails.append(f"{'missing' if old is None else 'stale'}: {path}")
        for path in p["stale"]:
            fails.append(f"left over from a removed habit: {path}")
        for path in sorted(p["dir"].glob("*.md")):
            if not path.read_text(encoding="utf-8").startswith(install.FILE_MARK):
                warns.append(f"hand-written file in the habits folder: {path.name}")
    return fails, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", nargs="?", choices=("source", "context", "all"), default="all")
    ap.add_argument("--target", default=str(Path.home() / "CLAUDE.md"))
    ap.add_argument("--habits-dir", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = {}
    if args.what in ("source", "all"):
        report["source"] = dict(zip(("fail", "warn"), check_source()))
    if args.what in ("context", "all"):
        report["context"] = dict(zip(("fail", "warn"), check_context(args.target, args.habits_dir)))
    ok = not any(r["fail"] for r in report.values())
    report["ok"] = ok

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for name, r in report.items():
            if name == "ok":
                continue
            print(f"{name}: {'FAIL' if r['fail'] else 'ok'}")
            for f in r["fail"]:
                print(f"  fail: {f}")
            for w in r["warn"]:
                print(f"  warn: {w}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

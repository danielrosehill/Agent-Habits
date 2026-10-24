#!/usr/bin/env python3
"""Agent-Habits: standing habits and SOPs for an AI agent, one markdown file each.

Three places, three lifecycles:

    <repo>/library/habits/*.md      public example habits, with {{VARIABLES}}
    <root>/habits/*.md              the user's own habits, concrete, private
    <root>/sops/*.md                the user's own SOPs (see sop.py)

<root> is the user-data root: --root, else $CLAUDE_USER_DATA, else
~/.claude-user-data. It is one private git repo, one folder per tool.

The system prompt (default ~/CLAUDE.md) gets one generated, marker-delimited block:
one summary line per habit, triggered habits grouped separately, one trigger line
per SOP, and pointers to the folders. The full texts are read on demand.

    habits.py path                          resolved locations
    habits.py list [--library] [--all] [--json]
    habits.py adopt ID [--set NAME=VALUE ...] [--force]
    habits.py outdated                      adopted habits whose library copy is newer
    habits.py validate [--library]          exit 1 on a broken habit
    habits.py index [--library]             write index.json (and the SOP INDEX.md)
    habits.py install [--target F] [--mode index|inline] [--only a,b] [--write]
    habits.py check [library|source|context|all] [--target F] [--json]

Standard library only, so it runs anywhere without a venv. The frontmatter parser
handles only the scalar, inline-list and one-level `variables:` forms in use.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIBRARY = REPO / "library" / "habits"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sop  # noqa: E402  (SOP loading, validation and INDEX.md)

BEGIN = "<!-- agent-habits:begin -->"
END = "<!-- agent-habits:end -->"
# Markers written by earlier versions; install replaces them in place.
LEGACY = [("<!-- habits-of-claude:begin -->", "<!-- habits-of-claude:end -->"),
          ("<!-- claude-sops:begin -->", "<!-- claude-sops:end -->")]
RESERVED = {"README.md", "INDEX.md"}
KINDS = ("habit",)
STANCES = ("practice", "prohibition")
STATUSES = ("active", "retired")
SUMMARY_MAX = 320   # characters; the summary sits in every session's context
BLOCK_BUDGET = 7000  # characters for the whole block, roughly 1,750 tokens
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


# ---------------------------------------------------------------- locations

def user_root(arg=None) -> Path:
    if arg:
        return Path(arg).expanduser()
    env = os.environ.get("CLAUDE_USER_DATA")
    return Path(env).expanduser() if env else Path.home() / ".claude-user-data"


def tilde(path) -> str:
    """Display form with $HOME as ~, so the block reads the same on every machine."""
    home, s = str(Path.home()), str(path)
    return "~" + s[len(home):] if s == home or s.startswith(home + os.sep) else s


def today() -> str:
    return dt.date.today().isoformat()


# ---------------------------------------------------------------- parsing

def unquote(value: str) -> str:
    return value.strip().strip('"').strip("'")


def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: missing frontmatter")
    _, fm, body = text.split("---\n", 2)

    meta, block = {"variables": {}}, None
    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":
            if block != "variables":
                raise ValueError(f"{path.name}: indented line outside a variables block")
            name, _, value = line.strip().partition(":")
            meta["variables"][name.strip()] = unquote(re.sub(r"\s+#.*$", "", value.strip()))
            continue
        block = None
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        elif key == "order":
            meta[key] = int(value)
        elif key == "variables" and not value:
            block = "variables"
        else:
            meta[key] = unquote(value)

    for key in ("id", "title", "stance", "order"):
        if key not in meta:
            raise ValueError(f"{path.name}: frontmatter missing '{key}'")
    meta.setdefault("kind", "habit")
    meta.setdefault("status", "active")
    if meta["id"] != path.stem:
        raise ValueError(f"{path.name}: id '{meta['id']}' does not match filename")
    if meta["kind"] not in KINDS:
        raise ValueError(f"{path.name}: kind must be one of {KINDS} (procedures are SOPs, in sops/)")
    if meta["stance"] not in STANCES:
        raise ValueError(f"{path.name}: stance must be one of {STANCES}")
    if meta["status"] not in STATUSES:
        raise ValueError(f"{path.name}: status must be one of {STATUSES}")
    if meta["status"] == "active" and not meta.get("summary"):
        raise ValueError(f"{path.name}: active habit needs a 'summary'")
    if len(meta.get("summary", "")) > SUMMARY_MAX:
        raise ValueError(f"{path.name}: summary is {len(meta['summary'])} chars, max {SUMMARY_MAX}")

    sections = {m.group(1).strip().lower(): m.group(2).strip()
                for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", body, re.S | re.M)}
    if "snippet" not in sections:
        raise ValueError(f"{path.name}: no '## Snippet' section")
    meta["template"] = sections["snippet"]
    meta["why"] = sections.get("why", "")

    used = set(PLACEHOLDER.findall(meta["template"])) | set(PLACEHOLDER.findall(meta.get("summary", "")))
    declared = set(meta["variables"])
    if used - declared:
        raise ValueError(f"{path.name}: undeclared variable(s): {', '.join(sorted(used - declared))}")
    if declared - used:
        raise ValueError(f"{path.name}: unused variable(s): {', '.join(sorted(declared - used))}")
    render(meta, {})
    meta["path"] = path
    return meta


def render(meta: dict, overrides: dict) -> dict:
    values = {k: overrides.get(k, v) for k, v in meta["variables"].items()}
    sub = lambda t: PLACEHOLDER.sub(lambda m: values[m.group(1)], t)
    meta["snippet"] = sub(meta["template"])
    meta["summary_rendered"] = sub(meta.get("summary", ""))
    return values


def load(folder: Path, active_only=True, strict=None) -> list[dict]:
    """strict: a dangling `related:` id is an error. True for the library; for the
    user's own folder it's only a warning (check source), since adopting a subset
    of the library legitimately leaves references to habits not adopted."""
    strict = (folder == LIBRARY) if strict is None else strict
    if not folder.is_dir():
        sys.exit(f"no habits folder at {folder}")
    habits = [parse(p) for p in sorted(folder.glob("*.md")) if p.name not in RESERVED]
    ids = {h["id"] for h in habits}
    titles = [h["title"].lower() for h in habits]
    for h in habits:
        for ref in h.get("related", []):
            if strict and ref not in ids:
                raise ValueError(f"{h['id']}: related habit '{ref}' does not exist")
        if titles.count(h["title"].lower()) > 1:
            raise ValueError(f"{h['id']}: duplicate title '{h['title']}'")
    habits.sort(key=lambda h: h["order"])
    return [h for h in habits if h["status"] == "active"] if active_only else habits


def version_of(meta: dict) -> str:
    return meta.get("revised") or meta.get("added", "")


def load_active_sops(root: Path) -> list[dict]:
    folder = root / "sops"
    if not folder.is_dir():
        return []
    out = []
    for path in sop.sop_files(folder):
        fm, _ = sop.parse_front_matter(path.read_text(encoding="utf-8"))
        if fm.get("status", "active") == "active":
            out.append(fm | {"id": fm.get("id", path.stem)})
    return out


# ---------------------------------------------------------------- outputs

PUBLIC_KEYS = ("id", "title", "kind", "stance", "order", "trigger", "added", "revised",
               "status", "source", "related", "library", "library_version")


def write_index(folder: Path, habits: list[dict], library=False) -> Path:
    rows = []
    for h in habits:
        row = {k: h[k] for k in PUBLIC_KEYS if k in h}
        row["summary"] = h.get("summary", "") if library else h["summary_rendered"]
        if library and h["variables"]:
            row["variables"] = h["variables"]
        row["file"] = h["path"].name
        rows.append(row)
    payload = {"generated_by": "Agent-Habits scripts/habits.py", "plugin_repo": str(REPO), "generated": today(),
               "count": len(rows), "habits": rows}
    out = folder / "index.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def build_index_block(habits, sops, root: Path) -> str:
    hdir, sdir = tilde(root / "habits"), tilde(root / "sops")
    always = [h for h in habits if not h.get("trigger")]
    triggered = [h for h in habits if h.get("trigger")]
    line = lambda h: f"- **{h['title']}** (`{h['id']}`): {h['summary_rendered']}"
    out = [
        BEGIN,
        f"<!-- Generated by Agent-Habits on {today()} from {tilde(root)}. Edit the files"
        " there, then run `habits.py install --write`. -->",
        "",
        "## Habits",
        "",
        "Standing habits, in force before the task is known. Each line is the rule. The",
        f"full text, with exceptions and rationale, is `{hdir}/<id>.md`. Read it when a",
        "task falls squarely under a habit, or when the line leaves you unsure.",
        "",
        *map(line, always),
    ]
    if triggered:
        out += ["", "These apply only when their trigger does:", ""]
        out += [f"- *When {h['trigger']}:* **{h['title']}** (`{h['id']}`): {h['summary_rendered']}"
                for h in triggered]
    out += [
        "",
        "## Procedures",
        "",
        f"Recurring procedures (SOPs) live in `{sdir}/`. Before improvising a multi-step",
        "job, check whether one matches below; if one does, read that `<id>.md` and",
        "follow it, at its stated autonomy. If the same sequence comes up a second time",
        "and no SOP covers it, offer to write one.",
        "",
    ]
    out += ([f"- When {s.get('trigger', '')}: `{s['id']}`" for s in sops]
            or ["None written yet."])
    out += ["", END]
    return "\n".join(out)


def build_inline_block(habits) -> str:
    out = [BEGIN, f"<!-- Generated by Agent-Habits on {today()}. -->", "", "## Habits", "",
           "Standing habits, in force before the task is known.", ""]
    for h in habits:
        heading = h["title"] + (f" (when {h['trigger']})" if h.get("trigger") else "")
        out += [f"### {heading}", "", h["snippet"], ""]
    out.append(END)
    return "\n".join(out)


def find_blocks(text: str):
    """(begin, end) marker pairs present in text, current first."""
    return [(b, e) for b, e in [(BEGIN, END)] + LEGACY if b in text or e in text]


def splice(text: str, block: str):
    pairs = find_blocks(text)
    for b, e in pairs:
        if text.count(b) != 1 or text.count(e) != 1:
            sys.exit(f"marker {b} or {e} appears other than exactly once; fix by hand")
    if not pairs:
        return text.rstrip("\n") + "\n\n" + block + "\n", "appended new block"
    # Replace the first block found, drop any others (legacy SOP block, etc.).
    (b0, e0), rest = pairs[0], pairs[1:]
    head, _, tail = text.partition(b0)
    tail = tail.partition(e0)[2]
    text = head + block + tail
    for b, e in rest:
        head, _, tail = text.partition(b)
        text = head.rstrip("\n") + "\n" + tail.partition(e)[2]
    return text, "updated existing block" + (f", removed {len(rest)} legacy block(s)" if rest else "")


def same_ignoring_dates(a: str, b: str) -> bool:
    strip = lambda s: re.sub(r"\d{4}-\d{2}-\d{2}", "", s)
    return strip(a) == strip(b)


def plan_install(target, root: Path, mode="index", only=""):
    target = Path(target).expanduser()
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    habits = load(root / "habits")
    if only:
        wanted = [w.strip() for w in only.split(",") if w.strip()]
        unknown = set(wanted) - {h["id"] for h in habits}
        if unknown:
            sys.exit(f"unknown or retired habit id(s): {', '.join(sorted(unknown))}")
        habits = [h for h in habits if h["id"] in wanted]
    block = (build_inline_block(habits) if mode == "inline"
             else build_index_block(habits, load_active_sops(root), root))
    updated, action = splice(original, block)
    if same_ignoring_dates(updated, original):
        updated, action = original, "unchanged"
    return {"target": target, "original": original, "updated": updated,
            "action": action, "block": block, "habits": habits}


# ---------------------------------------------------------------- commands

def cmd_path(a):
    root = user_root(a.root)
    print(json.dumps({"repo": str(REPO), "library": str(LIBRARY), "root": str(root),
                      "habits": str(root / "habits"), "sops": str(root / "sops")}, indent=2))


def cmd_list(a):
    folder = LIBRARY if a.library else user_root(a.root) / "habits"
    habits = load(folder, active_only=not a.all)
    rows = [{k: h.get(k) for k in ("id", "status", "stance", "order", "trigger", "title")}
            | {"summary": h["summary_rendered"]} for h in habits]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for r in rows:
        flag = "" if r["status"] == "active" else f" [{r['status']}]"
        when = f"  (when {r['trigger']})" if r["trigger"] else ""
        print(f"{r['order']:>3}  {r['id']}{flag} ({r['stance']}){when}\n     {r['summary']}")
    print(f"\n{len(rows)} habits in {tilde(folder)}")


def cmd_adopt(a):
    src = LIBRARY / f"{a.id}.md"
    if not src.exists():
        sys.exit(f"no library habit '{a.id}'; see `habits.py list --library`")
    meta = parse(src)
    overrides = dict(kv.split("=", 1) for kv in a.set)
    unknown = set(overrides) - set(meta["variables"])
    if unknown:
        sys.exit(f"'{a.id}' has no variable(s): {', '.join(sorted(unknown))}")
    dst_dir = user_root(a.root) / "habits"
    dst = dst_dir / src.name
    if dst.exists() and not a.force:
        sys.exit(f"{dst} exists; use --force to replace it with the library version")
    values = render(meta, overrides)
    text = src.read_text(encoding="utf-8")
    _, fm, body = text.split("---\n", 2)
    kept, skip = [], False
    for line in fm.splitlines():
        if line.startswith("variables:"):
            skip = True
            continue
        if skip and line[:1] in (" ", "\t"):
            continue
        skip = False
        if line.split(":", 1)[0].strip() in ("source", "library", "library_version"):
            continue
        kept.append(line)
    kept += [f'source: "Habits library, adopted {today()}"',
             f"library: {a.id}", f"library_version: {version_of(meta)}"]
    out = "---\n" + "\n".join(kept) + "\n---\n" + body
    out = PLACEHOLDER.sub(lambda m: values[m.group(1)], out)
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"adopted {a.id} -> {dst}" + (f" with {values}" if values else ""))


def cmd_outdated(a):
    lib = {h["id"]: h for h in load(LIBRARY, active_only=False)}
    rows = []
    for h in load(user_root(a.root) / "habits", active_only=False):
        src = lib.get(h.get("library", ""))
        if src and version_of(src) > h.get("library_version", ""):
            rows.append({"id": h["id"], "adopted": h.get("library_version"),
                         "library": version_of(src)})
    print(json.dumps(rows, indent=2) if a.json else
          "\n".join(f"{r['id']}: adopted {r['adopted']}, library now {r['library']}" for r in rows)
          or "all adopted habits match the library")


def cmd_validate(a):
    folder = LIBRARY if a.library else user_root(a.root) / "habits"
    try:
        habits = load(folder, active_only=False)
    except ValueError as exc:
        sys.exit(str(exc))
    print(f"ok: {len(habits)} habits valid in {tilde(folder)}")


def cmd_index(a):
    if a.library:
        print(write_index(LIBRARY, load(LIBRARY, active_only=False), library=True))
        return
    root = user_root(a.root)
    print(write_index(root / "habits", load(root / "habits", active_only=False)))
    if (root / "sops").is_dir():
        print(sop.write_index(root / "sops"))


def cmd_install(a):
    root = user_root(a.root)
    p = plan_install(a.target, root, a.mode, a.only)
    if p["action"] == "unchanged":
        print(f"{p['target']}: already up to date ({len(p['habits'])} habits, {a.mode} mode)")
        return
    sys.stdout.writelines(difflib.unified_diff(
        p["original"].splitlines(keepends=True), p["updated"].splitlines(keepends=True),
        fromfile=str(p["target"]), tofile=f"{p['target']} (proposed)"))
    if not a.write:
        print(f"\n-- dry run: {p['action']}, {len(p['habits'])} habits, {a.mode} mode."
              " Re-run with --write.")
        return
    if p["original"]:
        backup = p["target"].with_suffix(
            p["target"].suffix + f".bak-{dt.datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(p["target"], backup)
        print(f"\nbackup: {backup}")
    p["target"].write_text(p["updated"], encoding="utf-8")
    if a.mode == "index" and not a.only:
        write_index(root / "habits", load(root / "habits", active_only=False))
        if (root / "sops").is_dir():
            sop.write_index(root / "sops")
    print(f"{p['target']}: {p['action']}, {len(p['habits'])} habits, {a.mode} mode")


def check_library():
    fails, warns = [], []
    try:
        habits = load(LIBRARY, active_only=False)
    except ValueError as exc:
        return [str(exc)], warns
    idx = LIBRARY / "index.json"
    if not idx.exists():
        fails.append("library/habits/index.json missing; run `habits.py index --library`")
    else:
        current = json.loads(idx.read_text(encoding="utf-8"))
        ids = [r["id"] for r in current["habits"]]
        if ids != [h["id"] for h in habits] or any(
                r.get("summary") != h.get("summary", "") for r, h in zip(current["habits"], habits)):
            fails.append("library/habits/index.json is stale; run `habits.py index --library`")
    for h in habits:
        if "source" in h and h["source"] != "Habits library":
            warns.append(f"library/{h['id']}: source is '{h['source']}', expected 'Habits library'")
    return fails, warns


def check_source(root: Path):
    fails, warns = [], []
    try:
        habits = load(root / "habits", active_only=False)
    except (ValueError, SystemExit) as exc:
        return [str(exc)], warns
    status = {h["id"]: h["status"] for h in habits}
    for h in habits:
        for ref in h.get("related", []):
            if ref not in status:
                warns.append(f"{h['id']}: related habit '{ref}' is not in your habits")
        if h["status"] == "active" and PLACEHOLDER.search(h["template"] + h.get("summary", "")):
            warns.append(f"{h['id']}: still has {{{{VARIABLES}}}}; adopt renders them")
        for ref in h.get("related", []):
            if h["status"] == "active" and status.get(ref) == "retired":
                warns.append(f"{h['id']}: related to retired habit {ref}")
    if (root / "sops").is_dir():
        run = subprocess.run([sys.executable, str(REPO / "scripts" / "sop.py"), "validate"],
                             capture_output=True, text=True,
                             env=os.environ | {"CLAUDE_SOPS_DIR": str(root / "sops")})
        if run.returncode:
            fails += [f"sops: {l}" for l in run.stdout.strip().splitlines()]
    git = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                         capture_output=True, text=True)
    if git.returncode:
        warns.append(f"{tilde(root)} is not a git repo, so it doesn't sync or keep history")
    elif git.stdout.strip():
        warns.append(f"{tilde(root)} has uncommitted changes")
    lib = {h["id"]: h for h in load(LIBRARY, active_only=False)}
    for h in habits:
        src = lib.get(h.get("library", ""))
        if src and version_of(src) > h.get("library_version", ""):
            warns.append(f"{h['id']}: library has a newer version ({version_of(src)}); see `outdated`")
    return fails, warns


def check_context(target, root: Path):
    fails, warns = [], []
    target = Path(target).expanduser()
    if not target.exists():
        return [f"{target} does not exist"], warns
    text = target.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        fails.append(f"expected one {BEGIN} block, found {text.count(BEGIN)}")
    for b, _ in LEGACY:
        if b in text:
            fails.append(f"legacy block {b} still present; run install --write")
    if fails:
        return fails, warns
    block = text.partition(BEGIN)[2].partition(END)[0]
    outside = text.replace(BEGIN + block + END, "")
    for heading in ("Habits", "Procedures", "Standard operating procedures"):
        if re.search(rf"^#{{1,3}} {heading}\s*$", outside, re.M):
            fails.append(f"a hand-written '## {heading}' heading exists outside the block")
    if "## Procedures" not in block:
        fails.append("block is inline mode or predates SOPs; reinstall in index mode")
        return fails, warns
    if len(block) > BLOCK_BUDGET:
        fails.append(f"block is {len(block)} chars, budget {BLOCK_BUDGET}")
    try:
        p = plan_install(target, root)
    except ValueError as exc:
        return fails + [str(exc)], warns
    if p["action"] != "unchanged":
        fails.append("block is stale against the habit and SOP files; run install --write")
    idx = root / "habits" / "index.json"
    if not idx.exists():
        fails.append(f"{tilde(idx)} missing; run `habits.py index`")
    return fails, warns


def cmd_check(a):
    root = user_root(a.root)
    report = {}
    if a.what in ("library", "all"):
        report["library"] = dict(zip(("fail", "warn"), check_library()))
    if a.what in ("source", "all"):
        report["source"] = dict(zip(("fail", "warn"), check_source(root)))
    if a.what in ("context", "all"):
        report["context"] = dict(zip(("fail", "warn"), check_context(a.target, root)))
    ok = not any(r["fail"] for r in report.values())
    if a.json:
        print(json.dumps(report | {"ok": ok}, indent=2))
    else:
        for name, r in report.items():
            print(f"{name}: {'FAIL' if r['fail'] else 'ok'}")
            print("".join(f"  fail: {f}\n" for f in r["fail"]) +
                  "".join(f"  warn: {w}\n" for w in r["warn"]), end="")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", help="user-data root (default $CLAUDE_USER_DATA or ~/.claude-user-data)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("path").set_defaults(func=cmd_path)
    p = sub.add_parser("list"); p.set_defaults(func=cmd_list)
    p.add_argument("--library", action="store_true"); p.add_argument("--all", action="store_true")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("adopt"); p.set_defaults(func=cmd_adopt)
    p.add_argument("id"); p.add_argument("--set", action="append", default=[], metavar="NAME=VALUE")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("outdated"); p.set_defaults(func=cmd_outdated)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("validate"); p.set_defaults(func=cmd_validate)
    p.add_argument("--library", action="store_true")
    p = sub.add_parser("index"); p.set_defaults(func=cmd_index)
    p.add_argument("--library", action="store_true")
    target = str(Path.home() / "CLAUDE.md")
    p = sub.add_parser("install"); p.set_defaults(func=cmd_install)
    p.add_argument("--target", default=target)
    p.add_argument("--mode", choices=("index", "inline"), default="index")
    p.add_argument("--only", default="")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("check"); p.set_defaults(func=cmd_check)
    p.add_argument("what", nargs="?", choices=("library", "source", "context", "all"), default="all")
    p.add_argument("--target", default=target)
    p.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        a.func(a)
    except ValueError as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()

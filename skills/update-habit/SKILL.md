---
name: update-habit
description: Revise an existing habit in Habits-Of-Claude — change its rule, summary, exceptions or tunable values — then rebuild, reinstall and push. Use when the user corrects how a standing habit should work, sharpens or loosens one, or says a habit's one-line summary misleads.
---

# Update a habit

Work in the Habits-Of-Claude clone. With `${CLAUDE_PLUGIN_ROOT}` unset, its path is
`source_repo` in `~/.config/agent-habits/index.json`; failing that, clone
`danielrosehill/Habits-Of-Claude`. `git pull` first.

## Find the right file

`python3 scripts/list.py` shows every active habit with its summary. If the change
the user describes fits none of them, it is a new habit: use `add-habit`. If it fits
two, it belongs in one; say which, and why.

## Edit `habits/<id>.md`

- **`## Snippet`** is the full rule, read on demand from the habits folder. Second
  person, standalone, no reference to this repo or the conversation.
- **`summary:`** is the one line that sits in every session's `~/CLAUDE.md`. It
  must carry the rule by itself, including any carve-out an agent would otherwise
  over-apply. If the snippet's rule changed, the summary almost certainly must too.
  Keep it under 320 characters; `assemble.py` enforces that.
- **`## Why`** gets a sentence on what changed and why, dated. A habit whose
  rationale is lost can only be obeyed, not judged.
- Add `revised: YYYY-MM-DD`. Don't touch `added`.
- A changed tunable *value* for this machine is not an edit: run
  `install.py --set NAME=VALUE --write`. Edit the frontmatter default only when the
  default itself should change for everyone.

Prefer the user's wording to a paraphrase. A blunter or more concrete phrasing they
gave is usually the point of the correction.

## Apply

```bash
python3 scripts/assemble.py
python3 scripts/install.py            # dry run: check the summary line diff
python3 scripts/install.py --write
python3 scripts/check.py              # source + context must both be ok
git add habits assembled && git commit -m "<id>: <what changed>" && git push
```

Changes reach new sessions, not the running one. Say so.

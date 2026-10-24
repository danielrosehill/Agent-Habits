---
name: remove-habit
description: Retire a habit from Habits-Of-Claude so it stops being installed, or delete it outright when explicitly asked — then rebuild, reinstall and push. Use when the user says to drop, remove, delete, retire or stop applying a habit.
---

# Remove a habit

Work in the Habits-Of-Claude clone. With `${CLAUDE_PLUGIN_ROOT}` unset, its path is
`source_repo` in `~/.config/agent-habits/index.json`; failing that, clone
`danielrosehill/Habits-Of-Claude`. `git pull` first.

## Retire by default

"Drop it", "remove it", "stop doing that" mean retire:

1. In `habits/<id>.md` set `status: retired` and add `revised: YYYY-MM-DD`.
2. In `## Why`, add a dated line saying why it was dropped. A retired habit records
   a position that was considered and rejected; that is worth keeping.
3. Other active habits that list it in `related:` should drop the reference.
   `check.py source` warns about any that still do.

Retired habits stay in `assembled/habits.json` with their status, are left out of
`assembled/habits.md`, and are never installed. `install.py --write` removes the
habit's file from the habits folder and its line from `~/CLAUDE.md`.

## Delete only on an explicit request

If the user says to delete the file, or the habit was a mistake with nothing worth
recording, `git rm habits/<id>.md` and remove every `related:` reference to it, since
`assemble.py` fails on a dangling one. Git history still holds it.

## Apply

```bash
python3 scripts/assemble.py
python3 scripts/install.py --write
python3 scripts/check.py
git add -A habits assembled && git commit -m "Retire <id>: <reason>" && git push
```

If prose elsewhere in `~/CLAUDE.md` restates the removed habit, say so. Removing it
is the user's call, through `reconcile-habits`.

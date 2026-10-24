---
name: remove-habit
description: Retire one of your habits so it stops being installed, or delete it outright when explicitly asked — then reinstall the CLAUDE.md block and sync. Use when the user says to drop, remove, delete, retire or stop applying a habit.
---

# Remove a habit

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

## Retire by default

"Drop it", "remove it" and "stop doing that" mean retire:

1. In `habits/<id>.md`, set `status: retired` and `revised: YYYY-MM-DD`.
2. Add a dated line to `## Why` saying why. A retired habit records a position that
   was considered and dropped.
3. Remove it from other habits' `related:` lists. `check` warns about any left.

Retired habits stay in `index.json` and are never installed.

## Delete only when asked explicitly

If the user says to delete the file: `git -C ~/.claude-user-data rm habits/<id>.md`,
and remove every `related:` reference to it, since `validate` fails on a dangling
one.

## Apply

```bash
python3 "$PLUGIN/scripts/habits.py" validate
python3 "$PLUGIN/scripts/habits.py" install            # dry run: check the changed line
python3 "$PLUGIN/scripts/habits.py" install --write
python3 "$PLUGIN/scripts/habits.py" check
```

Then commit with `sync`. Changes reach new sessions, not the running one. Say so.

If prose elsewhere in CLAUDE.md restates the removed habit, point it out. Removing
that prose is the user's call; use `reconcile-habits`.

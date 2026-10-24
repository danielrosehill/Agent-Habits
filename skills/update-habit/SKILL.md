---
name: update-habit
description: Revise one of your habits — its rule, summary, trigger, exceptions or values — then reinstall the CLAUDE.md block and sync. Use when the user corrects how a standing habit should work, sharpens or loosens one, or says a habit's one-line summary misleads. Also for pulling in a newer library version of an adopted habit.
---

# Update a habit

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

`habits.py list` shows each habit with its summary. If the change fits none of
them, use `add-habit`. If it fits two, it belongs in one; say which.

## Edit `~/.claude-user-data/habits/<id>.md`

- If the rule in `## Snippet` changed, the `summary` almost certainly has to
  change too, since it's what every session sees. Keep the main exception in it.
- Add a dated line to `## Why` saying what changed and why.
- Set `revised: YYYY-MM-DD` and leave `added` alone.
- Prefer the user's wording. A blunter or more concrete phrasing they gave is
  usually the point of the correction.

## A newer library version

`habits.py outdated` lists adopted habits whose library copy has been revised since
the adoption. Diff the two files and show the user the differences. Then either:

- merge by hand, keeping the user's local edits, and set `library_version` to the
  library's `revised` date; or
- `habits.py adopt <id> --force [--set NAME=VALUE]`, which replaces the file
  wholesale and loses local edits. Only do this if they say so.

## Apply

```bash
python3 "$PLUGIN/scripts/habits.py" validate
python3 "$PLUGIN/scripts/habits.py" install            # dry run: check the changed line
python3 "$PLUGIN/scripts/habits.py" install --write
python3 "$PLUGIN/scripts/habits.py" check
```

Then commit with `sync`. Changes reach new sessions, not the running one. Say so.

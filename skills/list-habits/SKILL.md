---
name: list-habits
description: List your habits — ids and one-line rules, optionally retired ones — or the example library you can adopt from, or find which habit covers something. Use when asked "what are my habits", "list habits", "what habits are available", "which habit covers X", or before deciding whether something is already a habit.
---

# List habits

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

```bash
python3 "$PLUGIN/scripts/habits.py" list              # yours, active
python3 "$PLUGIN/scripts/habits.py" list --all        # including retired
python3 "$PLUGIN/scripts/habits.py" list --library    # the examples you can adopt
python3 "$PLUGIN/scripts/habits.py" list --json
```

Without the plugin clone, `~/.claude-user-data/habits/index.json` holds the same
list for the user's own habits. SOPs are listed with `sop-list`.

Answer with the list: id and one line each, with a habit's trigger if it has one.
For "which habit covers X", name the habit and quote the relevant sentence of its
snippet. If none covers it, say so, and say whether it would be a habit or an SOP
([`references/habit-or-sop.md`](../../references/habit-or-sop.md)).

When listing the library for someone choosing what to adopt, mark the ones they
already have, and flag any whose library version is newer (`habits.py outdated`).

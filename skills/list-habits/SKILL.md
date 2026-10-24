---
name: list-habits
description: List the user's standing habits (Habits-Of-Claude) — ids, one-line rules, and optionally retired ones or the full text of one. Use when asked "what are my habits", "list habits", "which habit covers X", or before deciding whether something is already a habit.
---

# List habits

The fastest read needs no repo: `~/.config/agent-habits/index.json` lists every
installed habit with its id, title, stance and summary, and `<id>.md` beside it is
the full text. That is what is in force on this machine.

For the source, including retired habits, use the Habits-Of-Claude clone
(`source_repo` in that index.json, or clone `danielrosehill/Habits-Of-Claude`):

```bash
python3 scripts/list.py            # active
python3 scripts/list.py --all      # with retired
python3 scripts/list.py --json
```

If the installed folder and the repo disagree, the install is stale. Run
`context-check`.

Answer with the list itself: id and one line each. Don't add commentary on the
habits unless asked. For "which habit covers X", name the habit and quote the
relevant sentence of its snippet. If none covers it, say so, and say whether it
would qualify as a habit (see `add-habit`).

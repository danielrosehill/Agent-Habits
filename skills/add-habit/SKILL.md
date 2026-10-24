---
name: add-habit
description: Add a new habit to your own habits — a standing rule for how the agent should behave across all work, or whenever a stated trigger applies — with a one-line summary that sits in every session. Writes ~/.claude-user-data/habits/<id>.md, reinstalls the CLAUDE.md block and syncs. Use when the user states a standing preference or principle ("from now on, always…", "my preference for X is…") or corrects the agent in a way that should persist. For an ordered procedure use sop-write; to take one from the example library use adopt-habit.
---

# Add a habit

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

## Qualify it

Read [`references/habit-or-sop.md`](../../references/habit-or-sop.md). In short:

- **Steps?** Then it's an SOP. Use `sop-write`.
- **A fact about this machine?** It goes in CLAUDE.md, not here.
- **Close to an existing habit** (`habits.py list`)? Then use `update-habit`. Two
  overlapping habits will drift apart into two different rules.
- **Already in the library** (`habits.py list --library`)? Then use `adopt-habit`.

## Write `~/.claude-user-data/habits/<id>.md`

```markdown
---
id: <slug, equals the filename>
title: <short imperative title>
summary: "<the rule in one or two sentences, under 320 characters, no double quotes>"
kind: habit
trigger: "<only if it applies to one kind of task: cutting a release, …>"
stance: practice | prohibition
order: <multiple of 10; practices before prohibitions>
added: <YYYY-MM-DD>
status: active
source: "conversation, <YYYY-MM-DD>"
related: [<other habit ids>]
---

## Snippet

## Why
```

- **`## Snippet`** is the full rule, read on demand. It is addressed to the agent,
  stands alone, and says nothing about the conversation it came from. State any
  exception explicitly. A rule with no carve-out gets over-applied.
- **`summary`** is the only part every session sees, so it must carry the rule and
  its main exception by itself. Write the snippet first, then compress it.
- **`trigger`** describes the circumstance, not the action ("cutting a release",
  not "versioning"). Leave it out for a rule that holds on every task.
- **`## Why`** holds the reasoning and the cost of getting it wrong. It is what
  lets the habit be judged later instead of just obeyed.
- Prefer the user's own wording to a paraphrase.

## Apply

```bash
python3 "$PLUGIN/scripts/habits.py" validate
python3 "$PLUGIN/scripts/habits.py" install            # dry run: check the changed line
python3 "$PLUGIN/scripts/habits.py" install --write
python3 "$PLUGIN/scripts/habits.py" check
```

Then commit with `sync`. Changes reach new sessions, not the running one. Say so.

If the habit is generic enough that others might want it, offer `share-habit`.

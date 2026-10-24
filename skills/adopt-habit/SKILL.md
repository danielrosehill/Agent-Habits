---
name: adopt-habit
description: Adopt a habit from the example library into your own habits — copies it to ~/.claude-user-data/habits/, fills in tunable values such as a spend limit, records which library version it came from, then reinstalls the CLAUDE.md block. Use when the user wants one of the example habits, asks "what habits could I use", or is setting up habits for the first time.
---

# Adopt a library habit

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

```bash
python3 "$PLUGIN/scripts/habits.py" list --library
```

Show the ids and summaries and let the user choose. For a choice, show the full
`library/habits/<id>.md` if they want to read it first. Adopt only what they pick.
Every adopted habit adds a line to every session.

## Values

Some library habits declare `variables:`. For example, `spend-approval-limit`
has `APPROVAL_LIMIT` (default `$5`) and `REAPPROVAL_MARGIN` (`25%`). Ask
for the user's value whenever the default is a judgement call rather than a
convention.

```bash
python3 "$PLUGIN/scripts/habits.py" adopt spend-approval-limit --set APPROVAL_LIMIT='$20'
python3 "$PLUGIN/scripts/habits.py" adopt release-versioning
```

`adopt` writes a concrete copy: values filled in, the `variables` block dropped,
`library` and `library_version` recorded. That copy is now the user's to edit
freely. `outdated` later reports when the library has revised it. It refuses to
overwrite an existing file unless given `--force`.

Read the adopted file back. The library is written in first person ("when I
ask…"), which becomes the adopting user's voice. If the user's existing CLAUDE.md
prose already covers the same ground, say so and offer `reconcile-habits`.

## Apply

```bash
python3 "$PLUGIN/scripts/habits.py" validate
python3 "$PLUGIN/scripts/habits.py" install            # dry run: check the changed line
python3 "$PLUGIN/scripts/habits.py" install --write
python3 "$PLUGIN/scripts/habits.py" check
```

Then commit with `sync`. Changes reach new sessions, not the running one. Say so.

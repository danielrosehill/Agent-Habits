---
name: context-check
description: Verify the user-level CLAUDE.md is wired correctly to your habits and SOPs — exactly one generated agent-habits block, in index mode, under its size budget, matching the current habit and SOP files, with no legacy or hand-written duplicates — and repair drift by reinstalling. Use when asked to "check the context", after adding or removing habits or SOPs, after hand-editing CLAUDE.md, after a pull on another machine, or when a habit seems not to be in force.
---

# Context check

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

The intended shape is one marker-delimited block in `~/CLAUDE.md`
(`<!-- agent-habits:begin -->` … `:end -->`) with two parts:

- **`## Habits`**: one summary line per active habit. Triggered habits are grouped
  under "These apply only when their trigger does". It points at
  `~/.claude-user-data/habits/<id>.md` for the full text.
- **`## Procedures`**: one trigger line per active SOP, pointing at
  `~/.claude-user-data/sops/<id>.md`.

## Run

```bash
python3 "$PLUGIN/scripts/habits.py" check context      # --target <file>, --json
```

It fails when:

- there isn't exactly one block;
- a legacy `habits-of-claude` or `claude-sops` block remains;
- the block is in inline mode or has no `## Procedures` part;
- the block is over its 7,000-character budget;
- the block differs from what `install` would write now from the habit and SOP
  files (a habit or SOP was added, changed, retired or pulled without
  reinstalling);
- `habits/index.json` is missing;
- a hand-written `## Habits` or `## Procedures` heading sits outside the block.

## Repair

```bash
python3 "$PLUGIN/scripts/habits.py" install --write && python3 "$PLUGIN/scripts/habits.py" check context
```

That fixes staleness, legacy blocks and inline mode. Don't repair a duplicate
marker or hand-written habit prose mechanically. Show the user the text and use
`reconcile-habits`.

Over budget means too many always-on habits. Suggest giving some a `trigger`, or
retiring or merging some, rather than raising the budget.

## Also read it

The script checks structure. Read the text around the block too:

- the header should describe the block correctly;
- a behavioural directive written above it by hand belongs in a habit (offer
  `add-habit`);
- a numbered procedure written above it belongs in an SOP (offer `sop-write`).

Report pass or fail in a line or two, and what you repaired.

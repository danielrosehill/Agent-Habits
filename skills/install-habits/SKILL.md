---
name: install-habits
description: Install or update the generated agent-habits block — your habits' summary lines and SOP trigger lines — in ~/CLAUDE.md, or put full habit texts (a subset, inline) into a project CLAUDE.md or AGENTS.md that others read. Marker-delimited, idempotent, backs the file up, and leaves hand-written prose alone. Use when asked to install or refresh the habits, apply habits to another project, or after any habit or SOP change.
---

# Install the block

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

```bash
python3 "$PLUGIN/scripts/habits.py" install                 # dry run against ~/CLAUDE.md
python3 "$PLUGIN/scripts/habits.py" install --write         # backs the file up first
python3 "$PLUGIN/scripts/habits.py" check context
```

Show the dry-run diff before writing unless the user has already said to go ahead.
`--write` also regenerates `habits/index.json` and `sops/INDEX.md`.

## Modes

- **index** (default) is for user level. It writes one line per habit and per SOP,
  with pointers to `~/.claude-user-data/`. That stays around 1,000–1,500 tokens
  however long the full texts get.
- **inline** (`--mode inline`) puts the full habit snippets in the block, with no
  SOPs. It's for a project file other people read, where a path into one user's
  home means nothing:

```bash
python3 "$PLUGIN/scripts/habits.py" install --mode inline --only agent-first,verify-dont-infer --target ./CLAUDE.md --write
```

Choose the subset deliberately. Habits about working method (`agent-first`,
`verify-dont-infer`, `document-what-you-fix`) travel well into a shared project.
Habits about one person's preferences (`explain-less-do-more`,
`no-unsolicited-security-advice`) usually don't. Ask if the repo has other readers.

## Behaviour

- The installer replaces the existing block in place. Legacy `habits-of-claude` and
  `claude-sops` blocks are converted, and a second legacy block is removed.
- A marker that appears other than exactly once stops the run. Fix that by hand.
- Hand-written prose covering the same ground is left alone. Offer
  `reconcile-habits`.
- Changes take effect in new sessions, not the running one.

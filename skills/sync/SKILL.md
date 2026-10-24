---
name: sync
description: Commit and push your habits and SOPs (the ~/.claude-user-data repo), or pull them onto this machine, then reinstall the CLAUDE.md block so it matches. Use when the user asks to sync, save, push or back up habits or SOPs, when setting up a second machine, and at the end of any session that added or changed a habit or SOP.
---

# Sync habits and SOPs

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`.

`ROOT=~/.claude-user-data` (or `$CLAUDE_USER_DATA`). It's one private git repo
shared with other tools' folders.

## Push

```bash
git -C "$ROOT" status --short
python3 "$PLUGIN/scripts/habits.py" check source      # validates habits and SOPs
python3 "$PLUGIN/scripts/habits.py" index             # habits/index.json + sops/INDEX.md
git -C "$ROOT" add -- habits sops
git -C "$ROOT" commit -m "<what changed>"
git -C "$ROOT" push
```

Stage `habits` and `sops` only, never `-A`. Other tools keep half-finished work
in their own folders. If `status` shows changes outside these two folders, mention
them and leave them alone.

Validate before pushing. A broken file propagates to every machine. Write a real
commit message, such as "Add habit release-versioning" or "SOP close-the-month:
new step 4".

## Pull

```bash
git -C "$ROOT" pull --ff-only
python3 "$PLUGIN/scripts/habits.py" check source
python3 "$PLUGIN/scripts/habits.py" install --write   # the block must match what was pulled
```

`--ff-only` on purpose: a merge here means two machines edited the same file, and
that needs a human eye.

## Conflicts

- **`habits/index.json` or `sops/INDEX.md`**: these are generated. Take either
  side, run `habits.py index`, then add the file again.
- **A habit or SOP**: show both versions of the conflicting part and ask. If two
  versions of one SOP have genuinely grown apart, split them under two ids.

## No remote yet

That's fine. Offer it once per session, show the `gh repo create --private` command
from `setup`, and don't ask again.

## Report

Say how many files changed, which ids, and whether the push succeeded. If nothing
changed, say so in one line.

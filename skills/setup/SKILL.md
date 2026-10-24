---
name: setup
description: First-time setup of Agent-Habits — create the private user-data folder for your own habits and SOPs, optionally adopt habits from the library, put it under git with a private remote, and add the one generated block to the user-level CLAUDE.md. Also covers a second machine (clone the existing user-data repo) and moving the folder. Use when the user wants to start keeping habits or SOPs, when another skill finds no habits or sops folder, or when mirroring them to another machine.
---

# Set up habits and SOPs

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`.

Layout:

| What | Where | Lifecycle |
|---|---|---|
| Plugin: scripts, skills, schemas, and the public example library | `$PLUGIN`, with `library/habits/` and `library/sops/` | replaced on update; public |
| Your habits | `~/.claude-user-data/habits/<id>.md` | yours; private git |
| Your SOPs | `~/.claude-user-data/sops/<id>.md` | yours; private git |
| Local config | `~/.claude-plugins/habits/config.json` | never committed |
| The CLAUDE.md block | between `<!-- agent-habits:begin -->` and `:end -->` | generated; never hand-edit |

`$CLAUDE_USER_DATA` overrides `~/.claude-user-data`. Why the paths are what they
are: [`references/user-data-convention.md`](../../references/user-data-convention.md).
Never put user content under `~/.claude`.

## 0. Check what exists

```bash
python3 "$PLUGIN/scripts/habits.py" path
git -C ~/.claude-user-data rev-parse --show-toplevel   # fails if it isn't a repo
```

If `habits/` or `sops/` already hold `.md` files, don't re-initialise. Say what
you found and ask what the user actually wanted. The usual real cases are a second
machine (step 2b) or a move (below).

## 1. Create the folders

```bash
mkdir -p ~/.claude-user-data/habits
python3 "$PLUGIN/scripts/sop.py" init        # sops/, archive/, README.md, INDEX.md
```

Then offer the library: `python3 "$PLUGIN/scripts/habits.py" list --library`.
Show the ids and their one-line summaries, and let the user pick. Adopt each pick
with `adopt-habit`. Don't adopt the whole library unasked, because every habit
costs a line in every session.

## 2. Git, and a private remote

The repo is `~/.claude-user-data`, not a subfolder. It is the mirror point for every
tool that follows the convention.

```bash
git -C ~/.claude-user-data init
git -C ~/.claude-user-data add -- habits sops
git -C ~/.claude-user-data commit -m "Start habits and SOPs"
```

The remote creates something outward-facing, so show the command and get a yes:

```bash
gh repo create <name> --private --source="$HOME/.claude-user-data" --push
```

Always private: SOPs name real hosts, accounts and people. No `gh`? Leave the local
repo in place. It works fully without a remote.

**2b. Second machine:** `gh repo clone <owner>/<name> ~/.claude-user-data`, then step 3.

## 3. Install the block

```bash
python3 "$PLUGIN/scripts/habits.py" install            # dry run: show the user the block
python3 "$PLUGIN/scripts/habits.py" install --write    # backs CLAUDE.md up first
python3 "$PLUGIN/scripts/habits.py" check
```

`--target` picks the file; the default is `~/CLAUDE.md`. Show the dry run and ask
before writing, because this file governs every future session. The installer
replaces any legacy `habits-of-claude` or `claude-sops` block, so there is only
ever one.

## Moving the folder

Move it with `git mv` inside the repo, record the new location as `library` in
`~/.claude-plugins/habits/config.json` (SOPs), or set `$CLAUDE_USER_DATA` (both),
then reinstall. A stale block after a move points every session at an empty folder,
and an empty folder looks the same as having no habits.

## Finish

List what exists now: the paths, whether there is a remote, and how many habits and
SOPs there are. Then offer to write the first SOP if the session that led here
worked out a procedure.

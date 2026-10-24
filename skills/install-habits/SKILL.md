---
name: install-habits
description: Install or update the Habits-Of-Claude block in a system prompt file — all habits or a named subset — into ~/CLAUDE.md, a project CLAUDE.md, or AGENTS.md. User level uses index mode (one summary line per habit in the prompt, full texts in ~/.config/agent-habits/); shared project files use inline mode. Writes a marker-delimited managed region so re-running is idempotent and hand-written prose is left untouched. Use when asked to install the habits, add a specific habit snippet somewhere, push habit edits out to a system prompt, or apply the habits to another project.
---

# Install habits into a system prompt

Work in the Habits-Of-Claude clone. With `${CLAUDE_PLUGIN_ROOT}` unset, its path is
`source_repo` in `~/.config/agent-habits/index.json`; failing that, clone
`danielrosehill/Habits-Of-Claude`.

The habits are the source; a system prompt is a build target. Never hand-edit the
installed block — edit `habits/*.md`, regenerate, reinstall.

## Sequence

```bash
python3 scripts/assemble.py                    # habits/*.md -> assembled/
python3 scripts/install.py                     # dry run against ~/CLAUDE.md
python3 scripts/install.py --write             # apply, backing the target up first
python3 scripts/check.py context               # verify
```

## Modes

- **index** (default): the block holds one line per habit, `**Title** (`id`): summary`,
  and points at the habits folder. The full snippets are written to
  `~/.config/agent-habits/<id>.md` with an `index.json`. This keeps the always-loaded
  prompt around 1,000 tokens. `--habits-dir` picks another folder, and the choice
  is recorded in the block so later reinstalls reuse it.
- **inline** (`--mode inline`): full snippets in the block. Use it for a project
  file other people read, where a path into one user's home means nothing.

`assemble.py` first, always — `install.py` reads `assembled/habits.json`, so skipping
it silently installs the previous generation.

Show the user the dry-run diff before writing unless they have already said to go
ahead. `--write` makes a timestamped `.bak-<stamp>` copy of the target.

## Installing a subset

For a project CLAUDE.md, or when the user wants one specific snippet rather than the
whole set:

```bash
python3 scripts/install.py --mode inline --only agent-first,verify-dont-infer --target ./CLAUDE.md --write
```

Unknown or retired ids are rejected rather than silently skipped. With `--only`, the
folder is not pruned, so a subset install never deletes the user-level files. Habit ids are the filenames in
`habits/`; `assembled/habits.json` has them with titles and stances if you need to
pick.

Choosing a subset is a judgement call worth making deliberately. Habits that are
about *this* user's preferences (`no-unsolicited-security-advice`,
`explain-less-do-more`, `ship-without-asking`) belong at user level. Habits about
working method (`document-what-you-fix`, `agent-first`, `verify-dont-infer`) travel
fine into a shared project prompt. Ask which they want if the target is a repo other
people read.

## What it will not do

It will not remove existing hand-written prose that covers the same ground as a habit
— that is a content decision, not a mechanical one, so the block gets added and the
duplication is left in place. If the target already has sections saying the same
thing in the user's own words, say so and offer `reconcile-habits`.

## After installing at user level

Changes to `~/CLAUDE.md` take effect in new sessions, not the running one. Say that
rather than implying the habits are live immediately.

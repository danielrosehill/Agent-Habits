---
name: add-habit
description: Add a new habit to Habits-Of-Claude — writes habits/<id>.md with frontmatter, one-line summary, snippet and rationale, then rebuilds, installs into ~/CLAUDE.md and the habits folder, and pushes. Use when the user states a standing preference or principle that should hold across all work and projects ("from now on, always…", "my preference for X is…"), or corrects the agent in a way that should persist.
---

# Add a habit

Work in the Habits-Of-Claude clone. With `${CLAUDE_PLUGIN_ROOT}` unset, its path is
`source_repo` in `~/.config/agent-habits/index.json`; failing that, clone
`danielrosehill/Habits-Of-Claude`. `git pull` first. To change an existing habit use
`update-habit`, and to drop one use `remove-habit`.

## Qualify it first

A habit is a principle that should be in force before the task is known, in any
repository, on any machine. Three things it is not:

- **Environment configuration** — which server fronts a tool, what a hostname means,
  which package manager this machine uses. Belongs in `~/CLAUDE.md`.
- **A workflow** — an ordered procedure for a specific job. Belongs in a skill.
- **A one-off correction** — a preference about the task at hand, not about all work.

The test in the repo README: if it would still be true working on someone else's
machine, on an unfamiliar codebase, it is a habit.

If what the user said is close to an existing habit (`python3 scripts/list.py`),
revise that file with `update-habit` rather than adding a near-duplicate. Two habits that overlap will eventually contradict.

## Write the file

`habits/<id>.md`, where `<id>` matches the filename exactly — `assemble.py` enforces
this. Imperative slug, no numbering in the name; order is a frontmatter field.

```markdown
---
id: <slug>
title: <short imperative title>
summary: "<the rule in one or two sentences, under 320 characters>"
stance: practice | prohibition
order: <multiple of 10, leaving gaps>
added: <absolute date, YYYY-MM-DD>
status: active
source: "where this came from — a CLAUDE.md section, or a conversation with its date"
related: [<other habit ids>]
---

## Snippet

## Why
```

`## Snippet` is addressed to the agent in the second person and is what lands in a
system prompt — so it must stand alone, with no reference to this repo, to "the user's
preference", or to the conversation it came from. Write the rule and what it means in
practice, not the argument for it.

`summary` is the line that sits in every session's `~/CLAUDE.md`; the snippet is only
read on demand. So the summary must carry the rule on its own, including the main
exception. Write the snippet first, then compress it. No double quotes inside it.

`## Why` is the argument, addressed to the user, and is excluded from the assembled
output. Put the reasoning and the cost of getting it wrong here. It is what makes the
habit revisable in a year instead of merely inherited — a habit whose rationale is
lost cannot be judged, only obeyed.

State the exception explicitly where one exists. A prohibition with no carve-out gets
over-applied: `ship-without-asking` had to say that deletion and outward-facing
actions are excluded, or it would read as licence to push anything anywhere.

If the habit has a value a user would reasonably tune, such as a threshold, a limit
or a count, don't hard-code it. Declare it under `variables:` in the frontmatter
(`NAME: "default"  # meaning`) and write `{{NAME}}` in the snippet. State the value
once, prominently, near the top of the snippet, so the agent reading the prompt sees
the number in force. Users override it with `install.py --set NAME=VALUE`.

`order`: practices before prohibitions, documentation habits first. Use multiples of
ten so a habit can be inserted later without renumbering.

## Then apply

```bash
python3 scripts/assemble.py          # validates; exits non-zero on a broken habit
python3 scripts/install.py --write   # ~/CLAUDE.md line + ~/.config/agent-habits/<id>.md
python3 scripts/check.py             # source + context must both be ok
git add habits assembled && git commit -m "Add habit <id>: <one line>" && git push
```

`assemble.py` validates frontmatter, that `id` matches the filename, `stance` and
`status` values, the summary, variables, and that every `related` id resolves. Add
the habit to the table in `README.md` in the same commit.

Changes reach new sessions, not the running one. Say so.

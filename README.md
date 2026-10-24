[![Claude Code Repos Index](https://img.shields.io/badge/Claude%20Code%20Repos-Index-blue?style=flat-square&logo=github)](https://github.com/danielrosehill/Claude-Code-Repos-Index)

# Agent-Habits

Your standing instructions for an AI agent, kept as one markdown file each, with a
small generated block in your system prompt (`CLAUDE.md`, `AGENTS.md`) that points
at them. There are two kinds:

- **Habits:** rules for how the agent behaves, in force before the task is known.
  "Check the thing itself, not a status code that stands in for it." "Release tags
  are `v1.000`, `v1.001`, …"
- **SOPs:** procedures for one recurring job, followed when their trigger matches.
  "To publish a package: …"

The plugin (name `habits`) is the machinery plus a **library of example habits**
you can adopt. Your own habits and SOPs live in a private folder you own and never
enter this repo.

This repo was previously `Habits-Of-Claude`. The SOP half was previously the
separate `Claude-SOPs` plugin (`sop-library`), merged in on 2026-10-24.

## Habit or SOP?

Ask whether it is a rule or a sequence of steps, not whether it applies always or
sometimes. A rule that only matters for one kind of task is a habit with a
`trigger`. Anything with numbered steps is an SOP. Full test, edge cases and what is
neither: [`references/habit-or-sop.md`](references/habit-or-sop.md).

## Why it costs so little context

```
~/CLAUDE.md                          one generated block:
  ## Habits                            one summary line per habit (triggered ones grouped)
  ## Procedures                        one trigger line per SOP
        │
        ▼  read only when relevant
~/.claude-user-data/habits/<id>.md   full rule, exceptions, rationale
~/.claude-user-data/sops/<id>.md     full procedure
```

Inlining the full texts of 14 habits cost ~18,500 characters (~4,600 tokens) in
every session. The index block for the same 14 is ~4,500 characters. Each SOP adds
one line. `check context` enforces a 7,000-character budget.

## Three places, three lifecycles

| What | Where | Visibility |
|---|---|---|
| Machinery: `scripts/`, `skills/`, `schema/`, `references/`, `templates/` | this repo | public |
| Example library: `library/habits/` (with `{{VARIABLES}}`), `library/sops/` | this repo | public |
| Your habits and SOPs | `~/.claude-user-data/habits/`, `~/.claude-user-data/sops/` | one private git repo at `~/.claude-user-data` |
| Local config | `~/.claude-plugins/habits/config.json` | never committed |

`$CLAUDE_USER_DATA` overrides `~/.claude-user-data`. Never put user content under
`~/.claude`. See [`references/user-data-convention.md`](references/user-data-convention.md).

## Quick start

```bash
python3 scripts/habits.py list --library                         # browse the examples
python3 scripts/habits.py adopt verify-dont-infer
python3 scripts/habits.py adopt spend-approval-limit --set APPROVAL_LIMIT='$20'
python3 scripts/sop.py init                                      # ~/.claude-user-data/sops
python3 scripts/habits.py install                                # dry run against ~/CLAUDE.md
python3 scripts/habits.py install --write
python3 scripts/habits.py check                                  # library + source + context
```

Or just say what you want. The `setup` skill walks through all of this, including the
private remote.

## The library

Each is first person ("when I ask…"), so after adoption it reads as your own
prompt. `adopt` fills in variables, records `library` and `library_version`, and
`outdated` reports when the library has since revised one.

| Habit | Stance | In one line |
|---|---|---|
| [`document-as-you-go`](library/habits/document-as-you-go.md) | practice | What you learned is an output of the work; capture it unasked |
| [`document-what-you-fix`](library/habits/document-what-you-fix.md) | practice | A fix is not finished when it works |
| [`agent-first`](library/habits/agent-first.md) | practice | The next reader is an agent with no memory of this session |
| [`verify-dont-infer`](library/habits/verify-dont-infer.md) | practice | Check the thing itself, not a signal that stands in for it |
| [`escalate-before-declaring-failure`](library/habits/escalate-before-declaring-failure.md) | practice | One blocked route is not a dead end |
| [`own-capabilities-first`](library/habits/own-capabilities-first.md) | practice | Built-in beats external unless told or known otherwise |
| [`one-subject-one-repo`](library/habits/one-subject-one-repo.md) | practice | Knowledge gets its own home, at maximum specificity |
| [`skill-or-not`](library/habits/skill-or-not.md) | practice | Before a task, ask whether it should become a skill |
| [`ship-without-asking`](library/habits/ship-without-asking.md) | practice | Finished means deployed, not committed |
| [`release-versioning`](library/habits/release-versioning.md) | practice, triggered | Releases are `v1.000`, `v1.001`, … — not semver |
| [`parallelise-without-asking`](library/habits/parallelise-without-asking.md) | practice | Spawn the agent, don't propose it |
| [`spend-approval-limit`](library/habits/spend-approval-limit.md) | practice | Spend freely below a set limit; estimate and ask above it |
| [`explain-less-do-more`](library/habits/explain-less-do-more.md) | prohibition | Do the work; instruct only when asked to |
| [`no-unsolicited-security-advice`](library/habits/no-unsolicited-security-advice.md) | prohibition | My environment, my risk calculus, not yours |

Example SOPs: [`publish-a-package`](library/sops/publish-a-package.md),
[`set-up-a-new-machine`](library/sops/set-up-a-new-machine.md). These are invented
examples of the format. Real SOPs name real hosts and accounts and stay private.

`library/habits/index.json` is the same list for an agent, generated by
`habits.py index --library`.

## Skills

The plugin is reached through a skill catalogue rather than installed, so
`${CLAUDE_PLUGIN_ROOT}` may be unset. Every skill resolves `$PLUGIN` to that, else
to `plugin_repo` recorded in `~/.claude-user-data/habits/index.json`, else a fresh
clone.

| Skill | For |
|---|---|
| `setup` | First run, second machine, moving the folder |
| `sync` | Commit and push or pull `~/.claude-user-data`, then reinstall |
| `adopt-habit` | Take a habit from the library, filling in its values |
| `add-habit` | Write a new habit of your own |
| `update-habit` | Revise a habit, or merge a newer library version |
| `remove-habit` | Retire (default) or delete a habit |
| `list-habits` | Your habits, the library, or "which habit covers X" |
| `share-habit` | Depersonalise one of yours into the public library (maintainer) |
| `sop-write`, `sop-edit`, `sop-remove`, `sop-list`, `sop-run` | Write, change, retire, review and follow SOPs |
| `check-habits` | Validate habits and SOPs: parse, summary fidelity, overlap, wrong kind |
| `context-check` | Verify the CLAUDE.md block is single, current and in budget; repair |
| `install-habits` | Install the block; inline mode for shared project files |
| `reconcile-habits` | Hand-written prompt prose versus the files |

`/sop` (in `commands/`) dispatches to the SOP skills.

## File formats

**Habit**, `<id>.md`:

```markdown
---
id: release-versioning            # equals the filename
title: Number releases vMAJOR.NNN
summary: "<the rule plus its main exception; ≤320 chars; this line is always in context>"
kind: habit
trigger: "cutting a release, creating a tag, or bumping a version"   # optional
stance: practice | prohibition
order: 72                         # multiples of 10; practices before prohibitions
added: 2026-10-24
revised: 2026-10-24               # once edited; the library's version marker
status: active | retired
source: "conversation, 2026-10-24"
related: [ship-without-asking]
library: release-versioning       # set by adopt
library_version: 2026-10-24       # set by adopt
variables:                        # library only; adopt renders them
  NAME: "default"   # meaning
---

## Snippet
<the full rule, addressed to the agent, standalone>

## Why
<the rationale: what it prevents, what changed>
```

**SOP**: [`references/sop-format.md`](references/sop-format.md), with schema
[`schema/sop.schema.json`](schema/sop.schema.json).

## Scripts

- **`scripts/habits.py`**: `path`, `list`, `adopt`, `outdated`, `validate`, `index`,
  `install`, `check`. `--root` goes before the subcommand.
- **`scripts/sop.py`**: `init`, `new`, `list`, `show`, `index`, `validate`, `retire`.
  It resolves its folder from `$CLAUDE_SOPS_DIR`, then
  `~/.claude-plugins/habits/config.json`, then `$CLAUDE_USER_DATA/sops`.

Both use the standard library only, so no venv is needed.

`install` is dry-run by default and backs the target up on `--write`. It converts
legacy `habits-of-claude` and `claude-sops` blocks into the single
`<!-- agent-habits:begin/end -->` block. `--mode inline --only a,b` writes full
snippets instead, for a project file other people read.

Design notes from the SOP side: [`docs/sop-design-notes.md`](docs/sop-design-notes.md).

## What does not belong here

Facts about a particular machine or account, such as which server fronts which
tool, what a hostname means, or that Python uses `uv`. Those are environment
configuration, not habits, and they stay in `CLAUDE.md` and its reference files.
The test: would it still be true on someone else's machine, in an unfamiliar
codebase?

## Relation to Document-As-You-Go

[`Document-As-You-Go`](https://github.com/danielrosehill/Document-As-You-Go) was the
first pass at this idea: one habit developed on its own, with a slash command for
retroactive sweeps. The insight that came out of it was never one instruction.
Standing dispositions are the useful unit.

---

For more Claude Code projects, visit my [Claude Code Repos Index](https://github.com/danielrosehill/Claude-Code-Repos-Index).

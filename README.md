[![Claude Code Repos Index](https://img.shields.io/badge/Claude%20Code%20Repos-Index-blue?style=flat-square&logo=github)](https://github.com/danielrosehill/Claude-Code-Repos-Index)

# Habits Of Claude

Standing habits for an AI coding agent, one file per habit, installed into a
user-level system prompt (`~/CLAUDE.md`, `AGENTS.md`) as a short index that points at
a folder of the full texts. Also packaged as an agent-skills plugin, `habits`.

The unit here is the **habit**: a principle that should hold across every piece of
work, in every repository, public or private, regardless of the task in front of it.
Not a workflow, not a skill, not a tool preference — a disposition that ought to be
in force before the task is known.

## Why one file per habit

A system prompt written as one continuous document gets edited by accretion and is
hard to reason about. Split into habits it becomes maintainable: each has a single
subject, its own history, and can be revised, retired or lifted into another
project's instructions without disturbing the rest. New habits are added as files
rather than as paragraphs wedged into an existing section.

The assembled system-prompt block is generated, never hand-edited:

```bash
python3 scripts/assemble.py      # writes assembled/habits.md and assembled/habits.json
```

`assembled/habits.md` is the block to paste. `assembled/habits.json` is the same content
structured for an agent reading this repository programmatically — see the
`agent-first` habit for why that exists.

## Installing

`~/CLAUDE.md` is a build target, not a place to hand-edit habits. The installer
maintains a marker-delimited region and leaves everything around it alone:

```bash
python3 scripts/install.py                     # dry run — prints the diff
python3 scripts/install.py --write             # backs the target up first
python3 scripts/check.py                       # validate source and installed context
python3 scripts/install.py --mode inline --only agent-first,verify-dont-infer --target ./CLAUDE.md --write
python3 scripts/install.py --set APPROVAL_LIMIT='$20' --write   # tune a habit variable
```

### Index mode (default) and inline mode

Inlining every snippet put ~18,500 characters (~4,600 tokens) into every session.
Since 2026-10-24 the default is **index mode**:

- The prompt's block holds one line per active habit: `**Title** (`id`): summary`,
  taken from the habit's `summary:` frontmatter, about 4,200 characters for 14 habits.
- The full snippets go to `~/.config/agent-habits/<id>.md`, plus an `index.json`
  that lists them and records `source_repo` (this clone's path), so a skill can
  find the repo from the installed folder. The folder is vendor-neutral on purpose,
  so any agent can read it, not only Claude Code.
- The agent reads a habit's file when a task falls squarely under it. The summary
  line is the rule that is always in force, so it must carry the main exception
  itself.

`--habits-dir` picks another folder. The choice is recorded in the block as
`<!-- habits-of-claude:dir … -->` and reused on reinstall. Generated files carry a
`<!-- habits-of-claude:generated` header. Only those are pruned when a habit is
retired, and `--only` never prunes.

`--mode inline` writes full snippets into the block, as before. Use it for project
files other people read, where a path into one user's home means nothing.

`scripts/check.py context` verifies the wiring: one block, index mode, under a
6,000-character budget, a line for every active habit, and a folder matching what
`install.py` would write now. It exits 1 on any failure.

Some habits have values you can tune, such as the spend limit in `spend-approval-limit`.
`--set NAME=VALUE` overrides a value, and the flag can be repeated. The values used
are recorded in a comment inside the installed block, so a later reinstall without
`--set` keeps them. A value with no override and no recorded entry falls back to the
default in the habit's frontmatter.

Skills, in `skills/` (plugin `habits`). The plugin isn't installed; it's reached
through the skill catalogue, so `${CLAUDE_PLUGIN_ROOT}` is unset. Each skill runs
the scripts from a local clone of this repo, found through `source_repo` in
`~/.config/agent-habits/index.json`.

| Skill | For |
|---|---|
| `add-habit` | Add a habit with valid frontmatter and summary, install, push |
| `update-habit` | Revise a habit's rule, summary or default values |
| `remove-habit` | Retire a habit (default) or delete it on explicit request |
| `list-habits` | List habits, or find which one covers something |
| `check-habits` | Validate the source: build, summary fidelity, overlap, contradiction |
| `context-check` | Verify `~/CLAUDE.md` and the habits folder are wired correctly; repair |
| `install-habits` | Install or update the block — index or inline, all or a subset |
| `reconcile-habits` | Resolve drift when hand-written prompt prose and the repo disagree |

## The habits

| Habit | Stance | In one line |
|---|---|---|
| [`document-as-you-go`](habits/document-as-you-go.md) | practice | What you learned is an output of the work; capture it unasked |
| [`document-what-you-fix`](habits/document-what-you-fix.md) | practice | A fix is not finished when it works |
| [`agent-first`](habits/agent-first.md) | practice | The next reader is an agent with no memory of this session |
| [`verify-dont-infer`](habits/verify-dont-infer.md) | practice | Check the thing itself, not a signal that stands in for it |
| [`escalate-before-declaring-failure`](habits/escalate-before-declaring-failure.md) | practice | One blocked route is not a dead end |
| [`own-capabilities-first`](habits/own-capabilities-first.md) | practice | Built-in beats external unless told or known otherwise |
| [`one-subject-one-repo`](habits/one-subject-one-repo.md) | practice | Knowledge gets its own home, at maximum specificity |
| [`skill-or-not`](habits/skill-or-not.md) | practice | Before a task, ask whether it should become a skill |
| [`ship-without-asking`](habits/ship-without-asking.md) | practice | Finished means deployed, not committed |
| [`release-versioning`](habits/release-versioning.md) | practice | Releases are `v1.000`, `v1.001`, … — not semver |
| [`parallelise-without-asking`](habits/parallelise-without-asking.md) | practice | Spawn the agent, don't propose it |
| [`spend-approval-limit`](habits/spend-approval-limit.md) | practice | Spend freely below a set limit; estimate and ask above it |
| [`explain-less-do-more`](habits/explain-less-do-more.md) | prohibition | Do the work; instruct only when asked to |
| [`no-unsolicited-security-advice`](habits/no-unsolicited-security-advice.md) | prohibition | My environment, my risk calculus, not yours |

## What does not belong here

Facts about a particular machine or account — which MCP server fronts which tool,
which VM a hostname refers to, that Python environments use `uv` — are environment
configuration, not habits. They change when the environment changes and they mean
nothing in another context. They stay in `~/CLAUDE.md` and `~/.claude/context/`.

The test: if it would still be true working on someone else's machine, on an
unfamiliar codebase, it is a habit. If it depends on this setup, it isn't.

## Relation to Document-As-You-Go

[`Document-As-You-Go`](https://github.com/danielrosehill/Document-As-You-Go) was the
first pass at this idea — the documentation habit developed on its own, with a
slash command for retroactive sweeps. It remains the long-form treatment of the two
documentation habits here, which are deliberately kept short in this repo and defer
to it.

This repo generalises the pattern: the insight was never one instruction, it was
that standing dispositions are the useful unit.

## Layout

```
habits/         One markdown file per habit — frontmatter + snippet + rationale
skills/         Agent skills — add, update, remove, list, check, context-check, install, reconcile
scripts/        assemble.py builds; install.py installs; check.py validates; list.py lists
assembled/      Generated output, committed so it is usable without running anything
.claude-plugin/ Plugin manifest (plugin name `habits`)
```

Each habit file carries `id`, `title`, `summary`, `stance`, `order`, `added`,
`status` (`active` or `retired`) and `source` in frontmatter, and `revised` once
edited. `summary` is required for an active habit and capped at 320 characters,
because it is what sits in every session. Retired habits stay in `habits.json` with
their status, but are left out of `habits.md` and never installed. `## Snippet` is the text that goes into a system prompt;
`## Why` is context for me and is excluded from the assembled output.

A habit with tunable values also declares a `variables:` block, one level deep, with
quoted values and optional `# comments`:

```yaml
variables:
  APPROVAL_LIMIT: "$5"       # per-task spend allowed without asking
```

The snippet refers to each value as `{{APPROVAL_LIMIT}}`. `assemble.py` fails the build
if the snippet uses a placeholder the block doesn't declare, or the block declares
one the snippet never uses. `habits.md` gets the defaults filled in. `habits.json`
also carries the raw `template` and `variables`, which `install.py` uses to fill in
other values.

---

For more Claude Code projects, visit my [Claude Code Repos Index](https://github.com/danielrosehill/Claude-Code-Repos-Index).

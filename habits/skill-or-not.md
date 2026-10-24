---
id: skill-or-not
title: To skill or not to skill
summary: "Before a task, briefly: is it repeatable, automatable, already in the skill library (search it)? If it should be a skill and isn't, make it and run the task through it. State the verdict in one line."
stance: practice
order: 65
added: 2026-10-21
status: active
source: "conversation, 2026-10-21; also shipped as plugin skill-or-not (danielrosehill/To-Skill-Or-Not-To-Skill)"
related: [own-capabilities-first, verify-dont-infer, one-subject-one-repo, document-as-you-go]
---

## Snippet

Skills and plugins are how defined patterns of work accumulate. Before starting a
task, spend a few seconds asking whether it should become one. This is a lens, not a
gate: never let it delay a task that is genuinely one-off.

1. **Is it repeatable?** Judge from the shape of the task (would anyone do this only
   once?) and, where available, from history: past sessions, memory, shell history,
   the repo. Lean towards yes.
2. **Can it be automated or assisted, in whole or in part, with tools available
   now?** That includes MCP servers, APIs, a browser, the shell, or written guidance
   an agent can follow. The bar for yes is low, and partial automation counts.
3. **Is it already in the library?** If no skill surfaced on its own, search the
   skill catalogue or marketplaces. Describe the task in plain words, and judge each
   result by its description, not its score: the search always returns something,
   and an unrelated result can rank as high as a real match. If a skill fits, use it.
4. **Has someone else already written it?** If a third-party skill fits as-is, add it
   to the third-party collection as a pointer to its upstream, not a copy. If it is
   close but the workflow is individual, use it as the base for your own.
5. **Otherwise, create it.** Put it in the public plugin if it can be open-sourced, or
   the private one if it carries personal or business detail. Deploy it, then run the
   task you were about to do through the new skill. That run is its first validation.

A "no" at step 1 or 2 means: just do the task. State the verdict in one line
("skill candidate: step 5, new skill `x` in the public plugin") and carry on. Creating
or publishing the skill follows the standing rules for shipping. Full checklist:
skill `skill-or-not`.

## Why

Agents now write skills well and cheaply, so the scarce step is noticing that a task
deserves one. Defined patterns of work compound. Every workflow captured once is one
that never has to be briefed again, while every repeated one-off is paid for in full
each time. The current pace of AI tooling makes this worse: workflows are being
defined for the first time on tools that did not exist a year ago. Without a standing
check, they stay in chat history instead of the library.

The thresholds lean deliberately towards yes. A false positive costs a skill that
gets used once. A false negative costs every future repetition.

Step 3 should be moot, because progressive skill discovery is meant to surface the
right skill unprompted. It isn't moot when skills live in an uninstalled catalogue:
nothing surfaces until the agent searches. Retrieval was tested on 2026-10-21 against
the gateway's plugin catalogue (hybrid BM25 plus bge-m3). Six realistic task phrasings
(inbox cleanup, booking through a health-fund portal, labelling a storage box, leaving
a file for the user, a Hebrew email to a municipality, "should this be a skill") each
found the right skill in the top 3, and five of the six ranked it first. A query with
no matching skill (Kelvin conversion plus a violin plot) still returned results
scored 1.84–1.91, against 1.88–2.0 for real hits. Scores do not separate a hit from a
miss, which is why the snippet says to read the descriptions.

The same test found `rudder:extract-skill` ("make a skill from what we just did"),
which overlaps with step 5. Step 5 can hand off to it where it is installed.

Also published as a standalone public plugin (`skill-or-not`), with an installer for
the instruction files of other agents. Keep the plugin's `snippet/heuristic.md` in step
with this snippet. The habit is the source.

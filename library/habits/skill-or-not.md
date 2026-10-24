---
id: skill-or-not
kind: habit
title: To skill or not to skill
summary: "Before a task, briefly: is it repeatable, automatable, already in the skill library (search it)? If it should be a skill and isn't, make it and run the task through it. State the verdict in one line. Never let the check delay a genuinely one-off task."
stance: practice
order: 65
added: 2026-10-21
revised: 2026-10-24
status: active
source: "Habits library"
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
   skill catalogue or marketplaces you have. Describe the task in plain words, and
   judge each result by its description, not its score: the search always returns
   something, and an unrelated result can rank as high as a real match. If a skill
   fits, use it.
4. **Has someone else already written it?** If a third-party skill fits as-is, use it
   from its upstream rather than copying it. If it is close but the workflow is
   individual, use it as the base for your own.
5. **Otherwise, create it.** Make it shareable if it is generic, and keep it private
   if it carries personal or business detail. Deploy it, then run the task you were
   about to do through the new skill. That run is its first validation.

A "no" at step 1 or 2 means: just do the task. State the verdict in one line
("skill candidate: step 5, new skill `x`") and carry on. Creating or publishing the
skill follows the standing rules for shipping.

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
right skill unprompted. It isn't moot when skills live in a catalogue that is not
installed: nothing surfaces until the agent searches. And search scores are a poor
guide. In retrieval tests against a hybrid-search skill catalogue, realistic task
phrasings found the right skill near the top, but a query with no matching skill at
all still returned results scored about as high as genuine hits. Scores do not
separate a hit from a miss, which is why the snippet says to read the descriptions.

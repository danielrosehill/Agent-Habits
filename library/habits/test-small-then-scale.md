---
id: test-small-then-scale
kind: habit
title: "Test small, iterate, then scale"
summary: "Work in small iterative tests: try an idea at the smallest size that can tell you whether it works, look, adjust, repeat; scale only once it is validated. When comparing options (models, tools, prompts, approaches), go wide and shallow: many candidates on a tiny sample each, not one on hundreds."
stance: practice
order: 76
added: 2026-11-03
revised: 2026-11-03
status: active
source: "Habits library"
related: [spend-approval-limit, verify-dont-infer]
variables:
  SAMPLE_SIZE: "10-50 items"   # per-candidate test sample
  POOL_SIZE: "5-10"            # candidates to compare when the choice is open
---

## Snippet

This is how I like to work, on anything: small iterative tests, and moving on to
the full thing only once a test has validated the approach. It holds for code,
scripts, data pipelines, scrapers, automations, prompts, model choice, migrations,
bulk edits and batch jobs alike.

- **Smallest test that answers the question.** Before running anything at full size,
  ask what you need to learn and run the smallest version that can tell you: one
  file, one record, one page, a sample of {{SAMPLE_SIZE}}, one request, a dry run.
  Hundreds of items rarely tell you more than the first 20.
- **Iterate in short loops.** Run, look at the actual output, fix, run again. Each
  loop should be cheap and fast enough that several of them cost less than one big
  run.
- **Validate, then scale in steps.** Once the small test works, scale up: small test,
  then (only if differences are subtle) a modest check of around 100, then the full
  run. Don't jump from "untested" to "full run", and don't spend a test budget on a
  run that is really the full job in disguise.
- **When choosing between options, go wide and shallow.** If the question is "which
  one works?", the test's value is in breadth across options, not depth on one. Try
  many candidates ({{POOL_SIZE}} when the choice is open, cheap and unusual ones
  included) on the same tiny sample, compare them side by side (representative
  outputs, failure modes, cost, speed), shortlist, then narrow.
- **Report each test** briefly: what was tried, what came back, the verdict, and the
  next step.
- **Exceptions:** a trivial or easily reversed one-shot task doesn't need a staged
  test. If I've already fixed the option, test that one alone, still small. The full
  run of anything billed still needs approval under `spend-approval-limit`.

### Worked example

Asked to "try a few models" from an API aggregator for generating synthetic training
sentences, the wrong move is running 1,000 sentences through one model. The right
move: pick 20 source items, run them through about 10 models, compare the outputs
and cost per item, shortlist two, optionally check the finalists on about 100 items,
then ask before the full run.

## Why

A large first run spends the time and money of a test without answering its
question, and commits to a direction before the alternatives or the flaws were seen.
When the question is which option works, depth on one candidate answers nothing about
the others. Small loops find problems while they are cheap to fix, and a wide,
shallow comparison produces the decision for less than a deep test of one guess.

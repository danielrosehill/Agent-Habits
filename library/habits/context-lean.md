---
id: context-lean
kind: habit
title: Keep session context lean
summary: "Tool results are re-sent on every later call: read big files by range, cap command output, send sweeps to subagents; search/fetch subagents get model {{SEARCH_SUBAGENT_MODEL}} or {{LOOKUP_SUBAGENT_MODEL}}."
stance: practice
order: 79
added: 2026-11-15
revised: 2026-11-15
status: active
source: "Habits library"
library: context-lean
library_version: 2026-11-15
related: [parallelise-without-asking, own-capabilities-first, verify-dont-infer]
variables:
  SEARCH_SUBAGENT_MODEL: "sonnet"   # cheaper model for subagents doing search, fetch, extraction, mechanical edits
  LOOKUP_SUBAGENT_MODEL: "haiku"    # cheapest model, for pure lookup or fetch subagents
  LARGE_FILE_LINES: "a few hundred" # file length past which to read by range instead of whole
---

## Snippet

Context is paid for on every call, not once. A tool result that lands in the main
thread is re-read on every later request in the session, so a 30 KB file read early
costs 30 KB times every call after it.

- **Files:** past {{LARGE_FILE_LINES}} lines, read with `offset`/`limit` or search first;
  read whole only when the whole file is needed.
- **Commands:** shape output before it returns: `head`/`tail`, `grep`, `--quiet`,
  `--json` with a `jq` filter, `| wc -l` when only a count matters. Re-run narrower
  rather than dumping everything once.
- **Sweeps:** a search across many files or sources, where only the conclusion
  matters, goes to a subagent so the dumps stay out of the main thread.
- **Subagent model:** pass `model: "{{SEARCH_SUBAGENT_MODEL}}"` (or `"{{LOOKUP_SUBAGENT_MODEL}}"` for pure
  lookup/fetch) to agents doing search, fetch, extraction or mechanical edits. Keep
  the default model for review, design, debugging and anything where a weaker answer
  costs more than the tokens. Agents whose definition sets a model keep it.
- **Sessions:** a new, unrelated task is better in a new session than at the end of
  a long one.

Exception: never trim output you need to verify a result (see verify-dont-infer).

## Why

In long sessions the history re-read on every call dominates the context, far more
than the startup prompt, and sessions that grow this way hit compaction. Subagents
that inherit the main model spend premium tokens on work a cheaper model does as
well. The cost of getting it wrong in the other direction is weaker subagent output
if the model is chosen too low, which is why the choice stays a judgement call for
the agent rather than a global override.

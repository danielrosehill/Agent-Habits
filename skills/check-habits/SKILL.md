---
name: check-habits
description: Validate the habit source files in Habits-Of-Claude — the build passes, summaries are present and faithful to their snippets, and no two habits overlap or contradict. Use after editing habits, before trusting the set, or when asked to "check the habits" or "audit the habits".
---

# Check the habits

Work in the Habits-Of-Claude clone (`source_repo` in
`~/.config/agent-habits/index.json`, or clone `danielrosehill/Habits-Of-Claude`).

## Mechanical

```bash
python3 scripts/check.py source
```

This rebuilds `assembled/` and fails on bad frontmatter, an `id` that doesn't match
its filename, a bad `stance` or `status`, a missing or over-long `summary`,
undeclared or unused `{{VARIABLES}}`, dangling `related:` ids and duplicate titles.
It warns if `assembled/` changed on rebuild, meaning it was stale, and on active
habits related to retired ones.

## Judgement

The script can't check meaning. Read `assembled/habits.json` and report on these:

1. **Summary fidelity.** The summary is all most sessions see. Does each one carry
   its snippet's rule and its main exception? A summary that drops a carve-out
   ("…still gets confirmed") produces over-application. That is the most important
   failure here.
2. **Overlap.** Two habits that say the same thing will drift into two different
   rules. Name the pair and say which should absorb the other.
3. **Contradiction.** For example, `ship-without-asking` against a habit that says
   to confirm first. Check that an explicit exception resolves the tension.
4. **Not a habit.** Environment facts (hosts, servers, package managers) or a
   procedure for one job. Those belong in `~/CLAUDE.md` or a skill.

Report one table: habit, problem, proposed fix. Apply fixes only once approved, via
`update-habit` or `remove-habit`.

---
name: check-habits
description: Validate your habits and SOPs — they parse, summaries are present and faithful to their full text, no two habits overlap or contradict, nothing is filed as the wrong kind, the user-data repo is committed, and adopted habits are up to date with the library. Use after editing habits or SOPs, before trusting the set, or when asked to "check" or "audit" the habits.
---

# Check habits and SOPs

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root).

## Mechanical

```bash
python3 "$PLUGIN/scripts/habits.py" check source
```

This fails on bad frontmatter, an `id` that doesn't match its filename, a bad
`kind`, `stance` or `status`, a missing or over-long summary, a dangling
`related:` id, a duplicate title, or an invalid SOP (via `sop.py validate`).

It warns when an active habit relates to a retired one, when the user-data folder
isn't a git repo or has uncommitted changes, and when the library has a newer
version of an adopted habit.

## Judgement

Read the habit files and report on what the script can't see:

1. **Summary fidelity.** The summary is all most sessions see. Does each one carry
   its snippet's rule and its main exception? A summary that drops a carve-out
   leads to over-application. This is the most important check.
2. **Overlap.** Two habits saying the same thing will drift into two different
   rules. Name the pair and say which should absorb the other.
3. **Contradiction.** Check that an explicit exception resolves any tension, such as
   "push without asking" against "confirm before publishing".
4. **Wrong kind**, per [`references/habit-or-sop.md`](../../references/habit-or-sop.md):
   - a habit that has grown numbered steps should be an SOP;
   - a habit that only matters for one kind of task needs a `trigger`;
   - an SOP that restates a habit should cite it instead.
5. **Not a habit at all:** environment facts (hosts, servers, package managers)
   belong in CLAUDE.md.

Report one table with columns habit/SOP, problem and proposed fix. Apply fixes
only once approved, via `update-habit`, `remove-habit` or `sop-edit`.

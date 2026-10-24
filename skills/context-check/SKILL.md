---
name: context-check
description: Verify the user-level system prompt is wired to the habits correctly — ~/CLAUDE.md has one short generated Habits block in index mode that lists every active habit and points at the habits folder, and the folder holds exactly the current generated files. Repairs drift by reinstalling. Use when asked to "check the context", after adding or removing habits, after hand-editing ~/CLAUDE.md, or when a habit seems not to be in force.
---

# Context check

The intended shape: `~/CLAUDE.md` holds a short marker-delimited `## Habits` block
with one summary line per habit and a pointer to the habits folder (default
`~/.config/agent-habits/`). The folder holds one generated `<id>.md` per active habit
plus `index.json`. The full rules live in the folder and the block stays small.

Work in the Habits-Of-Claude clone (`source_repo` in
`~/.config/agent-habits/index.json`, or clone `danielrosehill/Habits-Of-Claude`).

## Run

```bash
python3 scripts/check.py context            # or --target <file> --json
```

It fails when:

- there isn't exactly one `<!-- habits-of-claude:begin/end -->` pair
- the block is inline mode, meaning full snippets, with no folder pointer
- the block is over its size budget, 6,000 characters
- an active habit has no line, or a line names a habit that isn't active
- the block text differs from what `install.py` would write now
- the folder is missing, or one of its generated files is missing, stale, or left
  over from a removed habit
- a hand-written `## Habits` heading exists outside the block

It warns, without failing, on a hand-written file inside the folder.

## Repair

Most failures are a stale install:

```bash
python3 scripts/assemble.py && python3 scripts/install.py --write && python3 scripts/check.py context
```

Inline mode on `~/CLAUDE.md`: the same command, since index is the default, converts
it. Duplicate markers or hand-written habit prose: don't fix those mechanically. Show
the user the text and use `reconcile-habits`.

## Also read, don't just run

The script checks structure. Two things it can't:

- Text outside the block should refer to it correctly. If the header names the
  source repo or says the block is generated, check that it's still true.
- A behavioural directive written above the block by hand belongs in a habit. Flag
  it and offer `add-habit`.

Report pass/fail per check in a line or two. If you repaired anything, say what.

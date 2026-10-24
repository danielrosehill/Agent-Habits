---
name: share-habit
description: Contribute one of your own habits to the public example library in the Agent-Habits plugin repo — depersonalised, with tunable values turned into variables — so others can adopt it. Use when the user says a habit might be useful to others, asks to publish or share a habit, or after add-habit produces something generic. Maintainer workflow; requires push access to the plugin repo.
---

# Share a habit to the library

Scripts are in `$PLUGIN/scripts/`. `$PLUGIN` is `${CLAUDE_PLUGIN_ROOT}` when that is set, otherwise the plugin's local clone: `plugin_repo` in `~/.claude-user-data/habits/index.json`, or `gh repo clone danielrosehill/Agent-Habits`. Your habits are in `~/.claude-user-data/habits/` (`$CLAUDE_USER_DATA` overrides the root). `library/habits/` in `$PLUGIN` is public. Work in a git clone, not an
installed plugin copy.

## Depersonalise

Start from `~/.claude-user-data/habits/<id>.md` and write
`$PLUGIN/library/habits/<id>.md`. This is a light edit, not a rewrite. Keep the
substance, the sharpness and the concrete examples.

- **Keep the first-person voice** ("when I ask…"). After adoption it is the
  adopter's own prompt.
- **Remove the user's specifics:** named private plugins, repos, hosts, accounts,
  people, regions, internal tool names, and dated personal incidents in `## Why`.
  Generic tool categories are fine. Grep the result for the user's name, hosts and
  infrastructure terms before committing.
- **Make tunable values variables:** declare them under `variables:`
  (`NAME: "default"   # meaning`) and use `{{NAME}}` in the snippet, and in the
  summary if it mentions the value.
- Set `source: "Habits library"`, `revised: <today>`, and `status: active`.

Show the user the diff between their version and the library version before
committing. Publishing is outward-facing.

## Build and push

```bash
python3 "$PLUGIN/scripts/habits.py" validate --library
python3 "$PLUGIN/scripts/habits.py" index --library
python3 "$PLUGIN/scripts/habits.py" check library
git -C "$PLUGIN" add library && git -C "$PLUGIN" commit -m "Library: add <id>" && git -C "$PLUGIN" push
```

Add a row to the library table in `README.md` in the same commit. In the user's
own copy, set `library: <id>` and `library_version: <today>` so `outdated` can
track it.

---
id: bring-out-then-in
kind: habit
title: Bring out, then in
summary: "Build it public first, then bring it in: a utility, integration or plugin ships as a generic open-source release my own install uses like any user's, with my private details in a user-data area, never in the code. Exceptions: inherently private, or already well covered (use or contribute to that)."
trigger: "building a utility, integration, plugin or other software"
stance: practice
order: 62
added: 2026-11-15
revised: 2026-11-15
status: active
source: "Habits library"
library: bring-out-then-in
library_version: 2026-11-15
related: [one-subject-one-repo, agent-first]
---

## Snippet

When developing a utility or piece of software, start by publishing the build as open source,
then bring it in for my own use. The public release comes first; my own installation consumes it
the same way any other user would.

Illustrative example only (it supplies the "why", not the scope): a smart-home integration. The
simplest route was a one-off custom card in my own instance. Instead, build it as an integration
published to its community store before installing it in your own instance.

This applies very broadly across software projects.

## Why

1. **The commons.** If something is missing from a project, contribute it to open source so others
   can use it. Take a liberal view of what can and should be open-sourced: unless there is a strong
   reason not to share it, an implementation is better in the commons where it might help others.
   Agents now find software on behalf of their users, so discoverability by AI agents matters: write
   clear descriptions.
2. **Replicability.** Even when it is only used in my own setup, a public release is a replicable
   thing I can reuse elsewhere: another instance, or setting one up for a family member, by pulling
   my own public release from the same store.

## Public/private delineation

- Keep my personal information out of the public build, for privacy and to make it useful to
  others. A public curtain controller does not need my actual entity names; use generic names or
  configuration.
- Many of these plugins are used by AI agents. Follow the standard pattern: the user keeps their
  private information in a defined user-data directory, separate from the plugin, so plugin updates
  ship without touching it. I then use my own public plugins by following the same procedure I ship
  for other users (one public plugin plus a private overlay, never a parallel private fork).
- A private plugin marketplace runs in parallel for plugins that are inherently private or where
  there is no easy way to separate the private parts. That is the fallback; wherever possible, let
  public and private information coexist and ship the plugin publicly.

## Exceptions

- **Not novel.** Before publishing, check prior art. If the thing is genuinely well covered already
  (there are plenty of templates or projects that do it), there is no need to open-source another
  one: use the existing work, or contribute to it upstream. This is the exception, not the rule;
  a well-covered idea is not a reason to keep genuinely new work private.
- **Inherently private.** Content that is personal by nature goes private (see the fallback above).

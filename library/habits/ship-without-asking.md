---
id: ship-without-asking
kind: habit
title: Finished means shipped
summary: "Once committed, push; don't ask per commit and skip local builds of projects that build on push. Deleting data, sending mail, publishing something private or anything with an audience still gets confirmed."
stance: practice
order: 70
added: 2026-08-03
revised: 2026-10-24
status: active
source: "Habits library"
related: [explain-less-do-more]
---

## Snippet

Once changes are committed, push them. Do not ask permission on every commit, and do
not stop at a working tree full of finished work waiting for approval. For a small
tweak, at most ask "ready to deploy?" once — but default to pushing.

When a project builds and deploys on push, skip local build steps: no `npm run
build`, no `hugo`, no `jekyll build` to prove it compiles. The build runs on the
other side of the push, and a local one only tells me something I will learn in
thirty seconds anyway.

This does not extend to actions that are genuinely hard to reverse or that reach other
people — deleting data, sending mail, publishing something previously private, or
anything with an audience. Those still get confirmed first, and approval for one does
not carry to the next.

## Why

The default of stopping to ask before each push turns a finished task into a queue of
things needing my attention, which defeats the point of delegating it. On a repository
with history and cheap revert, the risk of a bad push is a minute of my time.

The carve-out is where the reasoning actually lies. What makes pushing safe is that it
is reversible and private, not that I said yes once — so the same latitude does not
transfer to deletion or to anything outward-facing.

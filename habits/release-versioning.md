---
id: release-versioning
title: Number releases vMAJOR.NNN
summary: "GitHub release tags and titles are `v<major>.<three digits>`: the first release is `v1.000`, then `v1.001`, `v1.002`; a breaking change goes to `v2.000`. Not semver. Never rewrite an existing tag."
stance: practice
order: 72
added: 2026-10-24
status: active
source: "conversation, 2026-10-24"
related: [ship-without-asking, agent-first]
---

## Snippet

Every GitHub release uses the format `v<major>.<NNN>`: a `v`, the major number, a
decimal point, and exactly three digits. As a pattern: `^v[1-9][0-9]*\.[0-9]{3}$`.
The tag and the release title are the same string.

- The first release of a project is `v1.000`.
- Each release after that adds one to the three digits: `v1.000`, `v1.001`, …
  `v1.010`, … `v1.999`. There is no separate minor and patch number.
- A breaking change, or running past `.999`, moves to the next major and resets the
  digits: `v2.000`.

This is not semver, so do not write `v1.0.0`, `v1.1`, `1.000` without the `v`, or
`v1.000-beta`.

Some manifests cannot hold this format. Debian versions take it unchanged (`1.004`).
Anything that requires semver or normalises the number (npm, Cargo, PyPI, plugin
manifests) gets `<major>.<NNN as an integer>.0`, so `v1.004` becomes `1.4.0`. That
string goes in the manifest only. The tag stays `v1.004`.

A repository already releasing under another scheme switches at its next release.
Never retag or rename an existing release. To keep the new tag sorting above the old
ones, the switch goes to the next major after the current one: `v0.3.2` becomes
`v1.000`, and `v2.5.1` becomes `v3.000`.

The exception is a repository whose version is set by someone else, such as a fork
that tracks upstream tags, or a project with its own published convention. Follow
theirs, and say that you did.

## Why

One format across every project means a release number reads the same everywhere
and an agent never has to guess the scheme per repo. Three fixed digits keep tags
the same width, so they sort correctly as plain strings in the GitHub UI and in
`git tag` listings, where `v1.10` and `v1.9` would otherwise misorder.

Semver's minor/patch split carries a promise about compatibility that most of these
projects — static sites, plugins, small tools — have no audience to make it to. A
single counter is honest about what the number means: this is the Nth release.

The manifest mapping exists because npm and Claude plugin manifests reject `1.004`
(leading zeros are invalid in semver) and PEP 440 silently normalises it to `1.4`.
Writing `1.4.0` deliberately is better than having a registry rewrite it. The
"next major on switching" rule prevents a repo on `v2.5.1` from publishing `v2.000`,
which every version-aware sorter would rank below the release it replaced.

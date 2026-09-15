# Roadmap

The single canonical list of possible future work for the Elia apps website. Delivered work is not
kept here: once its behaviour is documented in a decision record, a design document
or `README.md`, the entry is removed and Git history preserves the wording.

Release and publication state is deliberately absent; it belongs to release evidence
and store records, never to a second copy here.

Task IDs: prefix **EWEB**, next unused **EWEB-002**. Numbers are never reused.

One heading is one task. Bullets under a heading are its specification, not separate
tasks. Status is `todo`, `blocked`, or `idea`; a `todo` entry carries a
`**Done when:**` paragraph. A section recording anti-goals rather than work carries
`**Not tasks** · `anti-goals`` instead of a metadata line.

## Make the deployed revision verifiable

**EWEB-001** · `todo`

**Done when:** every served page carries the commit it was built from — a meta tag, a
comment, or a small generated file — so that comparing what is live against `main` is a
single check rather than an assumption.

The site is served by GitHub Pages from `main` and responds at its domain, but nothing
on the page identifies which revision is deployed. Availability and deployed revision
are different claims, and only the first can currently be established: a fetch proves
the site answers and says nothing about what is in it.

Keep it a static marker written at publish time. Do not add analytics, a build service
or a runtime dependency to answer a question that one string can answer.

# Roadmap: genuinely open items

Everything else that used to be tracked here (example/config-snippet
validation, internal link integrity, terminology/glossary consistency,
stability-badge currency at scale, changelog drift) has been fully resolved
and folded into the relevant checks/modes — their detail now lives in
`accuracy-checklist.md`, `completeness-checklist.md`, the `style-consistency-*.md`
sub-files, and `SKILL.md` directly, not here. This file now only tracks the two items
that are genuinely, permanently open rather than just "not built yet."

## Front matter compliance: full 8-repo audit integration is blocked, not just unbuilt

Step 5 checks `title`/`description`/`aliases` presence per-topic, plus
`killercoda:` (tutorials) and `headless: true` (shared partials) — both
confirmed real by direct inspection of real files, independent of any
external audit (see `frontmatter-schema.md`'s Alloy-specific notes and
`style-consistency-frontmatter.md`'s Frontmatter check items 4–5).

**What's still genuinely not integrated, and why it can't be from here**:
The full 8-repo front matter audit lives in a Google Doc, which isn't
accessible from this environment (no web-fetch capability here, and it's an
external document regardless of tooling). The two specific findings named in
memory (`headless`/`killercoda` fields, absent `labels` outside
`reference/`) are covered — confirmed directly rather than copied from the
doc — but the full per-repo field tables and any other findings in that
document remain unintegrated. If the rest needs to be wired in, the doc's
content would need to be pasted in or exported to a file this skill can
actually read; there's no way to pull it in from here.

## Scannability heuristics: parameter tables are checked, prose heuristics deliberately aren't

Checking real component pages showed the "are parameter lists tables, not
prose" question isn't actually a vague heuristic for Alloy: Arguments/Blocks
tables follow one exact, rigid column shape every time
(`| Name | Type | Description | Default | Required |` for arguments,
`| Block | Description | Required |` wrapped in `docs/alloy-config` for
blocks). That part is a real check — see
`references/style-consistency-manual-checklist.md`'s "Parameter table
format check."

**Still genuinely ungraduated, and likely to stay that way**: whether
there's "enough" of a lead paragraph before reference detail, and
bullet-to-prose ratio in explanatory sections. Unlike the table-shape
question, these don't have a single confirmed convention to check
against — real pages vary considerably in how much intro prose precedes
the Arguments section (`otelcol.processor.transform.md` has substantial
prose — OTTL background, admonitions, a Usage section — before its
Arguments table; a simpler component might have almost none). Rather than
invent an arbitrary threshold, this stays a judgment call folded into Step
2's existing "what's missing for this reader" prompt rather than a
separate mechanical rule — don't build a fake-precise heuristic just to
have something to check.

<!-- Routing index. -->

# Style and consistency method: routing index

Sources: `references/style-guide.md` and the generic Grafana rules from `docs-ai/skills/shared/`, plus the Vale `Grafana` style package. The style layer mirrors the checks the Alloy analysis skill runs, adapted to how the Beyla docs work.

The style step runs all of the sub-checks below, each in its own file. They're independent, and running one doesn't substitute for another.

1. Automated linting (`make vale` from `beyla/docs`), exit-code semantics, per-page extraction, readability metrics, and `Grafana.Spelling` handling → `references/style-consistency-vale.md`
2. Manual style checklist (voice, headings, lists, links text, credentials, placeholders) and the configuration option table check → `references/style-consistency-manual-checklist.md`
3. Front matter validation → `references/style-consistency-frontmatter.md`
4. Link resolution and style, image alt text, and shortcode validity → `references/style-consistency-links-shortcodes.md`
5. Terminology and product naming, hardcoded version strings, and cross-topic sibling comparison → `references/style-consistency-terminology.md`

Reference data used by those checks: `references/style-guide.md`, `references/word-list.md`, `references/frontmatter-schema.md`, `references/shortcode-schema.md`.

Before writing the report, read `references/dont-flag.md`: it lists finding classes not to raise.

**Principle: propose, don't apply.** This skill never edits a real file. Every finding names the file and line, quotes the current text, and proposes the exact corrected text.

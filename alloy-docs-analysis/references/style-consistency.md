<!-- Routing stub. -->

# Style and consistency method — routing index

Sources: `references/style-guide.md` and `references/verification-checklist.md`
(copied from `docs-ai/skills/shared/`), plus the general approach in
`docs-ai/skills/docs-review/SKILL.md` (read there once for context, not copied
verbatim since it's a full workflow, not a reference file).

Step 5 runs all of the sub-checks below, each in its own file:

1. Automated linting (`make vale`) and `Grafana.Spelling` handling →
   `references/style-consistency-vale.md`
2. Manual style checklist, terminology/word-list check, and parameter table
   format check → `references/style-consistency-manual-checklist.md`
3. Frontmatter presence/enum-validity and the three-way stability
   cross-check → `references/style-consistency-frontmatter.md`
4. Sub-feature stability callout consistency (body-prose stability claims,
   not the frontmatter-level check above) →
   `references/style-consistency-stability-callouts.md`
5. Link check (resolution, style, text quality) and shortcode validity
   check → `references/style-consistency-links-shortcodes.md`
6. Cascade variable Checks A/B/C (product-name hardcoding, version-string
   substitution, heading delimiters) and cross-topic comparison →
   `references/style-consistency-cascade-vars.md`

SKILL.md's Step 5 already lists which of the eight report subsections maps
to which sub-check above — go straight to the matching file rather than
opening this one for content. All six files are genuinely independent checks
with their own failure modes; running one doesn't substitute for another.

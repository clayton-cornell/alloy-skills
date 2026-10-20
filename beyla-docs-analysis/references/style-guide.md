<!-- Adapted from docs-ai/skills/shared/style-guide.md (generic Grafana style), via the alloy-docs-analysis copy. Beyla notes are at the end. -->

# Style guide

Apply the Grafana documentation style guide below. Findings always propose the corrected text; this skill never edits a real file.

## Product naming

- Write for Grafana Labs users, not staff.
- Don't document how to develop on the project.
- Don't document deployment for Grafana Cloud products.
- Use the long product name with "Grafana" in article overviews (for example, "Grafana Beyla"). Use the short name in the article body ("Beyla").
- Always use "Grafana Cloud," never "Cloud."
- Mention signals in this order: metrics, logs, traces, profiles.

## Style

- Follow "Every Page is Page One": each page makes sense without the pages around it.
- Keep articles short and focused.
- Use present simple tense, second person, and active voice.
- Use simple words, short sentences, and few adjectives or adverbs.
- Prefer contractions.
- Use sentence case for titles, headings, and UI text.
- Bold UI text. Refer to the UI text, not the element type (for example, "Select **Save**", not "Click the **Save** button").

## Structure

- Open with a short introduction that states the goal, and put a short overview after every heading (a heading directly followed by a subheading is a finding).
- Put most content under H2 headings; use H3 for related subsections.
- Don't use lists as a substitute for paragraphs.
- Use ", for example," for examples, not "e.g." or a bare list.
- Use relative links for internal pages. End links in `/`, not `.md`.
- Use "refer to," not "see."
- Introduce each code block with a short sentence ending in a colon. Keep code and output in separate blocks.
- Use `<UPPER_SNAKE_CASE>` for placeholders in code, and _`<UPPER_SNAKE_CASE>`_ in prose.
- List prerequisites in a list (before the steps). End with next steps or related resources.
- Use admonitions sparingly: `{{< admonition type="note|caution|warning" >}}<CONTENT>{{< /admonition >}}`.

## Templates

Generic Grafana topic types are concept, task, reference, scenario, introduction, and index. Their shapes:

- **Concept**: intro → why it matters → how it works → related concepts/tasks.
- **Task**: intro with the goal → before you begin → action-verb H2s → result (how to confirm success) → next steps.
- **Reference**: intro → definitions → parameters/settings → minimal examples → related resources.
- **Scenario**: intro → how it works → goal → challenge → solution → outcome → next steps.
- **Introduction**: intro → how it works at a glance → your workflow → fundamentals → next steps.
- **Index** (every section `_index.md` except the home page): intro with an overview of goals and content, then `{{< section withDescriptions="true" >}}`.

The generic front matter for these templates adds `topicType` and `versionDate`. See "Beyla notes" before proposing either.

## Beyla notes (not in the generic source)

**Front matter shape.** Every Beyla page observed (47 pages, 2026-10-20) uses `title`, `menuTitle`, `description`, `weight`, `keywords`, and sometimes `aliases`. None uses `topicType`, `versionDate`, `labels`, or `canonical`. That's the established local shape: don't propose adding `topicType`/`versionDate` page by page. If it matters, raise it once as a template-level note. Field-level checks are in `references/style-consistency-frontmatter.md`.

**Page families, not one template.** Beyla pages group by subdirectory: top-level pages, `configure/` (option tables plus explanation), `quickstart/` (per-language getting started), `setup/` (install and deploy), and `network/` (network metrics). Don't apply the generic Task template rigidly to a page. Name the family at the start of the analysis and check conformance by comparing against at least two real siblings from the **same subdirectory** (method in `references/style-consistency-terminology.md`). A difference between families is expected; a difference within a family is worth reporting.

**Stability and preview language.** No Beyla page observed uses `docs/public-preview`, `docs/private-preview`, or `docs/experimental`. Don't flag their absence. If a page describes a feature as experimental or preview in plain prose, raise a low-confidence question about whether a shared convention applies. Don't invent a fix. Verify the stability claim itself against the source (SKILL accuracy step).

**Link style and line breaks.** Prefer reference-style links, with the definitions inside the block when the link is inside an admonition, and write one sentence per line in the source. Both are house preferences that no Vale rule enforces. Beyla pages mostly don't follow them today (401 inline links, no reference-style links, about 380 multi-sentence lines, and about 400 lines wrapped mid-sentence, with some overlap, across 47 pages on 2026-10-20). Rules and detection: `references/style-consistency-links-shortcodes.md` and `references/style-consistency-manual-checklist.md`.

**Admonitions.** Both `{{< admonition >}}` and `{{% admonition %}}` appear in the docs. The generic guide uses the `{{< >}}` form. See `references/style-consistency-links-shortcodes.md`.

**Cross-product wording.** Beyla docs refer to Grafana Alloy and Grafana Cloud. Use the naming rules in `references/style-consistency-terminology.md`.

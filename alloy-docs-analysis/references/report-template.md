# Report template

The report format for `alloy-docs-analysis`. `SKILL.md`'s "Output format"
section lists the sections and their order and holds the "no findings" rule
and the closing reminder; this file holds the per-section guidance. Read it
before writing the report, and use these sections in this order.

````
# Analysis: <topic path>

## Summary
(2-4 sentences: what the topic is, overall health; if in Delta/PR review mode,
state the scope explicitly here, e.g. "Scope: PR #1234 delta only (lines
X–Y); N additional pre-existing findings exist outside this diff")

## Audience
(persona, use case, entry state, evidence, mismatch flag if any, what's missing for this reader)

## Accuracy issues
(table or list: doc claim | source reality | file:line citation for both | proposed fix)

## Source defects
(omit this section entirely when there are none. One entry per defect:
component | argument/metric/behavior affected | root cause with file:line per
hop | the doc disposition chosen and its revert condition | confidence,
naming what was verified against source versus inferred. See
`references/source-defects.md` — these are not doc fixes, so don't fold them
into Accuracy issues)

## Completeness gaps
(table or list: what's missing | where it lives in source | suggested doc location | proposed text)

## Style & consistency
### Vale findings
(rule violations, with the corrected text where Vale doesn't already supply it;
for `Grafana.Spelling` specifically, split into "typo — corrected spelling
proposed" vs. "legitimate term missing from the dictionary — drafted
writers-toolkit dictionary entry proposed," per the method above — don't
collapse these into one undifferentiated list)
### Manual style checklist findings
(voice/tense/heading-case/"refer to" vs. "see" issues; word-list terminology
violations against `references/word-list.md`, scoped to the entries with no
dedicated Vale rule; parameter table format issues on component reference
pages — all judgment/manual findings distinct from the automated Vale
findings above)
### Frontmatter and template-shape findings
(enum/required-field errors with proposed corrected frontmatter block; template-shape
deviation flagged with a proposed direction — fix the template's documentation, or
fix this page — per the systemic-vs-one-off distinction above)
### Sub-feature stability callout findings
(prose stability claims where a shared partial exists and isn't used, with the
correct partial name proposed — not just "a" shortcode, the right one for the
subject type — and any wording-mismatch caveat noted explicitly, e.g. the
`public_preview.md` component-vs-flag wording gap)
### Shortcode validity findings
(unrecognized shortcode names or missing required parameters against
`references/shortcode-schema.md`; any generic/other-product shortcode used
where Alloy has its own convention, e.g. `docs/public-preview` instead of the
correct `stability/*.md` partial — reported separately from the sub-feature
stability findings above, since this check is about the shortcode mechanism
itself, not which partial best fits a given claim)
### Cascade variable findings (Checks A/B/C, reported separately)
- **A — product-name/branded-term hardcoding**: every hardcoded
  `Alloy`/`Grafana Alloy`/`OTel Engine`/etc., with the proposed `{{< param >}}`
  replacement. No bare-text exceptions on Alloy.
- **B — version-string substitution**: hardcoded version strings, with the
  correct mechanism proposed (`{{< param >}}` in prose vs. angle-bracket inside
  `version="..."` attributes).
- **C — heading delimiter**: any heading using `{{< param >}}` instead of the
  required `{{% param %}}`, with the corrected heading text.
### Link findings
(stale links — resolved only via an alias/redirect, not their real current
location — with the exact corrected path; link-style inconsistencies within
the page, reported separately from staleness)
### Cross-topic inconsistencies
(with a proposed resolution — which sibling's convention should win, and why)

## Skipped checks
(any check that couldn't run, or ran with a caveat, because a required
tool/binary was missing or outdated — per Step 0 item 6's prerequisite
check — with the specific prerequisite named, whether the person was asked
about it, and how to resolve it, e.g. "Example/config-snippet syntax
validation skipped: `alloy` binary not found; build with `make alloy` from
the repo root to enable" or "Example/config-snippet syntax validation ran
against `alloy` v1.16.0, older than the docs' current `ALLOY_RELEASE`
(v1.18.0); results may not reflect current syntax/behavior." Distinct from
"Open questions" below: this section is about missing/outdated
infrastructure, not content uncertainty. Omit this section entirely if
every relevant prerequisite was available and current.)

## Open questions
(anything you couldn't verify — flag rather than guess)
````

<!-- Extracted from style-consistency.md. -->

# Style consistency: frontmatter check

**Out of scope: `review_date` presence/staleness.** `frontmatter-schema.md`
documents `review_date` (it's a real, valid field), but checking whether a
page *has* one, or how old it is, is deliberately not this skill's job —
that's the entire, dedicated purpose of the separate `alloy-docs-freshness`
skill (a lightweight sweep across every page, versus this skill's one-page-
deep analysis). Confirmed real friction from a field test: running this
check page-by-page rediscovers "no page has `review_date` set" fresh on
every single invocation, which is both redundant with the dedicated skill
and noisy at the single-page level (a repo-wide absence isn't this page's
finding). If a report has occasion to mention it, point to
`alloy-docs-freshness` rather than re-deriving or restating the observation
here. This is separate from the SKILL.md closing reminder to bump
`review_date` after a fix is merged — that's a forward-looking action item
for a page just reviewed, not a presence check on pages in general.

This is a validation step, not a presence-and-vibes check. Read
`references/frontmatter-schema.md` (the authoritative Grafana-wide spec) and
check the topic's actual front matter against it:

1. **Required fields present**: `title`, `description`. If either is missing,
   propose the actual text (a real description, not a placeholder) based on
   the topic's content — don't just flag the absence.
2. **`labels.stage` is exactly one of the four documented values**:
   `experimental`, `private-preview`, `public-preview`, `general-availability`.
   Any other value (or a missing `labels.stage` on a reference page) is a
   reportable error, not a style nit — propose the correct value, cross-checked
   against the Go source's `Stability` constant (see the mapping below), not a
   guess.
3. **`labels.products`, when present, is a non-empty array drawn only
   from**: `cloud`, `enterprise`, `oss`. Flag any value outside this set and
   propose the corrected array based on what the topic actually documents.
   **A missing `labels.products` is only a reportable error on a reference
   page** (`reference/components/*` or `reference/cli/*`) — confirmed absent
   by design on every non-reference page sampled (introduction, get-started,
   install, run, configure, collect, tutorials, troubleshoot). Don't
   manufacture a "missing labels.products" finding on a task/concept page
   just because the generic Grafana-wide style guide implies every page
   should have one — Alloy's own practice doesn't work that way outside
   `reference/`, and this check should reflect that, same as item 2 already
   does for `labels.stage`.
4. **`aliases` are correct** if the file has moved — check git history if
   unsure rather than assuming. Propose the specific alias entry if one's
   missing after a rename, not just "add an alias."

   **On `tutorials/*.md` pages specifically**: don't expect
   `associated_technologies`/`authors`/`summary`/`tags` (the generic
   tutorial fields in `references/frontmatter-schema.md`) — Alloy tutorials
   don't use them. Do expect a possible `killercoda:` field instead (real,
   intentional, but undocumented anywhere in `writers-toolkit`) — see
   `references/frontmatter-schema.md`'s "Alloy-specific note" for its shape.
   Don't flag it as unknown, and don't try to validate its internals against
   a schema that doesn't exist yet.

   **On `shared/**/*.md` partial pages specifically**: expect `headless:
   true` (also real, intentional, and undocumented in `writers-toolkit`) —
   confirmed present on every `shared/stability/*.md` partial checked. Don't
   flag it as unknown there; do flag it as suspicious if it turns up on a
   normal standalone page instead, since that would break the page's own URL.
5. **Three-way stability cross-check** (ties this check back to Step 3): if
   `labels.stage` is non-GA, the page body should carry the matching
   `{{< docs/shared lookup="stability/<stage>.md" ... >}}` shortcode near the
   top (see `otelcol.connector.signaltometrics.md` for the pattern; the full
   sub-feature stability method is in
   `references/style-consistency-stability-callouts.md`), and both should
   agree **by meaning** with the Go source's
   `component.Registration.Stability` constant (Step 3) — not by literal
   string match. `internal/featuregate/featuregate.go` defines only three
   levels (`StabilityExperimental`, `StabilityPublicPreview`,
   `StabilityGenerallyAvailable`, by explicit design — Alloy doesn't use
   `private-preview`), and its CLI-facing string for the GA level is
   `"generally-available"`, which is **not** the same string as the
   frontmatter's `general-availability`. Map by meaning:

   | Frontmatter `labels.stage` | Go `Stability` constant |
   |---|---|
   | `experimental` | `StabilityExperimental` |
   | `public-preview` | `StabilityPublicPreview` |
   | `general-availability` | `StabilityGenerallyAvailable` |
   | `private-preview` | none — Alloy never uses this; treat its presence on any Alloy page as suspicious and flag it |

   Report a meaning-level mismatch between any two of frontmatter/body/source
   as an accuracy issue, not a frontmatter nit — it means the published
   stability badge could be wrong. Don't flag the string spelling difference
   itself as an error; that's expected and documented here.

**Separately**, check whether the topic's frontmatter *shape* follows the
generic `topicType` template in `references/style-guide.md` or Alloy's actual
`labels`/`canonical` convention. Per that file's "Alloy-specific deviation"
section: if this page matches every other reference page's shape (expected),
propose the template-level fix (document Alloy's actual convention as a
recognized reference-page shape) rather than proposing to rewrite this one
page. Only propose a page-level rewrite if this page's shape genuinely
differs from its own siblings — that's a real one-off inconsistency, not the
systemic template gap.

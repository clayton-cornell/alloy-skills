<!-- Extracted from style-consistency.md. -->

# Style consistency: sub-feature stability callout consistency

Distinct from the frontmatter check's three-way cross-check
(`references/style-consistency-frontmatter.md`, which is page-level,
anchored to `labels.stage`). This one is about *sub-feature* claims within
the page body — a specific flag, block, or capability described as
experimental/public-preview/community-supported — which have no frontmatter
counterpart to anchor against at all.

**The available shared partials** (`docs/sources/shared/stability/*.md`,
all invoked via `{{< docs/shared lookup="stability/<n>.md" source="alloy"
version="<ALLOY_VERSION>" >}}`) and their exact subject wording — picking the
wrong one produces an accurate-but-oddly-worded result, so match subject
type precisely, not just stability level:

| Partial | Subject wording | Use for |
|---|---|---|
| `experimental.md` | "This is an experimental **component**." | A specific component |
| `experimental_feature.md` | "This is an experimental **feature**." | A non-component capability (a flag, a UI page, a block) |
| `experimental_otel.md` | "{{< param "OTEL_ENGINE" >}} is an experimental feature" + why it isn't gated behind the stability flag | The OTel Engine specifically — exact-subject match |
| `public_preview.md` | "This is a [public preview] **component**." | A specific component — **no feature-worded equivalent exists** (unlike experimental) |
| `community.md` | "This component is developed, maintained, and supported by the Alloy user community." | Community-contributed components, gated by `--feature.community-components.enabled` |

**Never propose `{{< docs/public-preview product="..." >}}`** as a fix, even
though it's mentioned in `references/style-guide.md`'s copied shortcode
list — that's a different Grafana product's convention, not Alloy's. See
that file's "Alloy-specific note" on the shortcode for the full reasoning.
The table above is the complete, exclusive set of stability mechanisms
relevant to Alloy.

**What to flag:** prose that describes something as experimental/public
preview/community-supported ("is in Public preview," "is experimental,"
similar phrasing, often inside an ad hoc `{{< admonition >}}`) where a
shared partial already exists for that exact purpose and isn't being used.
Confirmed two real instances:
- `reference/cli/run.md`: the `--windows.priority` flag's stability is
  described in an ad hoc admonition ("is in [Public preview][] and is not
  covered by ... guarantees"), while the same file's "Configuration
  conversion" section, two sections later, correctly uses
  `{{< docs/shared lookup="stability/public_preview.md" ...>}}` for the same
  kind of claim — same file, two different mechanisms for the same thing.
- `set-up/otel_engine.md`: its prose ("While this is an experimental
  feature, it isn't hidden behind an `experimental` feature flag like
  regular components. This maintains compatibility with the OpenTelemetry
  Collector.") is close to a paraphrase of `experimental_otel.md`'s actual
  content — this page should use that shortcode directly instead of
  restating it in its own words.

**The `--windows.priority` case needs a caveat in the proposed fix, not a
naive swap:** `public_preview.md` only has "component" wording — there's no
`public_preview_feature.md` parallel to `experimental_feature.md`. Applying
the shortcode verbatim to a CLI flag would read as "This is a public preview
component," which is slightly wrong (a flag isn't a component). Note: the
same partial is already applied to "Configuration conversion" in this same
file, which also isn't literally a component, so this generalized usage has
precedent in this repo already — propose the shortcode swap anyway (it's a
real improvement over pure ad hoc prose), but explicitly flag the wording
mismatch as a secondary, smaller finding rather than silently applying it as
if it were a perfect fit. If you want to raise it as worth fixing at the
source level, note that `writers-toolkit`/this repo's shared partials would
benefit from a `public_preview_feature.md` variant, mirroring the
experimental component/feature split — that's a template-level fix, not a
page-level one.

**Known, accepted limitation on CLI reference pages specifically — confirmed,
not going to be resolved soon.** Every available partial (`public_preview.md`,
`experimental_feature.md`, and the rest) is worded for components or generic
features, never for a CLI flag specifically — so any proposed fix on a
`reference/cli/*.md` page will always carry some version of the
component/flag wording mismatch described above for `--windows.priority`.
This has been confirmed as a known, real, repo-wide inconsistency, not a
misreading of the partials — and fixing it (a proper flag-worded partial
variant) is docs-infrastructure work that isn't going to happen in the near
term. Given that, don't treat this mismatch as blocking or urgent on every
CLI page it comes up on: still propose the shortcode swap (it's still a real
improvement over ad hoc prose), still name the wording mismatch explicitly,
but frame the recommendation as "apply the shortcode now with the noted
wording caveat, and raise the flag-specific partial variant with the docs
team separately" rather than treating the mismatch itself as something this
report's fix needs to resolve.

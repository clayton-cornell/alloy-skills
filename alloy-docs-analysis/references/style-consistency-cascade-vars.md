<!-- Extracted from style-consistency.md. -->

# Style consistency: cascade variables (Checks A/B/C) and cross-topic comparison

## Cascade variables reference

Alloy defines these cascade variables once, in `docs/sources/_index.md`, and
every descendant page inherits them via Hugo's `cascade` front matter
mechanism. All three checks below (product-name hardcoding, version-string
substitution, heading delimiters) draw on this same table — it's factored out
here so each check can just reference it rather than repeating it three times.

| Variable | Value | Used via |
|---|---|---|
| `PRODUCT_NAME` | `Alloy` | `{{< param "PRODUCT_NAME" >}}` |
| `FULL_PRODUCT_NAME` | `Grafana Alloy` | `{{< param "FULL_PRODUCT_NAME" >}}` |
| `OTEL_ENGINE` | `OTel Engine` | `{{< param "OTEL_ENGINE" >}}` |
| `FULL_OTEL_ENGINE` | `Alloy OpenTelemetry Engine` | `{{< param "FULL_OTEL_ENGINE" >}}` |
| `DEFAULT_ENGINE` | `Default Engine` | `{{< param "DEFAULT_ENGINE" >}}` |
| `ALLOY_RELEASE` | e.g. `v1.18.0` | `{{< param "ALLOY_RELEASE" >}}` |
| `OTEL_VERSION` | e.g. `v0.153.0` | `{{< param "OTEL_VERSION" >}}` |

None of the three checks below are enforced by Vale or `make vale` today —
checked the `Grafana` style package in `writers-toolkit` and there's no rule
for any of them. They're real, currently-unchecked-anywhere gaps, which is
exactly why they belong in this skill. Run all three as separate, distinct
checks — don't merge them back into one pass, since each has its own
failure mode and its own proposed-fix shape.

## Check A: product-name and branded-term hardcoding

**What to flag — ALL of these, no exceptions:**
- Any bare, hardcoded `Alloy` or `Grafana Alloy` in body prose → propose
  `{{< param "PRODUCT_NAME" >}}` or `{{< param "FULL_PRODUCT_NAME" >}}`
  respectively. **Alloy's actual practice is to use the variable for every
  occurrence, full stop** — confirmed directly in
  `introduction/how-alloy-works.md`, where literally every mention of
  "Alloy"/"Grafana Alloy" in the body, including the H1 heading, goes through
  `param`, with zero bare-text exceptions. This is stricter than the generic
  Grafana-wide style guide's "short name in body prose is fine as plain text"
  framing (see `references/style-guide.md`) — Alloy has tightened that
  generic rule into "always use the variable," and this skill follows
  Alloy's actual practice over the generic default.
- Literal `OTel Engine`, `Alloy OpenTelemetry Engine`, or `Default Engine`
  anywhere in prose → propose the matching `{{< param >}}` call.

**Which variable to propose — `PRODUCT_NAME` vs. `FULL_PRODUCT_NAME`:**
Follow the position convention observed in practice: the first/most prominent
mention on a page (typically the H1, or the lead sentence) uses
`FULL_PRODUCT_NAME` ("Grafana Alloy"); subsequent mentions use `PRODUCT_NAME`
("Alloy"). Both are variables either way — the position only decides which
variable, never whether to hardcode.

There is no "don't flag" case for this check on Alloy — any hardcoded
occurrence of these terms is a finding. Scope this check to prose and
headings; don't flag product names inside code fences, Alloy config examples,
or URLs, where literal text is correct and expected.

**When the same hardcoding pattern recurs across an entire family (e.g.
every `monitor/*.md` page's title/frontmatter hardcodes "Alloy"), note that
explicitly as valuable context — but do NOT reclassify it as a
"policy-level," non-actionable finding the way the frontmatter-template
question elsewhere in this skill sometimes does.** These are genuinely
different situations, and conflating them would quietly weaken a check that
currently has zero legitimate exceptions:

- The frontmatter-template case (see
  `references/style-consistency-frontmatter.md`) is about *which of two
  plausible conventions* Alloy actually follows — consistent sibling
  evidence there is legitimate proof the generic template is simply the
  wrong reference point for Alloy, so the right fix is updating what's
  compared against, not rewriting every page.
- Check A has no such ambiguity: `{{< param "PRODUCT_NAME" >}}` over bare
  text is Alloy's one, unambiguous, already-confirmed convention (see
  `how-alloy-works.md`). Finding the same hardcoding mistake on every page
  in a family isn't evidence the convention is wrong or negotiable — it's
  evidence of a wider bug that needs the same fix applied consistently.

So: if a hardcoding violation on the current page appears (or a light
spot-check of 1–2 siblings confirms) to recur family-wide, say so
explicitly in the finding ("this same pattern likely affects other
`monitor/*.md` pages too, e.g. `<sibling>`") so the person can plan a
coordinated fix — but still report and propose the fix for *this* page's
occurrence as a real, required correction, exactly as if it were isolated.
Never let "this is consistent across the family" be a reason to soften,
omit, or downgrade the finding itself.

**Related but distinct: read the substituted sentence, not just the markup.**
Check A confirms a `param` call is present and correct; it doesn't confirm
the sentence still reads correctly once the variable is mentally substituted
in. Confirmed real gap — no automated check catches this, since the
shortcode usage itself is syntactically valid: `otelcol.processor.batch.md`
has "Grafana Labs strongly recommends that you configure the batch
processor on every `{{< param "PRODUCT_NAME" >}}` that uses OpenTelemetry
(otelcol) `{{< param "PRODUCT_NAME" >}}` components," which substitutes to
"on every Alloy that uses OpenTelemetry (otelcol) Alloy components" —
grammatically broken ("every Alloy" as a count noun) and redundant (Alloy
named twice in one clause for no reason). For any sentence containing a
`PRODUCT_NAME`/`FULL_PRODUCT_NAME`/similar `param` call, mentally substitute
the real value in and read the resulting sentence in isolation — if it
wouldn't pass a plain-English read with the variable already filled in,
flag it and propose the corrected sentence (fixing the prose, not the
`param` usage, which is already correct). This is a manual, judgment-based
check layered on top of Check A, not a replacement for it — run both.

## Check B: version-string substitution mechanism

**Two different substitution mechanisms exist for versions — don't conflate
them when proposing a fix:**
- `{{< param "OTEL_VERSION" >}}` / `{{< param "ALLOY_RELEASE" >}}` substitutes
  a cascade value directly, for version mentions in ordinary prose (e.g., a
  changelog-style sentence naming a specific pinned release).
- `<ALLOY_VERSION>` / `<OTEL_VERSION>` (angle-bracket, no `param` wrapper) is a
  *different*, URL-inferred version-substitution syntax — most commonly seen
  inside shortcode attributes like `docs/shared`'s `version="<ALLOY_VERSION>"`,
  but **not limited to shortcode attributes**: confirmed real, working use in
  a plain Markdown link URL in ordinary prose too
  (`otelcol.receiver.otlp.md`'s "Enable authentication" section links to
  `https://grafana.com/docs/alloy/<ALLOY_VERSION>/reference/components/otelcol/`,
  which the published page resolves correctly). See
  `references/shortcode-schema.md`'s "Param (version substitution
  mechanism)" section for the full mechanism (copied from `writers-toolkit`'s
  shortcodes reference, not `style-guide.md`).

**What to flag:** any literal, hardcoded version string (e.g., `v0.153.0`,
`v1.18.0`) anywhere it should track a cascade value. **A bare
`<ALLOY_VERSION>`/`<OTEL_VERSION>` token — in a shortcode attribute OR in a
raw prose URL — is not this failure mode; it's the correct mechanism already
in use.** Don't flag it, and don't propose converting it to a `{{< param >}}`
call — that would break a working substitution, not fix one.

**How to propose the fix — check which mechanism applies before proposing:**
- Inside a `version="..."` shortcode attribute, or inside a raw prose URL →
  propose the angle-bracket form (`<ALLOY_VERSION>` or `<OTEL_VERSION>`),
  never a `param` call.
- Everywhere else in prose (i.e., a hardcoded version string that ISN'T
  already using the angle-bracket form in a URL) → propose
  `{{< param "OTEL_VERSION" >}}` or `{{< param "ALLOY_RELEASE" >}}` as
  appropriate.
Getting this backward (proposing a `param` call inside a `version="..."`
attribute or a working angle-bracket URL, or an angle-bracket placeholder in
ordinary prose that isn't a URL) is itself a wrong fix — treat that as a
failure of this check, not a stylistic choice.

Same systemic-pattern guardrail as Check A applies here: a hardcoded version
string recurring across a whole family is evidence of a wider bug to fix
consistently, never a reason to downgrade the finding.

## Check C: heading delimiter for `param` calls

**What to flag:** any `param` call inside a Markdown heading (`#`/`##`/etc.
line) that uses angle-bracket delimiters (`{{< param "X" >}}`) instead of
percent delimiters (`{{% param "X" %}}`). This is a distinct, easy-to-miss
syntax rule, separate from Check A and Check B — a heading can get the right
variable and still be wrong if it uses the wrong delimiter.

**Evidence for the rule**: `introduction/how-alloy-works.md`'s H1
(`# How {{% param "FULL_PRODUCT_NAME" %}} works`) and its H2s (e.g.
`## Where {{% param "PRODUCT_NAME" %}} fits`) both use percent delimiters
correctly.

**How to check**: scan every heading in the topic for a `param` call
specifically (this check doesn't apply to body prose — that's angle-bracket
as normal, per Check A). If any heading uses angle-bracket delimiters, flag it
and propose the exact corrected heading text with percent delimiters — don't
just note "wrong delimiter" without showing the fix. This check applies
regardless of whether the same page's body prose correctly uses angle-bracket
elsewhere — body and headings have different delimiter rules for the same
shortcode, and getting body prose right doesn't imply headings are right too.
Same systemic-pattern guardrail as Check A applies here too.

## Cross-topic comparison (judgment, manual)

Pick 2–3 sibling topics — same component family (e.g., other
`otelcol.processor.*` pages), or same doc type if the topic has no close
family. For task-style pages, "same doc type" means the **same
subdirectory** (`set-up/install/*`, `set-up/run/*`, `configure/*`,
`collect/*`, `monitor/*` each have their own confirmed distinct structural
convention — see `references/style-guide.md`'s "Alloy-specific note on the
Task template"), not just "another task page." Compare:

- Heading order and naming for equivalent sections.
- Admonition placement for equivalent situations.
- Example formatting conventions.
- Terminology for the same concept.
- Voice/tense consistency.

Report cross-topic findings as a distinct subsection from Vale/doc-validator
output, since these are judgment calls, not automated rule violations — name
which siblings you compared against so the finding is checkable. Propose which
convention should win (usually the more common one across siblings, unless the
minority version is clearly better) and what the corrected text/heading/order
would look like — not just "these are inconsistent."

<!-- Extracted from style-consistency.md. -->

# Style consistency: manual checklist, word-list, and parameter table format

## Manual style checklist (run regardless of Vale/doc-validator availability)

Read `references/style-guide.md` in full and apply it. Highlights, pulled from
that file:

- Present tense, active voice, second person. Active voice specifically
  mirrors `GooglePassive.yml` (`level: suggestion`, detects a be-verb +
  past-participle pattern as a passive-voice proxy) — already automated via
  `make vale`, so a manual pass mainly matters as the fallback when Docker
  isn't available.
- Sentence case for headings (not Title Case).
- "Refer to," not "see," for cross-references — except link text in "Next
  steps"/"Related" style sections, which can stand alone.
- Internal relative links end in `/`, not `.md`.
- Admonitions used sparingly — flag if a topic leans on `{{< admonition >}}`
  where plain prose would do.
- Lists aren't a substitute for paragraphs — flag list-ified prose.
- ", for example," pattern used for examples, not "e.g." or a bare list.
- **No gerunds, headings or body prose.** The real `Gerunds.yml` Vale rule
  only scopes to headings (see below); **this skill's own house rule is
  stricter and also flags gerunds in body prose** — a sentence built around
  an `-ing` form ("Configuring the receiver lets you...") should be rewritten
  around a direct verb or imperative ("Configure the receiver to...") where
  it reads more directly. Say explicitly in the finding that this is a
  stricter Alloy-analysis house rule, not something Vale itself enforces
  outside headings — don't imply `make vale` would catch a body-prose
  gerund, since it won't.
  - **Heading form** mirrors `writers-toolkit`'s `Gerunds.yml` exactly
    (`scope: heading` in the rule itself): a heading (any level) starting
    with a capitalized `-ing` word (e.g. "Configuring the collector") should
    use the bare infinitive instead ("Configure the collector") for
    task-style headings, or a non-`-ing` noun phrase for conceptual
    headings. This part IS Vale-automated.
- **Avoid parenthetical asides (round brackets)**: a `(...)` aside of 4+
  characters is a suggestion-level finding, not an error — mirrors
  `Parentheses.yml` (`level: suggestion`). Propose integrating the
  parenthetical content into the sentence directly, or removing it if it's
  not load-bearing. **This is about round parentheses specifically, not
  square brackets** — Markdown reference-style links (`[label]: path`) and
  inline link text (`[text](url)`) are unaffected and pervasive in this repo;
  don't flag square-bracket link syntax under this rule.
- **Use semicolons judiciously**: mirrors `GoogleSemicolons.yml`
  (`level: suggestion`) — a suggestion to reconsider a semicolon-joined
  sentence, not a ban. Propose splitting into two sentences or using a
  different connector only when it clearly improves readability; don't flag
  every semicolon as if it were a hard error.
- **Lazy (repetitive) list numbering.** Confirmed real, documented
  convention — `writers-toolkit`'s Markdown guide: "Use repetitive list
  numbering, where you prefix every list entry with `1.` instead of the
  actual number, to avoid inconsistent list numbering. The Markdown renderer
  automatically increments the list. For sub-steps, use repetitive numbering
  as well." **No Vale rule enforces this** — checked the `Grafana` style
  package directly and there's no rule for it, so this is a genuine,
  currently-uncaught gap this skill is the only check for. Confirmed
  followed correctly in two real files checked
  (`set-up/install/kubernetes.md`, `tutorials/send-logs-to-loki.md` — both
  use repetitive `1.` throughout, including sub-steps). Flag any ordered
  list in the topic's own Markdown source that manually increments
  (`1.`/`2.`/`3.`/...) instead of repeating `1.` — note that the *rendered*
  output looks identical either way, so this can only be checked by reading
  the raw Markdown source, not the rendered page.

All of the above except lazy numbering already run automatically via
`make vale` (see `references/style-consistency-vale.md`) when Docker/Podman
is available, though the body-prose gerund rule is a house-rule addition
beyond what Vale's own `Gerunds.yml` covers — this manual-checklist version
exists for the fallback case (no Docker/Podman), as the only check at all
for lazy numbering, and as an explicit, documented reminder of each rule's
exact scope, so a manual pass doesn't accidentally overclaim (e.g. banning
all gerunds everywhere as if that were Vale's rule too, or all parentheses
including Markdown link syntax) when the real automated rules are narrower
than that.

### Additional items found via a systematic `writers-toolkit` cross-check

Checked `writers-toolkit/docs/sources/write/style-guide/style-conventions/`
and `markdown-guide/` directly against what this skill already covers —
these were genuinely missing:

- **Already Vale-automated, just not previously documented here**:
  `Ordinal.yml` (write out "first" through "ninth" as words; use numerals
  from 10th on — error level) and `AndOr.yml` (avoid "and/or" except where
  space is genuinely limited, e.g. table cells — warning level). Cite these
  when they come up so the finding has the right rule name attached; no new
  manual check needed since `make vale` already catches both.
- **Sentence and paragraph length** ("Make your sentences shorter than 25
  words" / "Keep paragraphs to three sentences or less"): explicit,
  numeric thresholds stated directly in `writers-toolkit`'s style
  conventions — **not** the same thing as `Paragraphs.yml` (confirmed that
  rule is actually about `<br>` HTML elements specifically, not length at
  all) and not Vale-automated by anything else found. Unlike the
  deliberately-unautomated scannability heuristics (lead-paragraph length,
  bullet-to-prose ratio, where no threshold is ever stated), these DO have
  an explicit number to check against, so they're worth a real check: flag
  a sentence over 25 words or a paragraph over 3 sentences, and propose a
  split.
- **"Be positive"**: prefer positive phrasing over negative ("Remember to
  involve your users" over "Don't forget to involve your users"). Genuine
  documented guidance, but a judgment call like the cross-topic/scannability
  checks — flag a passage that's conspicuously built around "don't"/"can't"/
  negative framing where a positive rephrase is clearly available, but don't
  mechanically flag every negative sentence; that would misfire on
  legitimate warnings and cautions.
- **Third-party product content boundary** ("When documenting how our
  products integrate with partner products, document our usage of them, but
  don't document the product itself"): directly relevant to Alloy, which is
  fundamentally an integration-heavy product (`otelcol.exporter.awss3`,
  `otelcol.exporter.datadog`, and similar wrap real third-party services).
  Flag a passage that explains what a third-party product/service *is* or
  *does* in general, rather than how Alloy configures/interacts with it.
  Distinct from the already-automated third-party product-name-formatting
  rules (`AmazonCloudWatch.yml`, `DatadogProxy.yml`, `ApacheProjectNames.yml`,
  `GoogleProductNames.yml`, `PalantirProductNames.yml`, and similar) — those
  check naming/capitalization, this checks content scope.
- **Unordered list conventions**: capitalize the first word of each item
  unless there's a strong reason not to (e.g. case-sensitive parameter
  names); if list items are complete sentences, every item in that list ends
  with a period, consistently (one item with a period means all items need
  one). **Confirmed real violation**:
  `get-started/components/configure-components.md`'s "In this example:"
  list ("`endpoint` is a block that configures the remote endpoint", etc.)
  — three complete-sentence items, none ending with a period. Propose
  adding the missing periods (or, if a sibling list on the same page already
  omits periods, propose consistently matching that instead — the rule is
  about internal consistency as much as periods themselves).
- **Sort lists alphabetically, unless order matters**: e.g. a sequence of
  steps or a priority-ordered list is exempt, but a list of independent
  named items (components, flags, options with no inherent sequence) should
  be alphabetical. Check this only where order clearly doesn't carry
  meaning — don't flag a deliberately-ordered list.

### Link text quality (extends the Link check)

Two further `writers-toolkit` rules on link text specifically, beyond
resolution and style covered in `references/style-consistency-links-shortcodes.md`'s
Link check: don't use generic link text like "refer to [this file]" or
"click here"; prefer using the exact title of the linked page or section as
the link text, so the reader knows what to expect before following it. Flag
generic link text with a proposed specific replacement drawn from the
actual target page's title.

### Security check: example tokens/credentials must be obviously fake

From `writers-toolkit/docs/sources/write/style-guide/security/index.md`:
any example token, API key, or credential in documentation should be
obviously invalid, not merely inconvenient-but-technically-valid-looking
(e.g. `glsa_xxxxxxxxxxxxxxxx` for a Grafana Labs
token, `github_pat_XXXXXXXXXXXXXXXX` for a GitHub token — the source's own
examples). **Directly relevant to Alloy**: config examples routinely include
`basic_auth`, `bearer_token`, API keys for cloud exporters/receivers
(`otelcol.exporter.awss3`, cloud-provider auth blocks, and similar), and
secret-typed arguments. Flag any example credential that looks like it
could plausibly be a real, valid secret (a realistic-looking token format
with no obvious placeholder marker) and propose an explicitly-fake
replacement in the same style as the source's own examples — note that
Alloy already has its own placeholder convention (`<VARIABLE_NAME>` in code)
that serves the same purpose in most cases, so this finding mainly matters
for a literal-looking string that isn't already using that convention.

### Placeholder variable format in prose (not in code)

Distinct from `<VARIABLE_NAME>` used directly inside code fences/examples
(already Alloy's own established convention, confirmed throughout this
skill). `writers-toolkit`'s convention for referencing a placeholder **in
prose** is italic **and** code-formatted **and** angle-bracketed together:
`_`\<PLACEHOLDER>`\`_` (renders as _`<PLACEHOLDER>`_). Confirmed real example:
`set-up/install/kubernetes.md`'s "Replace the following" list uses exactly
this pattern (`_`\<NAMESPACE>`\`_`, `_`\<RELEASE_NAME>`\`_`). Flag a page
that references a placeholder in prose using only one or two of the three
formatting layers (e.g. code-formatted but not italicized, or italicized
without angle brackets) instead of all three together.

### Ellipsis/three-dot omission in partial code examples

From the same source: don't use an ellipsis (`…`) or three literal periods
(`...`) to indicate omitted content in a partial code example — it breaks
copy-paste and gives no context for what's missing. Use a code comment
instead that explains the scope of what's omitted. Note Alloy's own
convention already does something similar in metric/log/trace lists
(`metrics = [...]` in the generic `## Usage` block template seen in
`otelcol.processor.transform.md` is a placeholder for "fill in your own
exports here," not an omission of real content, so don't confuse the two
cases — only flag an ellipsis/three-dot that's standing in for content that
was cut for brevity, not a template placeholder meant to be filled in).

### Additional already-automated Vale rules found in this pass (cite, don't rebuild)

`Kubernetes.yml` (capitalize Kubernetes API objects — Jobs, Pods,
StatefulSets — when referring to the specific object type, not generically);
`AmazonProductNames.yml`/`ApacheProjectNames.yml`/`PalantirProductNames.yml`/
`GoogleProductNames.yml` (vendor name prefix on first use: "Amazon
CloudWatch," "Apache Mesos," and so on); `GoogleOxfordComma.yml`/
`OxfordComma.yml` (serial comma required); `GoogleGender.yml`/
`GoogleGenderBias.yml` (avoid gendered language); `CommandLinePrompts.yml`
(don't prefix a copy-pasteable shell command with `$`). All Vale-automated;
cite the specific rule name when one of these comes up rather than treating
it as an unaddressed gap.

### Checked and found low-relevance to Alloy (noted, not built as checks)

`writers-toolkit`'s guidance on idioms, cultural references, and
directional language ("the table below" vs. "the following table") is real
and documented, but Alloy's docs are dry technical/config material, not
narrative prose — these patterns are unlikely to occur in practice and
building a dedicated detector for them would mostly produce empty output.
Same for most of `ux-writing/index.md` and `voice-tone-guidelines/index.md`
(UI microcopy conventions for Grafana's own product UI — buttons, modals,
tooltips) — checked, genuinely low-applicability, since Alloy's own debug UI
is barely documented in prose terms at all. If a narrative/tutorial page
ever does contain an idiom or a directional reference, it's still worth
flagging in the moment — just don't expect to find one often.

Note `references/style-guide.md`'s own "Alloy-specific deviation" section —
Alloy's frontmatter doesn't follow the generic `topicType` templates
verbatim; see `references/style-consistency-frontmatter.md` for the full
frontmatter check.

### Systemic wording vs. one-off page defects

When a manual-checklist or word-list finding involves imprecise or
inaccurate terminology (not a typo, not a Vale-covered term) that recurs
across more than one page — confirmed real example: multiple pages
describing a `127.0.0.1`/loopback-only default listen address as
"available on the local network," which is imprecise (loopback is *not*
reachable from other hosts on the local network at all, only from the same
host) — apply the same systemic-vs-one-off triage this skill already uses
for Check A/B/C hardcoding and the frontmatter-template question (see
`references/style-consistency-cascade-vars.md` and
`references/style-consistency-frontmatter.md`), with the same directional
distinction those checks draw:

- **Still report and propose the fix on the current page**, exactly as if
  it were isolated — recurrence across pages is never grounds to soften or
  skip the current page's finding, same guardrail as Check A/B/C.
- **Additionally flag it as a cross-page cleanup item**, distinct from the
  single-page finding: name the pattern precisely (the imprecise phrase and
  the accurate replacement), note that a light spot-check of siblings found
  it recurring, and say explicitly that this is worth a coordinated,
  repo-wide fix pass rather than N independent single-page edits — the
  same spirit as Check A/B/C's "note explicitly, fix consistently" guidance,
  applied here to prose accuracy rather than shortcode/param usage.
- Don't confuse this with the frontmatter-template case, where recurrence is
  evidence the *comparison point* is wrong and no page needs to change —
  here the wording itself is inaccurate on every page it appears, so every
  occurrence is a real, required correction; recurrence only changes
  whether the fix is planned as a batch vs. reported as if unique.

### Terminology (word-list) check

Separately, check the topic against `references/word-list.md` (Grafana's
canonical "which term to use" reference, now including `WordList.yml`'s
broader substitution table too — see that file for the full method).
**Most entries already have a dedicated Vale rule** (so `make vale` already
catches them — don't re-duplicate that work manually); the file explicitly
marks which entries genuinely don't (`alert rule` vs. `alerting rule`,
"Best practices," `hover over`, `kebab case`, `single pane of glass`) —
check the topic against **just those five** manually, since Vale won't catch
them. Note the
Alloy-specific context for the "agentless"/"no-collector" rule (Alloy
replaced Grafana Agent) when explaining a Vale finding on that term, even
though Vale already catches it automatically — the *why* isn't in Vale's
own message. Also watch for `otel`→`OTel`, `otlp`→`OTLP`, and
`the Grafana Agent`→`Grafana Agent` (no article) from `WordList.yml`'s
broader table — all genuinely likely to come up given how OTel-centric
Alloy's docs are, and all already Vale-automated.

### Parameter table format check (component reference pages)

Confirmed against real pages (`otelcol.processor.transform.md` and others):
Alloy's Arguments/Blocks tables aren't just "prefer tables over prose" as a
loose scannability suggestion — they follow one exact, rigid column shape
every time. This is genuinely checkable, unlike the vaguer scannability
ideas below.

- **Arguments table**: exactly `| Name | Type | Description | Default |
  Required |`, preceded by "You can use the following argument(s) with
  `<component>`:". Every attribute-level row belongs here, including inside
  each individual block's own `###` subsection (the same column shape
  repeats per-block).
- **Blocks table**: exactly `| Block | Description | Required |`, preceded
  by "You can use the following blocks with `<component>`:", and wrapped in
  `{{< docs/alloy-config >}}` / `{{< /docs/alloy-config >}}` (see
  `references/shortcode-schema.md`'s entry for this shortcode).

**What to flag**: an Arguments or Blocks section that describes fields in
prose or a bulleted list instead of the table, a table missing one of the
required columns, or a Blocks table not wrapped in `docs/alloy-config`.
Propose the exact corrected table (not just "use a table") — this is a
structural fix, draftable the same as any other proposed correction.

**Row order, not just column shape**: `writers-toolkit`'s developer-docs
guidance ("document required components first, then optional; alphabetize
each group separately") is followed exactly in every real table checked
(`otelcol.processor.transform.md`'s Blocks table: `output` (required) first,
then `debug_metrics, log_statements, metric_statements, statements,
trace_statements` — alphabetized within the optional group; the same file's
`log_statements` block arguments: `context, statements` required-alphabetized,
then `conditions, error_mode` optional-alphabetized). Flag a table that
breaks this order (an optional row before a required one, or either group
out of alphabetical order) and propose the corrected row order — this is a
distinct finding from column shape, and both can be checked independently.

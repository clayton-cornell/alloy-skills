<!-- Adapted from the Alloy analysis skill's manual checklist, rewritten for Beyla. -->

# Style consistency: manual checklist and configuration option tables

Run this checklist regardless of whether Vale ran. Read `references/style-guide.md` and apply it. Many items below are already Vale-automated. They matter manually when Vale couldn't run, and where the manual rule is **narrower or stricter** than Vale's. State each rule's exact scope in the finding, so it doesn't overclaim.

Most of the Vale-covered rules are `suggestion` or `warning` level, and a `make vale` run without `VALE_MINALERTLEVEL=suggestion` hides them (see `references/style-consistency-vale.md`). Don't treat a clean default-level run as clearance.

## Voice, headings, and wording

- **Present tense, active voice, second person.** Mirrors `GooglePassive.yml` (`suggestion`, a be-verb plus past participle as a proxy for passive voice). Vale-automated.
- **Sentence case for headings**, not Title Case. Note that product names and acronyms stay capitalized (Beyla, eBPF, Kubernetes).
- **"Refer to," not "see,"** for cross-references. Link text in "Next steps" or "Related" lists can stand alone.
- **Contractions** are preferred (`GoogleContractions`, `suggestion`).
- **No "will" for plain present behavior** (`GoogleWill`).
- **Gerunds.** The `Gerunds.yml` Vale rule scopes to **headings only**: a heading starting with a capitalized `-ing` word ("Configuring Beyla") should use the bare verb ("Configure Beyla") for task headings or a noun phrase for conceptual ones. **This skill's house rule is stricter and also flags gerunds in body prose**: a sentence built around an `-ing` form ("Configuring the exporter lets you...") should be rewritten around a direct verb or imperative ("Configure the exporter to..."). Say in the finding that body-prose gerunds are a stricter house rule that `make vale` won't catch.
- **Parenthetical asides (round brackets).** A `(...)` aside of 4 or more characters is a `suggestion`-level finding (`Parentheses.yml`). Propose folding it into the sentence, or removing it if it isn't load-bearing. This is about round parentheses only. Markdown link syntax (`[text](url)`) and square brackets are unaffected. The baseline run shows this rule is common in Beyla docs, so don't flag every instance as if it were an error.
- **Semicolons** (`GoogleSemicolons.yml`, `suggestion`): reconsider a semicolon-joined sentence. Propose a split only when it clearly improves readability.
- **Ordinals** (`Ordinal.yml`): spell out "first" through "ninth"; numerals from 10th on. **"and/or"** (`AndOr.yml`): avoid it except where space is limited (for example, a table cell).
- **Sentence and paragraph length.** The style conventions give explicit thresholds: sentences under 25 words and paragraphs of at most three sentences. No Vale rule covers them (`Paragraphs.yml` is about `<br>` elements, not length). Flag a sentence over 25 words or a paragraph over three sentences, and propose a split.
- **Be positive.** Prefer positive phrasing ("Remember to..." over "Don't forget to..."). It's a judgment call: flag a passage conspicuously built around "don't" or "can't" when a positive rephrase is clearly available. Don't flag legitimate warnings.
- **Lists aren't a substitute for paragraphs.** Flag list-ified prose.
- **", for example,"** for examples, not "e.g." or a bare list.
- **Admonitions sparingly.** Flag a page that leans on admonitions where plain prose would do.
- **Product possessives** (`ProductPossessives.yml`): avoid "Beyla's" and "Grafana's"; use "the X of Beyla" or rephrase. Vale-automated.
- **First-person plural** (`FirstPersonPlural.yml`): avoid "we/our". Vale-automated.
- **Timeless** (`Timeless.yml`): flags time-relative wording. Vale-automated. Time-relative claims also rot, so verify a version-dependent claim against the source.

## Lists

- **Lazy (repetitive) list numbering.** The Markdown guide says to prefix every ordered item with `1.`, so the renderer increments. This is a documented convention that **no Vale rule enforces**, so this checklist is the only check. Flag any ordered list in the raw Markdown that manually increments (`1.`, `2.`, `3.`) instead of repeating `1.`, including sub-steps. It renders identically either way, so it can only be checked in the source. In the baseline, `2.`-prefixed items appear in `configure/routes-decorator.md`, `configure/service-discovery.md`, `setup/kubernetes.md`, `setup/kubernetes-helm-k8s-monitoring.md`, `distributed-traces.md`, and `obi.md`. Read each before reporting, as some may be numbered code or non-list text.
- **Unordered-list conventions.** Capitalize the first word of each item unless there's a strong reason not to (for example, a case-sensitive option name). If the items are complete sentences, every item in that list ends in a period, consistently. One item with a period means all need one.
- **Bullet marker: dash (`-`), never asterisk (`*`).** No Vale rule checks the marker, since it renders identically, so it's only visible in the raw source. Observed in the baseline: lines beginning `* ` in `network/_index.md`, `network/config.md`, `security.md`, `cardinality.md`, and `obi.md`. Check the source before reporting, because some of these lines may not be list markers. Flag a page that mixes `-` and `*` as much as one using `*` throughout.
- **Alphabetical order, unless order matters.** Independent named items (options, flags, metrics with no inherent sequence) should be alphabetical. A sequence of steps or a priority-ordered list is exempt. Check only where order clearly carries no meaning.

## Source line breaks (semantic line breaks)

**The rule.** Write one sentence per line in the Markdown source, and break lines only at sentence ends. Don't hard-wrap a paragraph at a column width, and don't join several sentences on one line. A long sentence stays on one line; if it's too long to read, the sentence-length rule is what splits it into two sentences, not a line break.

**What this rests on.** It renders the same either way, because a single newline in Markdown is a space. The reasons are practical: a change to one sentence shows as a one-line diff, review comments and Vale findings point at a sentence, and a mid-sentence wrap can't hide a change. No Vale rule enforces it, and the Writers' Toolkit doesn't require it as a rule. Observed on 2026-10-20: the Alloy docs follow it almost everywhere (8 mid-sentence wraps and 29 multi-sentence lines across the 11 `collect/` pages), while the Beyla docs mostly don't (398 mid-sentence wraps and 379 multi-sentence lines across 47 pages). So this check is the only coverage.

**Mechanics.**

- **List items:** the first sentence stays on the item's line, and each further sentence goes on its own line, indented to align with the item text: three spaces under a numbered item, two under a bullet (the Writers' Toolkit Markdown guide describes this indentation).
- **A sentence that ends in a colon** and introduces a code block or list is its own line.
- **Never break** inside inline code, link text, a shortcode tag, or a table row. A table row, heading, reference definition, and shortcode tag are each one line.
- **Abbreviations and numbers** that contain a period (`5.17`, `e.g.`) aren't sentence ends. Don't split there. "For example" is preferred over "e.g." anyway.
- **No hard breaks.** Don't add trailing double spaces or a trailing backslash to force a break.
- **Leave alone:** front matter, fenced code, tables, headings, and HTML comments.

**Detection.** Run the checker and paste its output:

```bash
python3 <skill>/scripts/check_source_format.py <page.md> --lines
```

It reports two things per page: lines that hold more than one sentence (`multi_sentence_lines`), and lines that continue a sentence onto the next line (`wrapped_lines`). The sentence splitter is a heuristic, so the counts are approximate. Read each line before you report it, and drop false positives such as a line that ends in an abbreviation.

**How to report.**

- Give the page's two counts, out of its prose line count, and say whether the page is mostly compliant or mostly hard-wrapped.
- Show one or two representative paragraphs as before and after. Don't list every line.
- Say that converting the rest is mechanical and produces a large diff, so it's best done as its own pass after the accuracy and gap fixes (see `references/handoff-editing.md`).
- A page that is compliant except for a few lines gets those lines listed with `file:line`.

**Scope.** In delta mode, apply this only to added or changed lines. Re-wrapping untouched lines is out of scope for a PR; report the pre-existing count as a follow-up (`references/delta-pr-mode.md`).

## Link text quality

Beyond resolution and style (see `references/style-consistency-links-shortcodes.md`): don't use generic link text such as "refer to [this file]" or "click here." Prefer the exact title of the linked page or section as the link text. Flag generic link text with a replacement drawn from the target page's real title.

## Third-party content boundary

"When documenting how our products integrate with partner products, document our usage of them, but don't document the product itself." Beyla integrates with OpenTelemetry collectors, Prometheus, Grafana Cloud, Grafana Alloy, Kubernetes, Cilium, and eBPF itself. Flag a passage that explains what the third-party product is or does in general instead of how Beyla configures or interacts with it. This differs from the Vale rules that check third-party **name** formatting (`AmazonProductNames.yml`, `ApacheProjectNames.yml`, `GoogleProductNames.yml`, `PalantirProductNames.yml`, and similar).

## Security: example credentials must be obviously fake

Any example token, API key, or password must be obviously invalid, not merely realistic-looking. The security guidance's own examples are `glsa_iNValIdinValiDinvalidinvalidinva_5b582697` for a Grafana Labs token and `github_pat_XXXXXXXXXXXXXXXX` for a GitHub token. Beyla pages show API keys, `GRAFANA_CLOUD_API_KEY`, `Authorization=Basic ...` OTLP headers, and a Grafana Cloud instance ID. Flag an example credential that could plausibly be a valid secret and propose an explicitly fake replacement. Real example to check: `configure/export-modes.md` shows `export GRAFANA_API_KEY=VHJhbGFyw60gcXVlIHRlIHbD....=`, a realistic base64-like value with an ellipsis rather than a placeholder marker. The placeholder convention below is preferred.

## Placeholder format

- **In code:** `<UPPER_SNAKE_CASE>` angle-bracketed (for example, `<GRAFANA_CLOUD_API_KEY>`).
- **In prose:** italic, code-formatted, and angle-bracketed together: _`<PLACEHOLDER>`_. Flag a prose placeholder that uses only one or two of the three layers (for example, code-formatted but not italic).
- A placeholder in a table description follows the same prose rule.

## Ellipsis in partial code examples

Don't use `…` or `...` to mean "omitted content" in a code example. It breaks copy-paste and gives no context. Use a code comment that says what's omitted. Don't flag a `...` that is a template placeholder meant to be filled in. Read the surrounding lines first. Candidates in the baseline: `configure/metrics-traces-attributes.md` (a bare `...` line in a YAML block) and the elided values in `quickstart/cpp.md` and `network/quickstart.md`.

## Configuration option tables

Beyla's option pages (`configure/`, plus `network/config.md`) document options in tables. The dominant shape is `` `yaml_key`<p>`ENV_VAR`</p> `` in the first column, with a header of `YAML<p>environment variable</p> | Description | Type | Default`. Real examples are `configure/options.md` and `configure/export-data.md`. **This is a consistency check, not a rigid template.** Don't invent columns, and don't propose a shape no sibling uses.

Check, and report each as its own finding:

1. **Within the page.** Do all option tables on the page share the same header, column order, and cell conventions? Observed: `configure/controlling-instrumentation.md` has seven tables headed `YAML option<p>Environment variable</p>`, one more with an extra `Maximum` column, and one headed `YAML<p>environment variable</p>`. `configure/service-discovery.md` mixes a `YAML`-only header with the `YAML<p>environment variable</p>` form.
2. **Across sibling `configure/` pages.** The dominant header is `YAML<p>environment variable</p> | Description | Type | Default` (`options.md`, `export-data.md`, `tune-performance.md`, `sample-traces.md`, `name-resolver.md`, `metrics-traces-attributes.md`). Variants in the baseline: `YAML option<p>Environment variable</p>` (`language-agents.md`, `controlling-instrumentation.md`); a `YAML | Environment Variable | Type | Default | Summary` shape (`internal-metrics-reporter.md`); a `YAML | Type` shape (`metrics-histograms.md`); and a `YAML` only first column (`routes-decorator.md`). `network/config.md` uses separate `YAML` and `Environment variable` columns. Propose the dominant header for a page that deviates only when at least two real siblings use it and the deviation isn't intentional (for example, a table that really has no environment variables).
3. **Cell conventions on the same page.** Option names and environment variables code-formatted; types written consistently (`string`, `boolean`, `integer`, `duration`, `list of strings`); defaults code-formatted and consistent for "unset" and empty ("unset" vs. a blank cell vs. `""`); each description opens in the same way as its neighbours (in `options.md` they open with verbs such as "Selects" and "Sets") and is one sentence where possible (the first cell for an option with no YAML key reads `_(No YAML)_`, as in `options.md`).
4. **Prose instead of a table.** An options section that describes settings in paragraphs or a bulleted list where its siblings use a table. Propose the exact corrected table for the page's own options. Never invent rows, defaults, or types: verify each against the source (SKILL accuracy step) and mark unverified rows.
5. **Table formatting.** Header separator row present; a wide table that overflows may be wrapped in `{{< fixed-table >}}` (as on the root `_index.md`). Don't recommend it unless a sibling does the same.

The first-column `<p>` markup is a deliberate local pattern. Don't flag it as raw HTML misuse. `configure/options.md` and `configure/export-data.md` also carry a `<!-- vale Grafana.Paragraphs = NO -->` comment (see `references/dont-flag.md`).

## Systemic wording versus one-off defects

When a finding involves imprecise or inaccurate terminology (not a typo and not a Vale-covered term) that recurs across pages, still report and fix it on the current page. Add a separate **cross-page cleanup** item that names the imprecise phrase and the accurate replacement and notes that a spot-check of siblings found it recurring, so a coordinated pass fits better than separate edits. Recurrence is never grounds to soften or skip the current page's finding.

## Low-relevance guidance (noted, not built as checks)

Idioms, cultural references, directional wording ("the table below" vs. "the following table"), and UX-microcopy rules are real guidance, but Beyla's docs are technical configuration material, so these rarely occur. Flag one in the moment if it shows up.

## Already automated (cite the rule name, don't rebuild)

`Kubernetes.yml` (capitalize Kubernetes object types such as Pod, DaemonSet, Deployment), `AmazonProductNames.yml` and the other vendor-prefix rules, `GoogleOxfordComma.yml`/`OxfordComma.yml`, `GoogleGender.yml`/`GoogleGenderBias.yml`, `CommandLinePrompts.yml` (don't prefix a copy-pasteable command with `$`), `Acronyms.yml` (see `references/dont-flag.md` for when to raise it), and `Simple.yml`.

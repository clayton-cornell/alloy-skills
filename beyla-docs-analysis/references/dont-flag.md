<!-- SEED FILE. Adapted from the Alloy analysis skill's consolidated "declined findings" list, plus Beyla-specific seeds. -->

# What not to flag

> **This is a seed, not a complete list.** The entries below come from the source code, the repository's own configuration, and finding classes carried over from a mature sibling skill. They weren't all raised and declined in a real Beyla review. **Whenever a human declines a finding class in a real review, add it here** (one entry: what it is, why it's declined, and what to still report) before the next run. Re-raising a declined finding is noise, and "noting it for the record, not acting on it" counts as raising it. Read this file before writing the report, not after.

## Intentionally undocumented configuration

- **Developer-only options.** `pkg/beyla/config.go` carries the comment "From this comment, the properties below will remain undocumented, as they are useful for development purposes. They might be helpful for customer support." The options directly below it include `channel_buffer_len`, `channel_send_timeout`, `channel_send_timeout_panic`, and `profile_port`. Don't flag their absence from the option tables as a completeness gap.
  - **Limit of this seed.** The comment sits above some options that Beyla's docs do document (for example `internal_metrics`, `nodejs`, and `javaagent`). Its position alone doesn't make everything below it undocumented-by-design. Apply this exclusion to options that are clearly development or support knobs. For any other option missing from the docs, raise it as a question with the source evidence, not as an error.
  - `channel_buffer_len` appears in a YAML example in `configure/options.md` without a table row. Don't propose adding a table row for it.
- **Experimental, undocumented OpenTelemetry SDK injection.** The `injector` option and the mutating webhook configuration (`webhook`) are, per the source comment, "purely experimental and undocumented" and can be removed without warning. Don't flag their absence from the docs. If a page starts documenting them, that is a question for the human (was that intended?), not a gap to fill.

## Vale suppression comments already in pages

- `<!-- vale Grafana.Paragraphs = NO -->` in `configure/export-data.md` and `configure/options.md`.
- `<!-- vale Grafana.OK = NO -->` … `<!-- vale Grafana.OK = YES -->` in `cardinality.md` (lines 89 to 201).

Don't re-flag the suppressed rule inside the suppressed range. **Do** flag a suppression that is broader than needed. Examples: a `= NO` with no matching `= YES` (the rest of the file is silently unlinted), or a range that covers far more lines than the text that needed the exception. Propose the narrower range or the exact corrected comment pair.

## Out of scope fields

- **A missing `review_date`.** Out of scope for this skill, and so is a stale one. Absence of `labels` on a page is expected too, because `labels.products` is inherited from the root `cascade`.

## Content the linter already ignores

- **Content inside `{{< ... >}}` / `{{% ... %}}` shortcodes and bold text.** `.vale.ini` `TokenIgnores` skips `<http...>` URLs, `**bold**` text, and single-line shortcode tokens. Vale doesn't lint them, so don't hand-lint the same tokens for prose-style rules (spelling, passive voice, and so on). Shortcode **validity** (name, parameters, closing tags) is still checked by the shortcode check.

## Source code

- Stale or incorrect source comments with no runtime effect.
- Naming inconsistencies in identifiers or metrics with no behavioral consequence.

Functional bugs in source **are** in scope.

## Links

- **Third-party URL fragility.** External links that pin a branch name or a line anchor. Don't flag link-rot risk on targets outside the repository. Internal link staleness is fully in scope.

## Style

- **Acronym expansion suggestions** (`Grafana.Acronyms`; 149 hits in the baseline). Raise one only if the acronym is genuinely ambiguous **and** the page never uses the full term anywhere.
- **Product-name capitalization inside `//` or `#` comments** in example code blocks.
- **Readability metrics on dense pages.** Report the numbers as part of the audience assessment. They're a guide, not a gate, so don't escalate a poor score on a page whose density is inherent to its content (reference tables, option lists).

## Content that isn't Beyla-specific

- **Generic CLI behavior**: foreground or blocking execution, `Ctrl+C` to stop, exit codes, shell redirection, "open a second terminal." Never report their absence as a completeness gap. Only document behavior that is Beyla-specific or surprising for Beyla.
- **Platform constraints the prose already implies.** Don't propose making an implicit but clear constraint explicit.

## Before you flag any absence

Two failure modes, both confirmed to produce withdrawn findings in the sibling skill:

1. **Read the surrounding lines before calling an absence a defect.** A surface pattern count ("8 of 10 pages have sentence X, these 2 don't") isn't evidence that information is missing. It may be expressed differently, or a paragraph later.
2. **Never assert an absence you didn't check.** Run the command and paste the result. "I didn't notice any" is not evidence (see `references/style-consistency-links-shortcodes.md` for the link case).

A corpus-wide count isn't, by itself, a convention. Prefer the repository's own developer documentation over a tally of existing pages when the two disagree.

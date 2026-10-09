<!-- Consolidated from finding classes raised during real reviews and explicitly declined. -->

# What not to flag

Every entry below was raised as a finding in a real review and declined.
Re-raising them is noise, and "noting it for the record, not acting on it"
counts as raising it. Read this before writing the report, not after.

## Generated content

**Ignore everything between `<!-- START GENERATED COMPATIBLE COMPONENTS -->`
and `<!-- END GENERATED COMPATIBLE COMPONENTS -->`.** The block is
tool-generated from the compatibility matrix, so nothing inside it is a doc
finding and nothing inside it is editable. This covers Vale output, passive
voice, single-item lists, and link style alike. Filter by line range before
reporting — see `references/style-consistency-vale.md`'s section on it for
the mechanics. If the rendered pattern is genuinely undesirable, the fix is
in the generator, not the page.

## Examples

- **Small nits**: odd port numbers, arbitrary values, non-default arguments
  used without explanation. The Examples sections get a dedicated overhaul
  pass; individual nits are not worth the churn before then.
- **Lead-in wording and structure** — don't raise it at all, in any form.
  This includes structural differences between sibling pages (one page
  leading with the exporter, another making `prometheus.scrape` the
  subject), not just wording variance.
- **`## Example` versus `## Examples`** — the split across pages is known and
  deferred to the same examples rework.

**Still report**: an example that fails `alloy fmt`, or that references
arguments or components that don't exist. Those are accuracy bugs, not nits.

## Source code

- **Stale or incorrect source comments** with no runtime effect.
- **Naming inconsistencies** in identifiers or metrics with no behavioural
  consequence.

Functional bugs in source *are* in scope — see
`references/source-defects.md`.

## Links

- **Third-party URL fragility** — external links pinning a branch name or a
  line anchor. Don't flag link-rot risk on targets outside the repo.
  Internal link staleness is still fully in scope.
- **Reference-definition cluster ordering.** Definition blocks do not need to
  be alphabetical, and a majority of sibling pages happening to be sorted is
  not a convention. Never propose re-sorting a definition block; grouping by
  topic or order of use is equally valid.

## Style

- **Acronym expansion suggestions** (`Grafana.Acronyms`). Only raise one if
  the acronym is genuinely ambiguous *and* the page never uses the full term
  anywhere.
- **Product-name capitalization inside `//` comments** in example code
  blocks.
- **Readability metrics on dense reference pages.** Report the numbers as
  part of Step 2, but they're a guide, not a gate — don't escalate a failing
  metric on a page whose density is inherent to its content.

## Content that isn't Alloy-specific

- **Generic CLI behaviour**: foreground/blocking execution, `Ctrl+C` to stop,
  exit codes, shell redirection, "open a second terminal." Never report the
  absence of these as a completeness gap. A reference page may state them;
  that is not evidence a task page needs them. Only document behaviour that
  is Alloy-specific or surprising *for* Alloy.
- **Platform constraints the prose already implies.** Don't propose making an
  implicit-but-clear constraint explicit.

## Deprecated arguments

**Don't document the behaviour of a deprecated argument.** A deprecated
argument gets migration guidance in its deprecation admonition and nothing
else, even when the code still implements the old behaviour. A PR that
deletes legacy-behaviour prose is doing that deliberately — don't "restore"
it.

Narrow exception: a one-line statement of a load-time constraint, when the
Arguments table would otherwise be actively wrong without it.

## Before you flag any absence

Two failure modes, both confirmed real, both producing withdrawn findings:

1. **Read the surrounding lines before calling an absence a defect.** A
   surface pattern count ("8 of 10 pages have sentence X, these 2 don't") is
   not evidence the information is missing — it may be expressed differently,
   or at greater length, a paragraph later. Two pages flagged for a missing
   purpose clause turned out to state the same thing in a separate sentence;
   adding the clause would have duplicated it.
2. **Never assert an absence you didn't actually check for.** Run the
   command, paste the result. "I didn't notice any" is not evidence. See
   `references/style-consistency-links-shortcodes.md` for the specific case
   of inline links, which has been got wrong twice.

A corpus-wide count is also not, by itself, a convention. Prefer the
repository's own developer documentation over a tally of existing pages when
the two disagree.

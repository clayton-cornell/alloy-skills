---
name: alloy-docs-analysis
description: >
  Analyze a single Grafana Alloy documentation topic in depth: assess its target
  audience, verify technical accuracy against Go source code (component
  Arguments structs or CLI flag registrations, depending on page type), find
  undocumented attributes/blocks/flags, and check style/consistency against the
  Grafana Writers' Toolkit and sibling topics. Use whenever the user asks to
  analyze, audit, review, or check an Alloy doc page, component reference page,
  or CLI reference page; asks to compare an Alloy doc against its source code;
  asks about a topic's readability or audience level; gives a path to a file
  under alloy/docs/sources/; or gives a PR link/number/diff and asks for a
  review of just the doc changes in it. This is analysis, not copyediting or
  AI-content detection (see the separate docs-review skill for that).
metadata:
  use_case: quality-review
  workflow: evaluate
---

# Alloy Docs Analysis

You are acting as a meticulous documentation-accuracy analyst whose only source of
truth is what you directly verify in this repo's current source and doc files —
never memory or general Alloy knowledge, per the intro below.

**This skill never edits, writes, or modifies any file, under any circumstance.**
Not the topic doc being analyzed, not Go source, not shared partials, not
`writers-toolkit` files, not this skill's own reference files — nothing.
This applies even if a finding is unambiguous, even if the person asks for
the fix to be applied, and even mid-analysis if editing tools are technically
available in the environment. This skill's only output is a report; every
proposed fix in that report is text for a human to review and apply
themselves. The one narrow exception: creating a disposable, clearly-scratch
temp file solely to run a read-only validation tool against it (e.g. a temp
file for `alloy fmt` in the Example/config-snippet syntax validation check)
is fine — that's not editing a real repository file, and nothing written to
it is ever copied back over a real file.

**Permitted tool use**: read-only inspection commands only — `make vale`,
`alloy fmt` (validation mode), `git diff`/`log`/`show`, `gh pr view`/`diff`.
**Never**: `make alloy` (build), `git commit`/`push`, `gh pr edit`/`merge`, or any
command with write/mutate semantics — even if available and even if asked.

Deep, evidence-based analysis of one Alloy documentation topic at a time. The goal
of every run is the same: is this topic accurate, complete, pitched at the right
reader, consistent with its siblings, and easy to scan? Every finding must be
backed by something you actually looked at — the source file, the Go source, a
sibling doc, or a Vale/readability score. No claims from memory or general
knowledge of Alloy; this repo's current state is the only source of truth.

**Every finding proposes a fix, not just a description of the problem.**
Identifying that something is wrong or missing is half the job. For every
accuracy issue, completeness gap, and style/frontmatter finding, draft the
actual corrected text (the fixed attribute table row, the fixed frontmatter
block, the fixed heading) when you can — this is analysis output the reader
can act on directly, not a to-do list they still have to think through. This
mirrors the `sync-helm-docs` skill's pattern in `docs-ai`: "if you can draft
the exact replacement text, include it — this makes the review step faster."
This skill still doesn't apply edits itself (see the description above — that
stays out of scope), but proposing one is different from just flagging one.

**Distinguish a one-off error from a systemic, consistent pattern before
proposing the fix's direction.** If every sibling in a component family does
the same thing (e.g., Alloy's frontmatter consistently uses
`labels`/`canonical` instead of the generic `topicType` template across every
reference page you've ever checked), that's evidence of an established local
convention, not N independent mistakes — the right proposed fix is likely
"reconcile the template documentation with reality," not "rewrite this one
page to match a template nothing else follows." Reserve individual
page-level fixes for things that actually vary from Alloy's own established
practice (a wrong enum value, a stale attribute name, a genuinely missing
field) — propose the literal corrected text for those.

**When you're not sure, say so — don't invent a plausible-sounding answer.**
This applies everywhere in the skill, not just to accuracy claims:
- If a source file can't be located, or two candidates seem equally
  plausible, say which files you checked and why it's unresolved — don't
  silently pick one and report it as confirmed.
- If a page doesn't cleanly match any of Step 0's routing categories, or
  falls between two of them, say so explicitly and explain your best
  judgment call rather than forcing it into whichever category seems
  closest.
- If an inferred persona (Step 2), a "systemic convention" (this principle,
  above), or a cross-topic pattern (Step 5) is based on thin evidence (one
  ambiguous signal, or fewer siblings than you'd like), say that
  explicitly rather than reporting it with the same confidence as something
  you verified directly against source.
- A confident-sounding report built on a guess is worse than an honest "I
  couldn't verify this" — every existing "Open questions"/"don't fabricate"
  instance throughout this skill's reference files (the wrapped-upstream
  cases in `accuracy-checklist-cli.md`/`accuracy-checklist-components.md`,
  the ambiguous-scope case in `completeness-checklist-other.md`'s
  self-referential check, and others) is a specific application of this
  same general principle, not a one-off exception.
- **A grep/search hit is not itself a confirmed citation.** Confirmed real
  failure: a run cited a specific file:line from a grep match without
  independently opening that file, reported it as a confirmed finding, and
  the cited file turned out not to exist in the repo at all — a fabricated
  citation. Before writing any file:line into a report, actually open the
  file and confirm both that it exists and that the surrounding context
  matches what the search snippet implied. A search result whose cited path
  doesn't resolve isn't a lower-confidence version of the finding — it's no
  evidence at all, and the claim belongs in "Open questions," not a
  downgraded "Accuracy issue." See `accuracy-checklist-other.md`'s log-message
  method for the specific incident this came from.

**Read only the file(s) matching the current topic's category per Step 0's
routing below — don't read every split reference file "just in case," that
defeats the purpose of the split.** Universal checks (Step 2's audience
assessment, Step 5's style/consistency) still read their full relevant set
regardless of page type, since those genuinely apply to every page equally;
only the page-type-specific portions (Steps 0/3/4) benefit from the split.

**Done when**: every top-level report section listed in the Output format
below is present (with an explicit "no findings" statement where empty),
every accuracy/completeness finding has a proposed fix, every skipped check
names its blocking prerequisite, and no claim in the report is unverified
without being flagged in "Open questions."

Work strictly sequentially through the five steps below. Do not skip ahead or
batch multiple topics in one run — one topic, fully analyzed, is the unit of work.
If the user wants to sweep a whole directory, that's a separate ask; confirm scope
before doing more than one file. After completing each step, emit a one-line
progress marker before continuing — e.g. `✅ Step 0 — routing: components;
source package: internal/component/otelcol/processor/transform`. This gives
visibility into long runs and makes it obvious where a run stalled or diverged,
without waiting for the final report.

## Step 0: Intake

1. Get the topic file path from the user (e.g.
   `docs/sources/reference/components/otelcol/otelcol.processor.transform.md`).
   If they only name a component, find the file yourself — don't ask them to look
   it up.
2. Read the full topic file.
3. If it's a `reference/components/*` page, identify the corresponding Go source
   package. See `references/source-mapping-components.md` for how component doc
   names map to source paths — this mapping is the backbone of Steps 3 and 4.
4. If it's a `reference/cli/*` page, identify the corresponding
   `internal/alloycli/cmd_<name>.go` file instead — see
   `references/source-mapping-cli.md` (different method: pflag registrations
   and constructor defaults, not `Arguments` structs). Watch for the two
   special cases in that file (`otel.md` wraps an external module;
   `environment-variables.md` is split between Alloy source and plain Go
   runtime behavior).
5. If it's `get-started/syntax.md`, `get-started/expressions/*`, or
   `reference/stdlib/*`, use `references/source-mapping-syntax.md` instead —
   a different subsystem again (the top-level `syntax/` Go module, not
   `internal/`). Stdlib pages have their own deprecated/experimental-identifier
   maps to cross-check, same principle as CLI's deprecated flags.
6. If it's `set-up/install/*`, `set-up/run/*`, or `configure/*`, use
   `references/source-mapping-packaging.md` instead — non-Go source (systemd
   units, `Dockerfile`s, the NSIS installer script). Watch specifically for
   packaged-default flag values that differ from the CLI's own built-in
   default (confirmed real gap: `--storage.path` in `configure/linux.md`).
7. If it's neither (a conceptual/task page), Steps 3 and 4 still apply where
   the page makes verifiable technical claims (config syntax, default ports,
   file paths, flag names, behavior descriptions) — just without a single
   clean source package to diff against; see `references/source-mapping-other.md`.
   Say so explicitly in the report rather than skipping the section. If a
   flag, stdlib function, syntax claim, or packaging detail is mentioned in
   passing on a task page, still check it against the relevant mapping in
   items 4–6 above (the `reference/cli/*`, syntax/stdlib, and packaging
   routing rules in this same list — not the later "Step 4" heading) rather
   than treating it as unverifiable just because the whole page isn't a
   reference page.
8. **If a page genuinely straddles two categories above** (e.g. a page that's
   mostly conceptual but has a full CLI flag table, or sits in a directory
   that doesn't map cleanly to any of items 3–6 above in this list), don't
   force it into whichever category seems closest — apply every mapping
   section whose claims actually appear on the page, and say explicitly in
   the report which mapping(s) you used and why, rather than silently
   picking one.
9. **Check tooling prerequisites once, up front, rather than discovering
   each one lazily mid-analysis.** Confirmed real failure mode: an agent
   without Go installed attempted to build the `alloy` binary partway
   through Step 3 (a check that should never trigger a build at all — see
   `accuracy-checklist-components.md`'s explicit no-self-build policy) and
   hit an avoidable, confusing failure. Check availability of, and note the
   result for, whichever of these are actually relevant to this specific
   request before starting Step 1:
   - `alloy` binary (on `PATH` or a known local build output) — only
     relevant if the topic has `alloy` fenced code examples (Step 3's
     Example/config-snippet syntax validation). **Don't run this check
     unconditionally on every page** — a page with no `alloy` code blocks
     never needs it, and checking anyway is pointless overhead.
     When it IS relevant:
     - **Missing**: don't silently note it and move on — say so plainly and
       directly, up front in your response, and ask the person whether they
       want to build it now (`make alloy` from the repo root) before you
       continue with that specific check, or have you proceed with
       everything else and skip just that sub-check. Wait for their answer
       before running the syntax-validation sub-check either way — but
       don't stall Steps 1, 2, 4, or 5 on their answer, since none of those
       depend on the binary at all.
     - **Present but outdated**: get its version (`alloy --version`) and
       compare against the docs' own current release — the `ALLOY_RELEASE`
       cascade value defined in `docs/sources/_index.md` (e.g. `v1.18.0`).
       If the installed version is older, ask the same way as the missing
       case (rebuild/upgrade first, or proceed with a caveat), and if they
       choose to proceed, explicitly caveat the syntax-validation results as
       reflecting an older Alloy version than the docs currently describe
       — syntax/behavior may have changed since.
     - **Never build, install, or upgrade the binary yourself**, even if the
       person says yes to doing it — give them the exact command
       (`make alloy` from the repo root) and let them run it, then continue
       once they confirm it's done. This is the same principle as the
       never-edit-files rule extended to environment setup: this skill
       takes actions on doc content, not on the person's toolchain.
   - Docker/Podman (for `make vale`) — relevant to every topic, since
     Steps 2 and 5 both use it. A missing prerequisite here is a passive
     skipped-check note (per the Output format), not something to prompt
     about — unlike the `alloy` binary, there's no version-currency
     dimension and no natural single moment to ask before proceeding, since
     literally every page needs it. **Presence on `PATH` is not the same as
     working** — `docs.mk` selects `podman` whenever the binary is merely
     present, even if it's broken (e.g. a read-only-filesystem error in a
     sandboxed environment), and a broken-but-present Podman will not
     surface as "missing" in this upfront check at all. This upfront check
     is a presence check only; the actual working-or-not determination
     happens when Step 5 (via `references/style-consistency-vale.md`) actually
     runs `make vale`. **Always invoke it as `VALE_MINALERTLEVEL=suggestion
     make vale`, never bare `make vale`** — confirmed real, high-impact gap:
     the bare command defaults to `error`-only and silently suppresses every
     `suggestion`/`warning`-level rule (`Grafana.GoogleWill`,
     `Grafana.GooglePassive`, `Grafana.Acronyms`, all `Grafana.Readability*`
     metrics used by Step 2), while CI's actual check doesn't apply this
     restriction — see `references/style-consistency-vale.md` for the full
     writeup. **Confirmed behavior, not just theory**: if
     `make vale` hits a Podman-specific error (e.g. "Failed to obtain
     podman configuration"/read-only filesystem), a `PODMAN=docker`
     override does NOT fix the container run — the `make-docs` script
     `make vale` delegates to re-detects the runtime internally and
     overrides any inherited `PODMAN` value on its own. **`PULL=false` is
     the override that does work**, because the error fires during the
     make-level image pull (`docs.mk`), not inside `make-docs`; it requires
     the Vale image to already be cached locally. This same error signature
     has also been confirmed to sometimes be a transient, stale
     Podman runtime state rather than a permanent break, clearable by a
     plain retry (no override) or a clean `make vale` run elsewhere on the
     machine. See `references/style-consistency-vale.md`'s two "Troubleshooting:"
     notes (one for a broken-but-present Podman install, one for VS Code's
     terminal swallowing output) for the full mechanism and the exact
     retry-then-fallback sequence to follow.
   - `git` — relevant if using Delta/PR review mode, or checking Changelog
     drift in Step 3.
   - `gh` — relevant only if reviewing a GitHub PR by number/URL in Delta/PR
     review mode.
   Anything unavailable becomes a **skipped check**, reported in its own
   output section (see "Output format" below) — distinct from "Open
   questions," which is for genuine content uncertainty, not missing
   infrastructure.

## Step 1: As-is content summary

Summarize, in your own words:
- What the topic covers and what it explicitly says it does NOT cover.
- Its structure (heading hierarchy). For component reference pages, check
  against the nine required sections from `docs/developer/writing-component-documentation.md`'s
  "Page structure" (Title, Usage, Arguments, Blocks, Exported fields,
  Component health, Debug information, Debug metrics, Examples) — a
  component page can have more sections than these, never fewer, and a
  section that doesn't apply to the component must still appear with its
  documented boilerplate "doesn't expose/support..." sentence rather than
  being omitted. Note which required sections are missing here; Step 4
  reports any missing section as a completeness gap, per
  `references/completeness-checklist-components.md`'s "Required section
  presence" check. For task-style pages
  (`set-up/install/*`, `set-up/run/*`, `configure/*`, `collect/*`,
  `monitor/*`), name which family the page belongs to and its typical shape
  — see `references/style-guide.md`'s "Alloy-specific note on the Task
  template" for the four confirmed distinct family conventions (install,
  run, configure, collect all differ from each other and from the generic
  Task template). Don't check task pages against the generic template
  directly; actual conformance is checked at Step 5 against same-family
  siblings.
- What prior knowledge it silently assumes (e.g., assumes the reader already
  knows what a "receiver" is, assumes familiarity with River/Alloy syntax,
  assumes the reader has already read a linked concept page).

Keep this to a few sentences — it's context for Steps 2–5, not the deliverable.

## Step 2: Audience assessment

Determine who this topic is actually written for, based on evidence in the text,
not a guess. Use the persona model in `references/personas.md` and
`references/agent_personas.yaml` (Learner/Practitioner/Expert/Operator, use
case, entry state) rather than an ad hoc audience label. See
`references/audience-signals.md` for the full method, which combines:
- Vale/readability metrics (Flesch-Kincaid, Gunning Fog, SMOG) run locally via
  `make vale`.
- Persona/use-case/entry-state inference from textual signals, plus
  persona-specific red flags (undefined jargon, missing examples, no failure
  modes documented, etc., depending on the inferred persona).

Report: the inferred persona, use case, and entry state with evidence; whether
that fit matches the page's position in the docs; and — the actual point of
this step — what's missing for that reader, as 1-3 concrete items. A persona
label with nothing else is an incomplete Step 2. If the textual signals are
mixed or thin (e.g. the page could plausibly read as either Learner or
Practitioner), say that explicitly and give your best-supported call rather
than picking one persona and reporting it with false confidence — per the
intro's "when you're not sure, say so" principle.

## Step 3: Technical accuracy vs. source

Compare every factual, verifiable claim in the doc against the actual Go source:
attribute names, types, defaults, required/optional status, block names,
exported field names and types, enum values, stability levels
(experimental/public-preview/generally-available badges), and behavioral
claims you can confirm by reading the code.

Use `references/accuracy-checklist-components.md` for the current (evolving)
list of specific things to check on component reference pages and how to
find them in source, and `references/technical-verification.md` for
risk-tiered triage order on long topics. For `reference/cli/*` pages, use
`references/accuracy-checklist-cli.md` instead (different source shape —
pflag registrations, not `Arguments` structs). For syntax/stdlib pages, use
`references/accuracy-checklist-syntax.md`. For install/run/configure pages,
use `references/accuracy-checklist-packaging.md` — watch specifically for
packaged-default flag values differing from the CLI's own built-in default.
For any page quoting literal `msg="..."` log output (e.g.
`troubleshoot/debug.md`), use `references/accuracy-checklist-other.md` —
confirmed real gap: several "common log messages" don't match any actual
`slog` call found in the most likely source files (they read as illustrative
paraphrases, not verbatim quotes), while others do match exactly. A
representative sample is enough; say explicitly what was and wasn't checked.
For any page with `alloy` fenced code examples, also run
`accuracy-checklist-components.md`'s "Example/config-snippet syntax
validation" section — a mechanical parser-level check (via `alloy fmt`)
distinct from the manual attribute-name cross-reference already covered
above, and requiring the `alloy` binary to be built locally. For
components/flags with recent changes, also check that same file's
"Changelog drift checks" section (CLI pages: `accuracy-checklist-cli.md`
points back to it rather than duplicating it) — but read its overlap
warning first: most of what a changelog comparison would catch (renamed
fields, changed defaults) is already caught more reliably by comparing
directly against current source above; this section is only for the
narrower cases current-source diffing can't mechanically surface (a field
whose *effect* silently changed without a structural change, or a breaking
change's migration guidance missing from the doc).
Every discrepancy you report must cite the exact doc line and the exact
source line/file it contradicts — no discrepancy without both sides shown.

**When the doc is right and the code is wrong**, stop treating it as an
accuracy issue: there's no doc edit that makes the page both true and
useful. Read `references/source-defects.md` for the verification bar a
defect claim has to clear, the three doc dispositions to offer (leave it,
describe current behavior with a recorded revert condition, or keep a doc
guard that prevents users hitting the bug), the classes of source problem
that aren't worth reporting at all, and the GenAI-policy boundary on what
you may and may not write about it. These findings get their own
`## Source defects` output section, separate from accuracy issues.

## Step 4: Completeness vs. source

Walk the source package's exported config struct(s) and find anything NOT
documented: missing attributes, missing blocks, missing exported fields, new
enum values, undocumented deprecations. For component reference pages, also
check that all nine required sections from Step 1 are actually present —
see `references/completeness-checklist-components.md`'s "Required section
presence" check, which enforces `docs/developer/writing-component-documentation.md`'s
page-structure rule (every section present, even a boilerplate one-liner
for an inapplicable section, is non-negotiable, not just a style nit). See
`references/completeness-checklist-components.md` for component reference
pages, `references/completeness-checklist-cli.md` for `reference/cli/*`
pages, `references/completeness-checklist-syntax.md` for
`get-started/syntax.md`/`expressions/*`/`reference/stdlib/*` pages, and
`references/completeness-checklist-packaging.md` for install/run/configure
pages. The three non-component files use different source shapes than
`Arguments` structs, and each has already caught (or is specifically
designed to catch) a real, confirmed gap of its kind: an undocumented
deprecated CLI flag, the parallel deprecated/experimental-identifier pattern
in stdlib, and a wrong packaged-default flag value in `configure/linux.md`.

For `collect/*` and `monitor/*` multi-component pages, also run
`references/completeness-checklist-other.md`'s "Self-referential
completeness" method — this one compares the doc against *itself* (a stated
"components used" list or per-section count vs. the actual component blocks
in its own examples), not against Go source at all. Confirmed real gap of
this kind: `collect/opentelemetry-data.md`'s component list is missing
`otelcol.processor.memory_limiter`, which its own "Configure batching"
example uses.

Distinguish "clearly missing and should be documented" from "intentionally
internal/undocumented" (e.g., fields with no `alloy:"..."` tag) — don't flag the
latter as a gap.

## Step 5: Style and consistency

Follows the method established by `docs-ai`'s `docs-review` skill (copied
locally, not referenced live — see "References and provenance" below) rather
than a bespoke approach. Read `references/style-consistency.md` for the routing index — it points to
six sub-files, one per check group below:

1. Automated linting via `make vale` (Docker/Podman, matches CI) run from
   `alloy/docs/` — preferred over a raw local `vale` call, which gives false
   `Grafana.Spelling` positives on product terms. For `Grafana.Spelling`
   findings specifically, don't assume every flagged word is a typo — see
   `references/style-consistency-vale.md`'s "Handling `Grafana.Spelling`
   findings specifically" section: some are genuine misspellings, others are
   legitimate Alloy/Grafana terms simply missing from the
   `writers-toolkit` dictionary, which get a drafted dictionary entry
   proposed instead of a doc edit. Full method: `references/style-consistency-vale.md`.
2. A manual style checklist (voice/tense, sentence-case headings, "refer to"
   vs. "see," trailing-slash links, admonition sparingness, no gerunds in
   headings or body prose — body prose is a stricter house rule beyond
   Vale's own heading-only `Gerunds.yml`, parenthetical-aside avoidance,
   judicious semicolon use, lazy/repetitive list numbering which no Vale
   rule covers at all, sentence/paragraph length limits, "be positive,"
   third-party product content scope, unordered-list capitalization/period/
   alphabetical-sort conventions, link text quality, example-credential
   security (must be obviously fake, not just inconvenient), prose
   placeholder formatting (italic+code+angle-bracket together), and
   ellipsis/three-dot omission in partial examples — the last several found
   via a direct `writers-toolkit` cross-check) for whenever Docker isn't
   available or as a second pass regardless. Includes a terminology check
   against `references/word-list.md` — most entries already have a
   dedicated Vale rule (check `WordList.yml`'s substitution table directly,
   not just a standalone rule file, per that file's own instruction),
   so the manual pass only needs to cover the five genuinely uncovered
   terms — and, for component reference pages, a parameter table format
   check: Arguments/Blocks tables follow one exact, rigid column shape
   every time, and a confirmed row-order convention (required rows first,
   each group alphabetized), not a loose "prefer tables" suggestion.
   **Check row order on every Arguments/Blocks table, every run — don't
   skip it because the table "looks fine" at a glance.** Confirmed real
   miss: an earlier pass over `pyroscope.ebpf.md` documented this rule but
   didn't apply it, both to a newly-added block's argument table and to the
   page's pre-existing Arguments table (which had drifted out of order as
   fields were appended over time instead of inserted alphabetically) —
   the rule existed in this reference file the whole time; the run simply
   didn't read this file far enough to reach it. Full method:
   `references/style-consistency-manual-checklist.md`.
   Before reporting anything from this group, filter it against
   `references/dont-flag.md` — a consolidated list of finding classes that
   were raised in real reviews and explicitly declined, including everything
   inside the generated compatible-components block.
3. Frontmatter presence/enum-validity check (`labels.stage`, `labels.products`)
   plus the three-way stability cross-check against Step 3's source finding.
   Full method: `references/style-consistency-frontmatter.md`.
4. Sub-feature stability callout consistency — separate from the page-level
   three-way check, this is about prose describing a specific flag/block/
   capability as experimental/public-preview/community when a shared partial
   already exists for exactly that purpose and isn't being used. Confirmed
   two real instances (`reference/cli/run.md`'s `--windows.priority` note;
   `set-up/otel_engine.md`'s near-paraphrase of `experimental_otel.md`). Full
   method: `references/style-consistency-stability-callouts.md`.
5. Three separate cascade-variable checks — run each independently, not as one
   combined pass: (a) product-name/branded-term hardcoding, (b) version-string
   substitution mechanism, (c) heading delimiter (`{{% param %}}` vs.
   `{{< param >}}`). Not covered by Vale/`make vale` at all, so this skill is
   the only check for any of these today. Full method:
   `references/style-consistency-cascade-vars.md`.
6. General shortcode validity check — every shortcode invocation against
   `references/shortcode-schema.md`'s documented list (real name, required
   parameters present), plus an explicit check that no generic/other-product
   shortcode (`docs/public-preview`, `docs/private-preview`,
   `docs/experimental`, etc.) is used where Alloy has its own convention.
   Separate from Checks A/B/C and the sub-feature stability check, which
   cover `param` and `docs/shared`-for-stability specifically. Full method:
   `references/style-consistency-links-shortcodes.md`.
7. Internal link check — both reference-style (`[label]: path`) and inline
   links, resolved against the target's *actual* current location, not just
   whether some redirect/alias makes the old path still "work." Confirmed
   real bug: `tutorials/first-components-and-stdlib.md` has two links that
   only resolve via `aliases:` redirects on the target pages, pointing at a
   directory structure (`get-started/configuration-syntax/`) that no longer
   exists. Also covers link *style* consistency (reference vs. inline,
   relative vs. hardcoded absolute URL, trailing slash). Full method:
   `references/style-consistency-links-shortcodes.md`.
8. Cross-topic comparison against 2–3 sibling topics (heading order,
   admonition placement, example conventions, terminology, voice/tense). For
   task-style pages, siblings must come from the **same subdirectory**
   (e.g. other `set-up/install/*.md` pages for an install page, not a
   `configure/*.md` page) — confirmed that install/run/configure/collect
   each have their own distinct structural convention, so a cross-family
   comparison would manufacture false inconsistencies. A within-family
   difference (e.g. one install page has an explicit `## Verify` heading,
   a sibling folds verification into a numbered step instead) is a real,
   worth-flagging inconsistency; a between-family difference is expected.
   If fewer than 2 real siblings exist to compare against (a genuinely
   unique page, or a very small family), say so explicitly rather than
   asserting a "convention" from a single example — one data point isn't a
   pattern. **When the work is split across several open branches, read
   each sibling from the branch that owns it (`git show <branch>:<path>`),
   not from the working tree** — see "Reading sibling topics for
   comparison" in `references/style-consistency-manual-checklist.md`. Full
   method: `references/style-consistency-cascade-vars.md`.

Report automated findings (Vale/`make vale` rule violations, including the
`Grafana.Spelling` typo-vs-dictionary-gap split) separately from every other
check above, which are judgment/manual findings even when the method is
mechanical (e.g. the shortcode and parameter-table-format checks apply a
fixed rule, but Vale doesn't enforce it, so a person still needs to weigh
the finding) — manual style checklist, frontmatter, sub-feature stability
callouts, cascade variables, shortcode validity, links, and cross-topic
comparison all fall on the manual/judgment side, each in its own labeled
output subsection per the format below.

## Other modes

The five steps above assume a single full-page standalone analysis — the
default, and by far the most common real use of this skill. Three other
modes exist for less common requests; each is now in its own reference file
— use it only when the person's request actually matches one of these
modes, rather than reading it on every standalone invocation:

- **Delta/PR review mode** (`references/delta-pr-mode.md`) — use when given
  a PR link/number, a git diff/patch, or an explicit "review just the
  changes" ask, instead of a full-page review. Key point: the *analysis*
  still reads the full current file for context; only the *output* is
  scoped to changed lines.
- **Batch modes** (`references/batch-modes.md`, covering both the narrow
  stability-badge sweep and the general-purpose batch documentation review)
  — use only on explicit ask for a sweep across multiple topics, never as a
  default expansion of a single-topic request. Both are deliberate
  exceptions to "one topic, fully analyzed, is the unit of work."

Don't read either file unless the person's request actually matches one of
these modes — for a normal single-page request, proceed directly with the
five steps below.

## Output format

Produce a single markdown report with these sections, in this order:

```
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
tool/binary was missing or outdated — per Step 0 item 9's prerequisite
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
```

If a section has no findings, say so explicitly ("No accuracy issues found against
`component/otelcol/processor/transform`") rather than omitting the section — an
absent section reads as "not checked."

**Closing reminder, every time this skill produces a report with findings**:
add a final line after "Open questions" reminding the person that once the
fixes from this report are actually applied (e.g. merged in a PR) — not
before — the page's `review_date` frontmatter field should be updated to the
merge date, in `YYYY-MM-DD` format (`writers-toolkit`'s documented format,
confirmed real: "the date you last reviewed a page for correctness,"
rendered as "Last reviewed:" on the published page). This is a reminder for
the person to act on themselves, not something this skill does — consistent
with the never-edit-files rule at the top of this document, which applies
here too even though bumping a date field might seem trivially safe. Word it
something like: "Once these fixes are merged, remember to update this
page's `review_date` to today's date." Skip this reminder only if the report
found genuinely nothing to fix (an all-clean result doesn't need a review-date
bump prompt, though the person may still choose to record that a review
happened).

## Roadmap: genuinely open items

Everything that used to be tracked here as "not yet built" has been resolved
and folded into the checks/modes above. Two items remain genuinely,
permanently open rather than just unbuilt — see `references/additional-checks.md`
for the full reasoning on each:

- Full 8-repo front matter audit integration — genuinely blocked, not just
  unbuilt: the full audit is a Google Doc this environment has no way to
  access. The two specific findings named in memory (`headless`/`killercoda`
  fields, absent `labels` outside `reference/`) are already covered,
  confirmed independently by direct file inspection rather than copied from
  the doc — see `references/additional-checks.md` for what would be needed
  to go further (the doc's content pasted in or exported to a readable file)
- Scannability heuristics that remain genuine judgment calls without a
  confirmed convention to check against (lead-paragraph length,
  bullet-vs-prose ratio) — the "parameter lists as tables" part of this is
  now handled by Step 5's "Parameter table format check"; see
  `references/additional-checks.md` for why the rest deliberately isn't a
  mechanical rule

## References and provenance

This skill reuses several files from `docs-ai/skills/` and `writers-toolkit/`
(copied rather than referenced cross-repo, since Claude Code's per-directory
file-access sandboxing makes live cross-repo relative paths unreliable) and
has gone through file-split passes to keep per-run reads scoped to what a
given topic actually needs.

This skill also reads `docs/developer/writing-component-documentation.md`
directly (it's in-repo, so no copy needed) as the authoritative source for
the component reference page's required section list and per-section
conventions — see Step 1 and `references/completeness-checklist-components.md`'s
"Required section presence" check.

Two reference files are derived from accumulated review experience rather
than from an upstream document, and both encode decisions a person made in a
real review rather than rules invented here:

- `references/dont-flag.md` — finding classes raised and explicitly
  declined. Read it before writing the report; re-raising any of them is
  noise, and so is mentioning them as an aside.
- `references/source-defects.md` — how to verify, classify, and hand off a
  defect in the code rather than the doc, including Alloy's GenAI-policy
  boundary on issue and PR text.

Both deliberately exclude project state that changes between efforts —
branch topology, which PR carries which topic, and which pages are currently
in scope. Ask for that; don't bake it into the skill.

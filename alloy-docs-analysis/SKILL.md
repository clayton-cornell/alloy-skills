---
name: alloy-docs-analysis
description: >
  Use when the user asks to analyze, audit, review, or check an Alloy doc
  page, component reference page, or CLI reference page; asks to compare an
  Alloy doc against its source code; asks about a topic's readability or
  audience level; gives a path to a file under alloy/docs/sources/; or gives
  a PR link, number, or diff and asks for a review of just the doc changes
  in it. Analyzes one Alloy documentation topic in depth: assesses its
  target audience, verifies technical accuracy against Go source code
  (component Arguments structs or CLI flag registrations, depending on page
  type), finds undocumented attributes/blocks/flags, and checks style and
  consistency against the Grafana Writers' Toolkit and sibling topics. This
  is analysis, not copyediting or AI-content detection.
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
  couldn't verify this."
- **A grep/search hit is not itself a confirmed citation.** Before writing
  any file:line into a report, actually open the file and confirm both that
  it exists and that the surrounding context matches what the search snippet
  implied. A search result whose cited path doesn't resolve isn't a
  lower-confidence version of the finding — it's no evidence at all, and the
  claim belongs in "Open questions," not a downgraded "Accuracy issue." (The
  incident behind this rule is recorded in `references/PROVENANCE.md` and
  `accuracy-checklist-other.md`'s log-message method.)

**Read only the file(s) matching the current topic's category per Step 0's
routing below — don't read every split reference file "just in case," that
defeats the purpose of the split.** Universal checks (Step 2's audience
assessment, Step 5's style/consistency) still read their full relevant set
regardless of page type, since those genuinely apply to every page equally;
only the page-type-specific portions (Steps 0/3/4) benefit from the split.

**Done when**: every top-level report section listed in the Output format
below is present (with an explicit "no findings" statement where empty,
except Source defects and Skipped checks, which are omitted when empty),
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
3. Route the page by path. This table is the backbone of Steps 3 and 4;
   each mapping file explains where that page type's facts live in source,
   including its special cases and known gaps. All files are under
   `references/`:

   | Page path | Source mapping | Accuracy (Step 3) | Completeness (Step 4) |
   |---|---|---|---|
   | `reference/components/*` | `source-mapping-components.md` | `accuracy-checklist-components.md` | `completeness-checklist-components.md` |
   | `reference/cli/*` | `source-mapping-cli.md` | `accuracy-checklist-cli.md` | `completeness-checklist-cli.md` |
   | `get-started/syntax.md`, `get-started/expressions/*`, `reference/stdlib/*` | `source-mapping-syntax.md` | `accuracy-checklist-syntax.md` | `completeness-checklist-syntax.md` |
   | `set-up/install/*`, `set-up/run/*`, `configure/*` | `source-mapping-packaging.md` | `accuracy-checklist-packaging.md` | `completeness-checklist-packaging.md` |
   | `collect/*`, `monitor/*` | `source-mapping-other.md` | none | `completeness-checklist-other.md` |
   | anything else | `source-mapping-other.md` | none | none |

   Source shapes differ by row: components map to a Go package; CLI pages
   to `internal/alloycli/cmd_<name>.go` (pflag registrations, not
   `Arguments` structs); syntax and stdlib pages to the separate top-level
   `syntax/` Go module; install, run, and configure pages to non-Go source
   (systemd units, `Dockerfile`s, the NSIS installer script).
4. If the page is in the last two rows of the table (a conceptual or task
   page), Steps 3 and 4 still apply where the page makes verifiable
   technical claims (config syntax, default ports, file paths, flag names,
   behavior descriptions) — just without a single clean source package to
   diff against; see `references/source-mapping-other.md`. Say so explicitly
   in the report rather than skipping the section. If a flag, stdlib
   function, syntax claim, or packaging detail is mentioned in passing on
   such a page, still check it against the matching row of the table rather
   than treating it as unverifiable just because the whole page isn't a
   reference page.
5. **If a page genuinely straddles two rows of the table** (e.g. a page
   that's mostly conceptual but has a full CLI flag table, or sits in a
   directory that doesn't map cleanly to any row), don't force it into
   whichever row seems closest — apply every mapping section whose claims
   actually appear on the page, and say explicitly in the report which
   mapping(s) you used and why, rather than silently picking one.
6. **Check tooling prerequisites once, up front, rather than discovering
   each one lazily mid-analysis** — a check should never trigger a build
   partway through (see `accuracy-checklist-components.md`'s explicit
   no-self-build policy). Check availability of, and note the result for,
   whichever of these are actually relevant to this specific request before
   starting Step 1:
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
     working** — a broken-but-present Podman will not surface as "missing"
     in this upfront check at all. This upfront check is a presence check
     only; the actual working-or-not determination happens when Step 5 (via
     `references/style-consistency-vale.md`) actually runs `make vale`.
     **Always invoke it as `VALE_MINALERTLEVEL=suggestion make vale`, never
     bare `make vale`** — the bare command silently suppresses every
     `suggestion`/`warning`-level rule, including the `Grafana.Readability*`
     metrics Step 2 uses, while CI's actual check doesn't apply this
     restriction. If `make vale` hits a Podman-specific error (e.g. "Failed
     to obtain podman configuration"/read-only filesystem), do NOT try a
     `PODMAN=docker` override — it does not fix the run. Follow the
     retry-then-fallback sequence in the two "Troubleshooting:" notes in
     `references/style-consistency-vale.md`.
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
  Component health, Debug information, Debug metrics, Examples) and note
  which are missing here; Step 4 reports each missing section as a
  completeness gap, per `references/completeness-checklist-components.md`'s
  "Required section presence" check, which also covers inapplicable and
  extra sections. For task-style pages (`set-up/install/*`, `set-up/run/*`,
  `configure/*`, `collect/*`, `monitor/*`), name which family the page
  belongs to and its typical shape — see `references/style-guide.md`'s
  "Alloy-specific note on the Task template." Don't check task pages against
  the generic template directly; actual conformance is checked at Step 5
  against same-family siblings.
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

Use the accuracy checklist for this page type from Step 0's routing table
(`accuracy-checklist-components.md` is the current, evolving list for
component reference pages), and `references/technical-verification.md` for
risk-tiered triage order on long topics. For any page quoting literal
`msg="..."` log output (e.g. `troubleshoot/debug.md`), use
`references/accuracy-checklist-other.md`. A representative sample is enough;
say explicitly what was and wasn't checked.
For any page with `alloy` fenced code examples, also run
`accuracy-checklist-components.md`'s "Example/config-snippet syntax
validation" section, which requires the `alloy` binary to be built locally
(see Step 0 item 6). For components/flags with recent changes, also check
that same file's "Changelog drift checks" section (CLI pages:
`accuracy-checklist-cli.md` points back to it) — but read its overlap
warning first, since most of what a changelog comparison would catch is
already caught more reliably by comparing against current source above.
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
for an inapplicable section, is non-negotiable, not just a style nit). Use
the completeness checklist for this page type from Step 0's routing table.
The three non-component files use different source shapes than `Arguments`
structs.

For `collect/*` and `monitor/*` multi-component pages, also run
`references/completeness-checklist-other.md`'s "Self-referential
completeness" method — this one compares the doc against *itself* (a stated
"components used" list or per-section count vs. the actual component blocks
in its own examples), not against Go source at all.

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
2. Manual style checklist — for whenever Docker isn't available, or as a
   second pass regardless. Read
   `references/style-consistency-manual-checklist.md` in full — not just its
   first sections — and run every section of it, which covers:
   - the manual style checklist and its `writers-toolkit` cross-check items
     (including list conventions and bullet markers)
   - link text quality, example-credential security, prose placeholder
     formatting, and ellipsis in partial examples
   - systemic wording vs. one-off defects
   - the terminology check against `references/word-list.md` (just the five
     terms with no Vale rule)
   - component reference pages only: the parameter table format check, the
     Usage section format check, and the deprecated-argument check.
     **Check row order on every Arguments/Blocks table, every run — don't
     skip it because the table "looks fine" at a glance.**
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
   already exists for exactly that purpose and isn't being used. Full
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
   whether some redirect/alias makes the old path still "work." Also covers
   link *style* consistency (reference vs. inline,
   relative vs. hardcoded absolute URL, trailing slash). Full method:
   `references/style-consistency-links-shortcodes.md`.
8. Cross-topic comparison against 2–3 sibling topics (heading order,
   admonition placement, example conventions, terminology, voice/tense). For
   task-style pages, siblings must come from the **same subdirectory** (e.g.
   other `set-up/install/*.md` pages for an install page), since each family
   has its own structural convention. A within-family difference is a real,
   worth-flagging inconsistency; a between-family difference is expected.
   If fewer than 2 real siblings exist to compare against, say so
   explicitly rather than asserting a "convention" from a single example.
   **When the work is split across several open branches, read each sibling
   from the branch that owns it (`git show <branch>:<path>`), not from the
   working tree** — see "Reading sibling topics for comparison" in
   `references/style-consistency-manual-checklist.md`. Full method:
   `references/style-consistency-cascade-vars.md`.

Report automated findings (Vale rule violations, including the
`Grafana.Spelling` typo-vs-dictionary-gap split) separately from every other
check above. Those are judgment/manual findings even when the method is
mechanical, because Vale doesn't enforce them; each goes in its own labeled
subsection per the Output format below.

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

Produce a single markdown report titled `# Analysis: <topic path>`. Before
writing it, read `references/report-template.md` and follow its sections in
this order, with the guidance it gives for each:

1. Summary (in Delta/PR review mode, state the scope explicitly)
2. Audience
3. Accuracy issues
4. Source defects
5. Completeness gaps
6. Style & consistency, with these subsections: Vale findings; Manual style
   checklist findings; Frontmatter and template-shape findings; Sub-feature
   stability callout findings; Shortcode validity findings; Cascade variable
   findings (Checks A/B/C, reported separately); Link findings; Cross-topic
   inconsistencies
7. Skipped checks
8. Open questions

If a section has no findings, say so explicitly ("No accuracy issues found against
`component/otelcol/processor/transform`") rather than omitting the section — an
absent section reads as "not checked." The two exceptions are Source defects
and Skipped checks, which are omitted entirely when empty.

**Closing reminder, every time the report has findings**: add a final line
after "Open questions" telling the person that once the fixes are actually
merged (not before), the page's `review_date` frontmatter field should be
updated to the merge date in `YYYY-MM-DD` format. This is a reminder for the
person to act on, not something this skill does — the never-edit-files rule
applies here too. Word it something like: "Once these fixes are merged,
remember to update this page's `review_date` to today's date." Skip it only
if the report found nothing to fix.

## Roadmap: genuinely open items

Two items remain permanently open: the full 8-repo front matter audit (a
Google Doc this environment can't access) and scannability heuristics with no
confirmed convention to check against. See `references/additional-checks.md`
for the full reasoning on each.

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

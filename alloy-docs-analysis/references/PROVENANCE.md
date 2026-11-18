# Provenance, sync history, and design log

This file consolidates the "how this skill got here" content that used to
be scattered as header comments and inline asides across every reference
file — copy-source metadata, file-split history, and the field-test
incidents that justify specific rules. None of this is consulted at
analysis time; it's here for whoever maintains the skill next. Every
functional file that used to carry one of these comments now has a
one-line pointer back to the matching section below instead.

## Copied-file sources

| File | Copied from | Copied | Notes |
|---|---|---|---|
| `references/style-guide.md` | `docs-ai/skills/shared/style-guide.md` | 2026-07-28 | Cross-repo relative paths are unreliable under Claude Code's per-directory sandboxing, so this is a physical copy, not a live reference. |
| `references/verification-checklist.md` | `docs-ai/skills/shared/verification-checklist.md` | 2026-07-28 | Supplementary human/agent reference only; no step in this skill directly invokes it — the `accuracy-checklist-*.md`/`completeness-checklist-*.md` split files are the Alloy-specific equivalents actually used in Steps 3–4. Its "docs-pr-write Step 8" mention refers to a different, unrelated docs-ai skill — ignore that instruction here. |
| `references/technical-verification.md` | `docs-ai/skills/docs-review/references/technical-verification.md` | 2026-07-28 | Adapted, not verbatim: the original defers to "local context" for lookup paths; this version points those paths at `accuracy-checklist.md`/`source-mapping.md` instead. |
| `references/personas.md` | `docs-ai/skills/shared/personas.md` | 2026-07-28 | Paired with `agent_personas.yaml` (the structured version) and the inference method adapted into `audience-signals.md`. |
| `references/agent_personas.yaml` | `docs-ai/skills/shared/agent_personas.yaml` | 2026-07-28 | Structured counterpart to `personas.md`. |
| `evals/evals.json` | pattern from `docs-ai/skills/docs-review/evals/evals.json` | 2026-07-28 | Structure and eval-writing pattern adapted; all 38 test cases are original to this skill. |
| `references/frontmatter-schema.md` | `writers-toolkit/docs/sources/write/front-matter/index.md` | 2026-07-28 | Copied verbatim (not from docs-ai) — authoritative Grafana-wide frontmatter field spec, used by Step 5 to validate `labels.stage`/`labels.products` against documented rules rather than just checking presence. |
| `references/shortcode-schema.md` | `writers-toolkit/docs/sources/write/shortcodes/index.md` | 2026-07-28 | Copied and condensed (not from docs-ai) — rendered example output and illustrative prose dropped to keep this a validation schema. Also folds in and supersedes what used to be a narrower, separate Param/version-substitution excerpt (`variable-substitution.md`, since removed). |
| `references/word-list.md` | `writers-toolkit/docs/sources/write/style-guide/word-list/index.md` | 2026-07-28 | Condensed, with a "Vale rule" column added cross-referencing which entries already have a dedicated rule in `writers-toolkit/vale/Grafana/styles/Grafana/`. |

`style-consistency-*.md` and `audience-signals.md` are original to this
skill but incorporate methods adapted from `docs-ai/skills/docs-review/SKILL.md`
and `docs-ai/skills/persona-check/SKILL.md` respectively (not physical
copies — the method was reimplemented for Alloy's specific checks).

All other reference files (`source-mapping-*.md`, `accuracy-checklist-*.md`,
`completeness-checklist-*.md`, `delta-pr-mode.md`, `batch-modes.md`,
`additional-checks.md`, `dont-flag.md`, `source-defects.md`) are
Alloy-specific and original to this skill.

**Re-sync policy**: if `docs-ai` or `writers-toolkit` update any of the
copied files above, re-sync manually — there's no automated link between
the repos.

**Last verified**: 2026-07-28, against `docs-ai` commit `dbbedb8` (`main`).
All copied files above were confirmed unchanged since the copy date at that
point. `docs-ai` had also added a new `sync-helm-docs` skill and a
Helm-chart section to its project-context template — neither applies to
this skill's scope (component-doc-vs-Go-source analysis), so nothing was
pulled in. `shared/load-context.md` had also changed (multi-root workspace
search fallback, warning against placing `project-context.md` in a
Hugo-published tree) — doesn't affect this skill since
`alloy/docs/project-context.md` isn't referenced here and already sits
outside `docs/sources/`.

## File-split history

**2026-07-29**: `source-mapping.md`, `accuracy-checklist.md`, and
`completeness-checklist.md` each used to be one large file (~14–19 KB)
mixing component/CLI/syntax/packaging content together, loaded in full on
every single analysis run regardless of page type. Split into category-specific
files (`-components`, `-cli`, `-syntax`, `-packaging`, plus `-other` for
remaining cross-cutting checks) so a single-page analysis only loads the
mapping/checklist file(s) relevant to that page's type. Each original
filename is now a short routing stub, kept (not deleted, since there's no
delete capability in this environment) purely as an index for anyone who
opens the old filename out of habit. Same reasoning applied to
`delta-pr-mode.md` and `batch-modes.md`, which used to be inline in
`SKILL.md` and are now only read when that specific mode is actually
invoked.

**2026-09-08**: `style-consistency.md` was the one remaining file that
hadn't followed this pattern — loaded in full on every single run
regardless of page type, and at ~61 KB the single largest file in the
reference tree. Split the same way, into six sub-files by check group
(`-vale`, `-manual-checklist`, `-frontmatter`, `-stability-callouts`,
`-links-shortcodes`, `-cascade-vars`); `style-consistency.md` is now a
routing stub like the others.

**Rationale, stated once here rather than repeated in every split file**:
splitting these files means a given run only loads the specific sub-file
its current page type or check actually needs, instead of unrelated
content for every other category. `SKILL.md`'s Step 0 routing (page type)
and Step 5's numbered list (check group) already tell you which file
applies — reading every split file "just in case" defeats the purpose of
the split. Universal checks (Step 2's audience assessment, Step 5's style
checks collectively) still read their full relevant set regardless of page
type, since those genuinely apply to every page equally; only the
page-type-specific portions (Steps 0/3/4) benefit from the split.

## Field-test incidents behind specific rules

Each entry below is the story behind a rule that's stated tersely in its
home file, tagged there as "confirmed via field test" (or similar) with a
pointer back here.

**`accuracy-checklist-components.md` — shell-agnostic block extraction.**
Confirmed real portability failures across two separate test runs: an
`awk` script issue, then a retry that assumed `rg` (ripgrep) was installed
when it wasn't, then a retry that used a zsh-specific glob qualifier
executed in a bash context; in a later run, two further attempts failed
from shell-escaping corruption around `awk` negation operators (`!/pattern/`)
getting mangled by wrapper-level quoting when the `awk` script was passed
inline as a quoted argument rather than as a file. None of these are
Alloy-specific issues; they're generic shell-portability bugs. This is why
the file's fixed extraction recipe writes the `awk` logic to a temp script
file first rather than inlining it, and avoids negation operators outside
that script file.

**`style-consistency-vale.md` — the Podman retry-then-fallback sequence.**
Confirmed real case: the `Failed to obtain podman configuration ...
read-only file system` error occurred when `make vale` was run via an
agent's own bash tool call, while a plain terminal on the same machine at
the same time ran `make vale` successfully with no override at all. A
subsequent retry of the exact same command that had failed then also
succeeded, with no environment change — pointing to a stale/torn-down
rootless-Podman runtime or mount state as at least one real cause, distinct
from a truly broken install. Separately confirmed: `PODMAN=docker
PULL=false make vale` still failed with the identical error on a machine
where `docker` was independently confirmed working and `podman`
independently confirmed present-but-broken — the override doesn't help
because `make-docs` re-detects the runtime internally with a plain
assignment that overwrites any inherited `PODMAN` value. This is why the
rule is "retry once plain, no override" before treating it as a genuine
block.

**2026-10-09 — `PULL=false` reconciled, not promoted.** A later session
recorded `PULL=false` as a reliable workaround and briefly wrote it into
`style-consistency-vale.md` and `SKILL.md` as "the override that works."
That overstated it and contradicted the confirmed failure above. Reconciled:
`docs.mk:95-98` runs `$(PODMAN) pull -q $(VALE_IMAGE)` only when `PULL` is
`true`, so `PULL=false` genuinely removes the pull as a failure site — but
`make-docs` still runs the container itself (`make-docs:846`, `:916`) using
its own re-detected runtime, so a broken install fails either way. Both
files now describe it as one step in the retry sequence, conditional on the
failure being in the pull step and on the image already being cached. Don't
re-promote it to a general fix without new evidence.

**`accuracy-checklist-other.md` — cluster messages are locally verifiable.**
Prior versions of this file told every run to skip cluster-related log
messages entirely, on the assumption they originate in the external
`github.com/grafana/ckit` module. That assumption was wrong for the large
majority of what `troubleshoot/debug.md` actually quotes, and led to an
entire section of the page going unchecked across multiple runs. Direct
confirmation: fourteen distinct cluster-related messages are all defined in
this repo's own `internal/service/cluster/` package, not in `ckit` — only
the actual gossip/membership protocol internals inside `ckit` itself remain
genuinely out of reach.

**`word-list.md` — the WordList.yml substitution-table correction.** An
earlier version of this file marked `data source` vs. `datasource`,
`dataset`, `menu icon`, and `time series` vs. `timeseries` as having "no
dedicated Vale rule," without actually opening `WordList.yml`'s own
substitution table. All four are in fact covered there. Lesson generalized
into the file's own instruction: always check `WordList.yml` directly, not
just for a standalone rule file named after the term, before concluding
something is Vale-uncovered.

**`shortcode-schema.md` — the version-substitution mechanism's real scope.**
An earlier version of this file described the angle-bracket
`<ALLOY_VERSION>`/`<OTEL_VERSION>` substitution syntax as limited to
shortcode attributes like `docs/shared`'s `version="<ALLOY_VERSION>"`. Confirmed
real, working counterexample: `otelcol.receiver.otlp.md` uses the same
token in a plain Markdown link URL in ordinary prose, and the published
page resolves it correctly. The file's description was corrected to cover
this site-wide substitution behavior, not just the shortcode-attribute case.

**`style-consistency-manual-checklist.md` — which word-list terms are
Vale-uncovered.** Same underlying correction as the `word-list.md` entry
above, referenced from the manual checklist's terminology-check
instructions: the check now scopes to exactly the five genuinely uncovered
terms (`alert rule` vs. `alerting rule`, "Best practices," `hover over`,
`kebab case`, `single pane of glass`), not the nine originally assumed
uncovered.

## Moved out of SKILL.md (2026-11-18)

Text removed from `SKILL.md` in a background-only trim to get the body under
the 500-line limit, kept here word for word. None of it is consulted at
analysis time. Every rule these passages supported is still stated in
`SKILL.md`; only the incident stories, history, and mechanism detail moved.
The Docker/Podman block below is also covered, in more detail, by the
"Troubleshooting:" notes in `references/style-consistency-vale.md`.

### Preamble: "A confident-sounding report..." bullet (original)

````
- A confident-sounding report built on a guess is worse than an honest "I
  couldn't verify this" — every existing "Open questions"/"don't fabricate"
  instance throughout this skill's reference files (the wrapped-upstream
  cases in `accuracy-checklist-cli.md`/`accuracy-checklist-components.md`,
  the ambiguous-scope case in `completeness-checklist-other.md`'s
  self-referential check, and others) is a specific application of this
  same general principle, not a one-off exception.
````

### Preamble: fabricated-citation incident (original bullet)

````
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
````

### Step 0, item 9: opening incident (original)

````
9. **Check tooling prerequisites once, up front, rather than discovering
   each one lazily mid-analysis.** Confirmed real failure mode: an agent
   without Go installed attempted to build the `alloy` binary partway
   through Step 3 (a check that should never trigger a build at all — see
   `accuracy-checklist-components.md`'s explicit no-self-build policy) and
   hit an avoidable, confusing failure. Check availability of, and note the
   result for, whichever of these are actually relevant to this specific
   request before starting Step 1:
````

### Step 0, item 9: Docker/Podman bullet, second half (original)

````
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
     overrides any inherited `PODMAN` value on its own. **`PULL=false`
     skips the make-level image pull**, which removes one of the two places
     the error can fire, but it does not fix a genuinely broken Podman
     install — `make-docs` still runs the container itself. This same error
     signature has also been confirmed to sometimes be a transient, stale
     Podman runtime state rather than a permanent break, clearable by a
     plain retry (no override) or a clean `make vale` run elsewhere on the
     machine. See `references/style-consistency-vale.md`'s two "Troubleshooting:"
     notes (one for a broken-but-present Podman install, one for VS Code's
     terminal swallowing output) for the full mechanism and the exact
     retry-then-fallback sequence to follow.
````

### Step 3: log-message gap (original sentence)

````
`troubleshoot/debug.md`), use `references/accuracy-checklist-other.md` —
confirmed real gap: several "common log messages" don't match any actual
`slog` call found in the most likely source files (they read as illustrative
paraphrases, not verbatim quotes), while others do match exactly. A
representative sample is enough; say explicitly what was and wasn't checked.
````

### Step 4: confirmed-gap examples (originals)

````
pages. The three non-component files use different source shapes than
`Arguments` structs, and each has already caught (or is specifically
designed to catch) a real, confirmed gap of its kind: an undocumented
deprecated CLI flag, the parallel deprecated/experimental-identifier pattern
in stdlib, and a wrong packaged-default flag value in `configure/linux.md`.
````

````
in its own examples), not against Go source at all. Confirmed real gap of
this kind: `collect/opentelemetry-data.md`'s component list is missing
`otelcol.processor.memory_limiter`, which its own "Configure batching"
example uses.
````

### Step 5: incident stories (originals)

Item 2, row-order miss:

````
   skip it because the table "looks fine" at a glance.** Confirmed real
   miss: an earlier pass over `pyroscope.ebpf.md` documented this rule but
   didn't apply it, both to a newly-added block's argument table and to the
   page's pre-existing Arguments table (which had drifted out of order as
   fields were appended over time instead of inserted alphabetically) —
   the rule existed in this reference file the whole time; the run simply
   didn't read this file far enough to reach it. Full method:
   `references/style-consistency-manual-checklist.md`.
````

Item 4, stability callout instances:

````
   already exists for exactly that purpose and isn't being used. Confirmed
   two real instances (`reference/cli/run.md`'s `--windows.priority` note;
   `set-up/otel_engine.md`'s near-paraphrase of `experimental_otel.md`). Full
   method: `references/style-consistency-stability-callouts.md`.
````

Item 7, stale-link bug:

````
   whether some redirect/alias makes the old path still "work." Confirmed
   real bug: `tutorials/first-components-and-stdlib.md` has two links that
   only resolve via `aliases:` redirects on the target pages, pointing at a
   directory structure (`get-started/configuration-syntax/`) that no longer
   exists. Also covers link *style* consistency (reference vs. inline,
````

### Roadmap section body (original)

````
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
````

### Step 5, item 2: manual-checklist enumeration (original, before the names-only rewrite)

Replaced on 2026-11-18 with a shorter list that names each check and adds an
instruction to read `style-consistency-manual-checklist.md` in full. This is
the text as it stood after the pyroscope story had already been removed (that
story is archived above).

````
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
   The same file also holds the Usage section format check (required-only,
   one block, with one documented exception) and the deprecated-argument
   check (table-cell format plus page-wide consistency).
   **Check row order on every Arguments/Blocks table, every run — don't
   skip it because the table "looks fine" at a glance.** Full method:
   `references/style-consistency-manual-checklist.md`.
````

### Step 5, item 8 and closing paragraph (originals, before the 2026-11-18 trim)

The rules were kept; the rationale and the `## Verify` example were dropped.

Item 8:

````
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
````

Closing paragraph of Step 5:

````
Report automated findings (Vale/`make vale` rule violations, including the
`Grafana.Spelling` typo-vs-dictionary-gap split) separately from every other
check above, which are judgment/manual findings even when the method is
mechanical (e.g. the shortcode and parameter-table-format checks apply a
fixed rule, but Vale doesn't enforce it, so a person still needs to weigh
the finding) — manual style checklist, frontmatter, sub-feature stability
callouts, cascade variables, shortcode validity, links, and cross-topic
comparison all fall on the manual/judgment side, each in its own labeled
output subsection per the format below.
````

### Step 1: structure bullet (original, before the 2026-11-18 trim)

The nine section names and the "note which are missing" rule were kept; the
rest is covered by `completeness-checklist-components.md`'s "Required section
presence" check.

````
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
````

### Routing table: Step 0 items 3–8, Step 3 and Step 4 routing sentences (originals, before the 2026-11-18 rewrite)

Step 0 items 3–6 (per-page-type routing) were replaced by one table; old
items 7, 8, 9 became items 4, 5, 6, and "Step 0 item 9" in the Output format
section now reads "Step 0 item 6." Two things were deliberately kept in the
mapping files rather than in `SKILL.md`: the `otel.md` and
`environment-variables.md` special cases (CLI), and the packaged-default flag
value gap (`--storage.path` in `configure/linux.md`).

Step 0, items 3–8:

````
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
````

Step 3, accuracy-checklist routing paragraph:

````
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
`troubleshoot/debug.md`), use `references/accuracy-checklist-other.md`. A
representative sample is enough; say explicitly what was and wasn't checked.
````

Step 4, completeness-checklist routing sentence:

````
for an inapplicable section, is non-negotiable, not just a style nit). See
`references/completeness-checklist-components.md` for component reference
pages, `references/completeness-checklist-cli.md` for `reference/cli/*`
pages, `references/completeness-checklist-syntax.md` for
`get-started/syntax.md`/`expressions/*`/`reference/stdlib/*` pages, and
`references/completeness-checklist-packaging.md` for install/run/configure
pages. The three non-component files use different source shapes than
`Arguments` structs.
````

### Step 3: syntax-validation and changelog sentences (original, before the 2026-11-18 trim)

The full explanations live in `accuracy-checklist-components.md`'s
"Example/config-snippet syntax validation" and "Changelog drift checks"
sections (the latter opens with the overlap warning and lists the two
additive cases).

````
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
````

### Output format: template moved, closing paragraphs trimmed (originals, before the 2026-11-18 change)

The full report template (the fenced block under "Output format") moved
unchanged to `references/report-template.md`; `SKILL.md` now lists the
sections and says to read that file before writing the report. Two behavior
clarifications were made at the same time: Source defects and Skipped checks
are named as the two sections omitted when empty, in both the "no findings"
paragraph and the "Done when" line. Before this, the general rule (and "Done
when") said every section is present with an explicit "no findings"
statement, while the template said to omit those two sections entirely.
No eval in `evals/evals.json` tested either reading.

Original "Done when" opening:

````
**Done when**: every top-level report section listed in the Output format
below is present (with an explicit "no findings" statement where empty),
every accuracy/completeness finding has a proposed fix, every skipped check
````

Original "no findings" paragraph and closing reminder:

````
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
````

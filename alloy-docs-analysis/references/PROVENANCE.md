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

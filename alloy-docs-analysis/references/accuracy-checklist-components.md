# Accuracy checklist: component reference pages

For triage order on long topics, read `references/technical-verification.md`
first (risk-tiered: check high-risk claims like defaults/limits/names before
low-risk prose). This file is the Alloy-specific "how to look it up" list —
use both together.

This is a starting list, not a finished one — refine it as false-positives or
missed-error patterns turn up in real runs. Keep entries concrete and
lookup-based; avoid vague judgment-call items here (those belong in the style/
audience references, not accuracy).

For every item below: cite the doc line making the claim AND the source
line/file that confirms or contradicts it. A discrepancy without both citations
isn't reportable yet — go find the missing side first.

## Attribute-level checks

- [ ] Attribute name in the doc matches the `alloy:"name,attr"` tag exactly
      (case, underscores vs. hyphens, singular/plural).
- [ ] Attribute marked "required" in the doc has NO `optional` in its tag,
      and vice versa.
- [ ] Data type stated in the doc (string, bool, int, duration, list of strings,
      etc.) matches the Go field's actual type.
- [ ] **`bool` specifically, not `boolean`.** Confirmed real, recurring stale
      artifact: `otelcol.receiver.otlp.md`'s `enforcement_policy` block
      (`permit_without_stream`) and `http` block (`keep_alives_enabled`) both
      list their type as `boolean`, while the same page's `grpc`/`http`
      `include_metadata` rows correctly say `bool` — same page, both spellings,
      only one is a valid Alloy type name. This isn't a Vale-covered typo (both
      words are real English words) and isn't caught by the general "data type
      matches Go field" bullet above unless you're specifically comparing
      spelling, not just type-category, across every type cell. Read every
      `Type` column value on the page and flag any `boolean` cell — propose
      `bool` as the fix. Worth a light spot-check on sibling wrapped-upstream
      pages too, since this reads like a stale artifact carried over from
      upstream OTel documentation conventions rather than a one-off typo.
- [ ] Default value stated in the doc matches `DefaultArguments` /
      `SetToDefault()` — or, if the field has no explicit default in the Alloy
      wrapper, matches the wrapped upstream component's default. **Follow
      `SetToDefault()` all the way to wherever the constant actually lives,
      even if that's a separate package** — confirmed real, doubly-instructive
      example: `loki.write.md` documents `queue_config.drain_timeout` as
      `"1m"` and `wal.drain_timeout` as `"30s"`, but both fields trace
      (`QueueConfig.SetToDefault()` → `defaultQueueConfig` in
      `internal/component/loki/write/types.go`, and `WalArguments.SetToDefault()`
      → `wal.DefaultWatchConfig` in
      `internal/component/common/loki/wal/config.go`) to the exact same
      underlying constant, `15 * time.Second`, elsewhere in the codebase —
      both doc values are wrong, and neither matches the other despite
      sharing one real source default. When you confirm one wrong default
      that traces through `SetToDefault()` into a separate package, it's
      worth a quick check of any *other* field on the same page whose
      default also lives in that same external package or constant — not
      because errors always cluster, but because a shared source constant
      wrong in one place is a plausible way for it to be wrong in a second,
      differently-misremembered place too. Don't over-generalize this into
      "recheck every default on the page" (spot-checking `loki.write.md`'s
      other ~15 duration/size defaults after finding this pair turned up no
      further errors) — it's specifically about defaults sharing a source
      constant, not a blanket revalidation trigger.
- [ ] Enum/allowed-value lists in the doc match the exhaustive set in the type's
      `UnmarshalText` (or equivalent validation) — no stale values, no missing
      new ones.
- [ ] Units stated for numeric/duration fields (seconds vs. milliseconds, bytes
      vs. MB) match what the code actually parses.

## Block-level checks

- [ ] Block name in the doc matches the `alloy:"name,block"` tag.
- [ ] Block cardinality (doc says "zero or more" / "exactly one" / "zero or one")
      matches whether the Go field is a slice, pointer, or plain struct.
- [ ] Nested attributes within a block are checked with the same attribute-level
      list above, recursively.

## Component-level checks

- [ ] Stability badge (experimental/public-preview/generally-available — Alloy
      has no "beta" or "private-preview" concept, see
      `references/style-consistency-frontmatter.md`'s stability mapping table) in the doc
      matches `component.Registration.Stability`, mapped by meaning not string
      equality (the Go GA constant's string is `"generally-available"`; the
      frontmatter value is `general-availability`).
- [ ] "This component accepts input from / exports data to" type claims match
      the actual `Exports` type and any `Consumer`/`Exporter` interfaces
      implemented.
- [ ] Debug info / component health claims match what `DebugInfo()` (or
      equivalent) actually reports, if the doc gets specific about it.
- [ ] Named examples in the doc (config snippets) use attribute/block names that
      exist in the current `Arguments` struct — a renamed field left stale in an
      example is a real, common failure mode.

## Cross-checking against wrapped upstream components

For `otelcol.*` components wrapping `opentelemetry-collector-contrib`: if the
Alloy doc states a default or behavior that isn't set explicitly in the Alloy
wrapper's `Arguments`/`DefaultArguments`, trace it into the upstream package's
`CreateDefaultConfig()` before either confirming or flagging it. Don't assume —
verify.

**When the upstream source genuinely isn't reachable** (no network access to
the upstream repo, and the vendored module isn't checked out locally in this
environment) — confirmed real, recurring limitation, not hypothetical: don't
leave the claim as a bare, unexplained "Open question." Say explicitly that
it's *effective behavior, not confirmed against upstream source*, and name
what would be needed to actually verify it — the upstream module path (e.g.
`go.opentelemetry.io/collector/receiver/otlpreceiver`) and the specific
function to check (`CreateDefaultConfig()` or equivalent) — so the person
reading the report knows exactly what to do next rather than just that
something's unverified. This is a more actionable version of the general
"when you're not sure, say so" principle from this skill's intro, not an
exception to it.

## Example/config-snippet syntax validation

Distinct from the "named examples use attribute/block names that exist"
bullet in Component-level checks above (which is a manual name-cross-
reference against the `Arguments` struct). This is a mechanical, tool-based
check of whether an example actually **parses** as valid Alloy syntax at
all — a different and genuinely additive failure mode (a missing comma or
brace can look fine to a human skimming an example but still be broken
Alloy syntax).

**Two different Alloy CLI commands, two different scopes — don't conflate
them:**

- **`alloy fmt <file>`** (confirmed via `internal/alloycli/cmd_fmt.go`) calls
  `parser.ParseFile()` first, before anything else — it's a **pure syntax
  parse**, no semantic/component knowledge involved. Run with no `-w`/`-t`
  flags: without those, `alloy fmt` can only fail if parsing fails (a
  formatting-only difference is silently reformatted to stdout, not an
  error) — which makes plain `alloy fmt <file>` exactly a "does this parse"
  check. **This works fine on an isolated single-component fragment** —
  parsing doesn't need to know whether `forward_to = [some.other.component]`
  actually resolves to a real component, so most doc examples (which are
  fragments, not complete configs) are fine to check this way.
- **`alloy validate <file>`** (confirmed via `internal/alloycli/cmd_validate.go`)
  is full semantic validation — checks that referenced components actually
  exist, that attribute names/types are correct against the real component
  registry, etc. **This needs a complete, self-contained config file** —
  running it on a single extracted component block will almost always fail
  on unresolved `forward_to`/cross-component references that have nothing to
  do with whether the example itself is correct. Don't run `alloy validate`
  on an isolated fragment and report its failures as real findings; that's a
  false-positive machine, not a check.

### Method

1. **Extract every ```` ```alloy ```` fenced code block from the topic — EXCEPT the `## Usage` section's block(s).** Confirmed real, universal Alloy
   convention: the `## Usage` section shows a synopsis/shape illustration,
   not a real, complete example — analogous to a man page's SYNOPSIS
   section. It uses a bare, unquoted `<PLACEHOLDER>` token in code font
   where a real value would go (e.g. `otelcol.processor.transform "<LABEL>"
   { ... }`), consistent with the exact same convention already confirmed
   in CLI reference pages' own Usage sections (`alloy run [<FLAG> ...]
   <PATH_NAME>`). **This was never meant to parse as valid Alloy syntax at
   all** — `<LABEL>` isn't a legal string literal, so running `alloy fmt`
   against a Usage block will always "fail," and that failure is not a real
   finding. Don't propose "fixing" the Usage block, and don't flag this as
   a documentation defect of any kind, template-level or otherwise — it's
   this skill's own check that needs to recognize and skip it, not
   something wrong with the docs.
   - **How to recognize a Usage-section block to exclude**: positionally,
     immediately under a `## Usage` heading and before the next heading;
     and/or by content, containing a bare unquoted `<PLACEHOLDER>` token
     (angle-bracket, no surrounding quotes) in a position where real Alloy
     syntax requires a quoted string or real value — real Alloy syntax
     never uses this pattern literally, so its presence is itself a
     reliable signal this is a synopsis, not real code.
   - **What to actually validate**: blocks under `## Examples` (or
     similarly-named sections presenting complete, filled-in, runnable
     configuration) — these use real component labels and real values, and
     genuinely should parse.
   - **A third pattern to recognize and skip, distinct from both of the
     above: REPL-prompt example blocks on stdlib pages.** Confirmed real:
     `reference/stdlib/array.md`'s `array.concat`/`array.combine_maps`/
     `array.group_by` examples are fenced as ` ```alloy ` blocks but contain
     a REPL transcript (`> array.concat([1, 2], [3, 4])` followed by the
     printed result `[1, 2, 3, 4]` on the next line) — this is a stdlib-doc
     convention showing function-call/result pairs, not a real, parseable
     Alloy config, and running `alloy fmt` against it fails with `expected
     identifier, got >` for the same structural reason a Usage block
     fails (it was never meant to parse). **Detection rule**: if the first
     non-blank line of an extracted ` ```alloy ` block starts with `> `,
     treat the whole block as a REPL transcript and skip it, same as the
     Usage-block and ellipsis-placeholder skips above — don't propose
     "fixing" it, and don't flag it as a documentation defect. This pattern
     is specific to `reference/stdlib/*.md` pages; component reference pages
     don't use this convention.
2. **Use a shell-agnostic extraction method — canonical snippet, don't
   re-derive one per run.** This avoids generic shell-portability bugs —
   use the fixed recipe below instead of writing a new extraction script
   each run.

   Write the `awk` logic to a temp script file first, then invoke it —
   don't inline a multi-line `awk` program as a quoted command-line
   argument, since that's exactly what breaks under wrapper-level quoting.
   Use only `find` and `awk` (POSIX utilities near-universally available,
   no `rg` dependency) and only simple state-equality checks (a `mode`
   variable set to `"code"`/`"usage"`/`""`), not negation operators, which
   are the pattern that broke under escaping:

   ```sh
   # 1. Write the extraction script to a temp file (avoids inline-quoting
   #    corruption of awk operators):
   cat > /tmp/extract_alloy_blocks.awk <<'AWK'
   BEGIN { mode = ""; block = ""; n = 0; first_line = 0 }
   /^## Usage/ { in_usage = 1 }
   /^## / && !/^## Usage/ { in_usage = 0 }
   /^```alloy/ {
     if (in_usage == 1) { mode = "skip" } else { mode = "code" }
     block = ""
     first_line = 1
     next
   }
   /^```$/ {
     if (mode == "code") {
       n++
       outfile = sprintf("/tmp/alloy_block_%02d.alloy", n)
       print block > outfile
       close(outfile)
     }
     mode = ""
     next
   }
   mode == "code" && first_line == 1 {
     first_line = 0
     if ($0 ~ /^> /) { mode = "skip"; next }
   }
   mode == "code" { block = block $0 "\n" }
   AWK

   # 2. Run it against the topic file:
   awk -f /tmp/extract_alloy_blocks.awk "<topic-file-path>"

   # 3. Validate each extracted block:
   find /tmp -maxdepth 1 -name 'alloy_block_*.alloy' -exec alloy fmt {} \;
   ```

   **Preferred invocation when distinguishing "reformatted, clean output"
   from "a real error" matters** (confirmed more legible in a field test
   than the plain `-exec` form above, which prints reformatted output with
   no visual marker of success/failure): wrap the validation call so each
   block's exit status is explicit, rather than relying on the presence or
   absence of parser diagnostics in the output alone:

   ```sh
   find /tmp -maxdepth 1 -name 'alloy_block_*.alloy' -exec sh -c \
     'alloy fmt "$1"; echo "EXIT ($1): $?"' _ {} \;
   ```

   Either form is acceptable; use the `sh -c`/`EXIT:` variant by default,
   since it removes the need to visually distinguish "formatted output"
   from "no output at all" — the two failure/success outcomes look
   identical otherwise unless you're specifically watching exit codes.

   The one negation this recipe still needs (`&& !/^## Usage/` to detect
   *leaving* the Usage section) is a single-line pattern-match negation
   inside the script file itself, not a shell-escaped inline argument —
   confirmed safe in practice, since the corruption in the failed runs came
   from shell/wrapper quoting around an inline `-e` argument, not from
   negation syntax inside a script file `awk` reads directly. If a future
   run still hits escaping trouble with this exact recipe, treat that as a
   new, distinct finding (note the exact error) rather than assuming this
   note already covers it.
3. **Syntax check (always attempt, works on any fragment)**: write each
   remaining (non-Usage) block to its own temp file and run
   `alloy fmt <tempfile>` (no flags). A non-zero exit / printed diagnostics
   is a real syntax error — report it with the exact parser diagnostic and
   propose the corrected syntax. `alloy fmt` with no flags reformats and
   prints a clean block to stdout with zero diagnostics and exit 0 — that's
   the expected, silent-success case, not an ambiguous or missing result.
   **Emit an explicit count summary after this step** (e.g. "Checked 3
   blocks, 0 errors") rather than leaving a successful run's output
   implicit — confirmed real friction during a field test: reformatted,
   error-free `alloy fmt` output for each block looked ambiguous enough
   ("did extraction stop early, or did every block just pass?") that a
   person had to manually re-count the doc's own fenced blocks to confirm
   nothing was silently dropped. A one-line count removes that ambiguity
   entirely.
4. **Semantic check — only when the page's own structure says its examples
   are a complete pipeline, not a per-run judgment call.** Concrete
   trigger, not a vague "looks complete enough": the page has an explicit
   "Components used in this topic" (or equivalently named) list, per the
   self-referential completeness check's own trigger condition (see
   `completeness-checklist-other.md`), AND every code block on the page,
   taken together in the page's own order, forms one self-contained
   pipeline with no unresolved `forward_to`/component references pointing
   outside that set. When both hold — common on `tutorials/*.md`,
   `collect/*.md`, `monitor/*.md` pages — concatenate the blocks in the
   page's own order into one file and run `alloy validate` against that.
   **A single reference-page component example (e.g. one `## Examples`
   entry on a `reference/components/*.md` page) never qualifies**, even if
   it looks self-contained in isolation — those pages don't carry a
   "components used" list, and running `alloy validate` there produces
   exactly the false-positive-on-unresolved-references failure mode this
   section already warns about. If a page is ambiguous against this
   trigger (e.g. it lists components used but one example clearly isn't
   part of the same pipeline as the others), say so explicitly and skip
   the semantic check for that page rather than guessing either way.
5. **This skill never builds, installs, or upgrades the `alloy` binary
   itself.** Check whether it's already available (e.g. `alloy` on `PATH`,
   or a known local build output like `./build/alloy`) — ideally as part of
   Step 0's upfront prerequisite check (SKILL.md item 9), not discovered
   here partway through Step 3.
   - **Missing**: ask the person directly whether they want to build it
     first (`make alloy` from the repo root) or proceed without this
     specific sub-check — don't silently decide either way. If they decline
     or don't respond before you need to finish the report, report this as
     a **skipped check** in the report's dedicated "Skipped checks" section
     (not "Open questions" — this is missing infrastructure, not content
     uncertainty): "Example/config-snippet syntax validation skipped:
     `alloy` binary not found; build with `make alloy` from the repo root
     to enable."
   - **Present but older than the docs' current `ALLOY_RELEASE`** (the
     cascade value in `docs/sources/_index.md`, e.g. `v1.18.0`): compare
     `alloy --version` against it. If older, ask the same way (rebuild/
     upgrade first, or proceed with a caveat) — and if proceeding, caveat
     the results explicitly: syntax/behavior in the installed version may
     not match what the current docs describe.
   - Whichever path is taken, don't run `make alloy` (or any other build/
     install/upgrade command) yourself under any circumstance — building
     the full binary is a genuinely heavier, slower action than anything
     else this check does, and it's the person's toolchain to manage, not
     something this skill decides to change.
6. A parse/validate failure is an accuracy issue like any other — cite the
   exact doc line (the code block) and the exact tool output, and propose
   the corrected example text, not just "this example is broken."

## Changelog drift checks

**Read the overlap warning below before using this** — most of what
"compare against the changelog" sounds like it would catch is already caught
more reliably by the ordinary Step 3/4 checks, which compare directly
against *current* source. Don't duplicate those findings under a separate
"changelog drift" label; this section is for the narrower, genuinely
additive cases only.

**Confirmed real structure** (`CHANGELOG.md`, release-please-generated):
versioned sections (`## [1.18.0](...)  (date)`) containing `### ⚠ BREAKING
CHANGES`, `### Features 🌟`, `### Bug Fixes 🐛` subsections. Many entries are
scoped with a `**component.name:**` prefix (e.g. `**otelcol.connector.spanmetrics:**
Expose include_collector_instance_id`), which is the anchor for finding
entries relevant to a specific component. The file is large enough that a
full read isn't practical in every environment — use `grep`/`rg` for the
component name rather than reading the whole file (same principle as
`references/accuracy-checklist-other.md`'s log-message-text checks).

**What's redundant with Step 3/4, and what's genuinely additive:**

- **Redundant (don't treat as a separate finding)**: a renamed/removed
  field, a changed default value, a new argument/block. All of these show
  up as a direct discrepancy against *current* source in Step 3/4 already,
  and comparing against current source is strictly more reliable than
  inferring "did this change" from changelog prose — if Step 3/4 already
  found it, don't also report it as a changelog-drift finding.
- **Genuinely additive case 1 — silent behavioral/semantic changes**: a
  field that still exists, with the same name/type/default, but whose
  *effect* changed — confirmed real example: `resolve_canonical_bootstrap_
  servers_only` on `otelcol.receiver.kafka`/`otelcol.exporter.kafka` is now a
  documented no-op per the 1.18.0 BREAKING CHANGES entry ("the argument
  still parses but no longer resolves bootstrap server addresses"), even
  though nothing about the field's structural shape changed. Step 3/4's
  structural diffing has no mechanical way to notice this on its own — only
  reading the changelog surfaces it.
- **Genuinely additive case 2 — missing migration guidance**: `BREAKING
  CHANGES` entries often state the migration path directly (e.g. the
  `otelcol.exporter.splunkhec` `batcher` block removal: "move the equivalent
  fields under `sending_queue.batch`"). Whether the *block itself* is stale
  in the doc is a Step 3 finding; whether the doc **explains the migration**
  for someone upgrading is a distinct, additional gap worth checking
  separately — a doc can be structurally accurate (post-fix) while still
  offering no help to a reader coming from the old behavior.

Also applicable to CLI flags with recent changes, not just components — see
`references/accuracy-checklist-cli.md`, which points back here rather than
duplicating this section.

### Method

1. Find the doc's last substantive edit date: `git log --follow -1
   --format=%ai -- <docpath>` (via the Bash tool in Claude Code).
2. Search `CHANGELOG.md` for entries scoped to the component/flag name,
   dated after that edit, prioritizing `BREAKING CHANGES` first (highest
   risk), then `Features` (cross-reference against Step 4's completeness
   findings rather than re-deriving), then generally skip `Bug Fixes`
   unless an entry explicitly describes a behavior change relevant to a
   claim the doc makes.
3. For each relevant `BREAKING CHANGES` entry, check specifically for the
   two additive cases above — not for structural staleness, which Step 3/4
   already covers.
4. If `git` isn't available or the changelog search comes back empty, say
   so rather than treating silence as "nothing changed."

# Batch modes (multiple topics in one run)

Both modes below are deliberate exceptions to "one topic, fully analyzed, is
the unit of work." Use them only on explicit ask, never as a default expansion
of a single-topic request.

For a lightweight overview across many pages (the usual case when someone says
"how are the Beyla docs doing?"), don't use either mode below. Use
[Triage mode](./triage-mode.md): one table row per page, high-risk claims only,
plus the topic-level gap pass. This file doesn't duplicate that content.

## Batch general review mode (full analysis across several topics)

Use this when the person wants a systematic, full-depth sweep of a directory or
doc section (accuracy, completeness, and any other passes they asked for),
with one report per topic and a rollup. It differs from triage mode in depth:
triage verifies only the highest-risk claims per page, while this mode runs
the complete procedure per page.

**State the cost up front.** This is the same depth as a single standalone
analysis, multiplied by the number of pages in scope. The full tree is 47 pages
under `docs/sources/`, which isn't a realistic single pass at this depth. If
the person only needs a ranking, propose triage mode first and use its
verdicts to pick the pages that deserve a full report.

**Done when**: every file in the confirmed scope has had the full procedure
run against it, each has its own report, and the rollup is written.

### Method

1. **Confirm scope before starting.** Propose a bounded scope (one directory
   such as `configure/`, `quickstart/`, or `setup/`, or a fixed sample) and
   confirm it, even if the original ask sounded broad.
2. **Enumerate files from the directory tree**, for example
   `find docs/sources/<dir> -name '*.md'`. Don't rely on a generated index page
   as a file list. Include `_index.md` files deliberately, and exclude
   non-page assets such as `configure/resources/`.
3. **Run the full procedure per topic**, exactly as in standalone mode. No
   shortcuts and no skipped checks. Each topic gets its own report in the
   standard output format.
4. **Checkpoint for large batches.** Process roughly 5-10 topics at a time,
   report interim results, and confirm before continuing, so the person can
   redirect early.
5. **Write a rollup after the per-topic reports.** The rollup is a short
   triaged summary, not a repeat of the reports:
   - One row per topic: its most significant findings only, ranked by severity
     (confirmed accuracy issues and completeness gaps first).
   - Findings that recur across topics (for example the same wrong default or
     the same stale sample output) called out once as a systemic finding
     rather than repeated per page.
   - Any confirmed bug that a user would hit (a wrong key or default that makes
     configuration silently fail) surfaced prominently, not buried.
   - A list of the reports produced, so the person can open any one.
6. **Don't edit files.** The batch output is reports only.

## Deprecated-key sweep (narrow)

Use this only when the person explicitly asks to find deprecated Beyla
configuration still used in the docs, for example "which pages still use the
old `discovery.services` key?". It's a cheap, grep-driven sweep across
`docs/sources/`, not a full review.

The candidate set, observed in the 2026-10-20 triage (not independently
verified, so confirm each against source before reporting it as a finding):

| Deprecated usage | Where to confirm |
|---|---|
| `otel_metrics_export.features` (feature selection under the exporter block; the current location is `metrics.features`) | `pkg/beyla/config.go` (comment around the legacy `Metric` feature sections) |
| `discovery.services` (replaced by `discovery.instrument`) | `pkg/beyla/config.go` (`Instrument`), `vendor/go.opentelemetry.io/obi/pkg/appolly/services/criteria.go` |
| `application_span` as a feature value (replaced by `application_span_otel`) | `docs/sources/configure/export-data.md` already marks it deprecated; confirm in the vendored OBI metrics feature definitions |
| `executable_name` / `BEYLA_EXECUTABLE_NAME` (marked `Deprecated: Use BEYLA_AUTO_TARGET_EXE`) | `pkg/beyla/config.go` (the `Exec` field) |

**Done when**: each hit is classified, and every page with at least one
deprecated *usage* is listed with its line numbers.

### Recipe

Run from the Beyla repo root:

```sh
grep -rnE \
  'otel_metrics_export:|prometheus_export:|application_span([^_]|$)|^[[:space:]]*services:|executable_name|BEYLA_EXECUTABLE_NAME' \
  --include='*.md' --include='*.yml' --include='*.yaml' docs/sources/
```

Then narrow each hit:

- `otel_metrics_export:` and `prometheus_export:` are valid blocks. Only a
  `features:` key nested under them is the deprecated usage:
  `grep -rn -A12 'otel_metrics_export:' docs/sources/ | grep 'features:'`
  (and the same for `prometheus_export:`). Check each match's indentation to
  confirm `features:` belongs to the exporter block and not to
  `metrics:` or a `discovery.instrument` entry.
- `^[[:space:]]*services:` also matches unrelated keys (for example a Docker
  Compose `services:` in `setup/docker.md`). Count it only when it's nested
  under Beyla's `discovery:` block. Check the surrounding lines.
- `application_span` (not `application_span_otel`, `_sizes`, and so on) is a
  deprecated usage only inside a `features` list or accepted-values text that
  recommends it. Text that says it is deprecated (as `configure/export-data.md`
  does) is documentation of the deprecation, not a deprecated usage.

Classify every hit as one of:

1. **Deprecated usage in an example or instruction**: report as a finding
   (page, line, replacement).
2. **Documents the deprecation**: not a finding. Leave it out of the table,
   but note it in the scope line.
3. **Unrelated match**: discard.

Output one consolidated table: page | line | deprecated usage | replacement |
source confirmation (file:line). This is the one place in this skill where a
single combined table across topics is correct. If the source can't be opened
to confirm a replacement, list that row under Open questions, not as a
finding.

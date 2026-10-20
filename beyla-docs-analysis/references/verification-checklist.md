<!-- Adapted from alloy-docs-analysis/references/verification-checklist.md (generic documentation verification list). Step 3 and 4 detail is in accuracy-checklist.md and completeness-checklist.md; this is the short end-of-run self-check. -->

# Verification checklist

Run through this before returning a report. It's a self-check on the analysis,
not a substitute for `accuracy-checklist.md` (Step 3) or
`completeness-checklist.md` (Step 4).

## Scope and setup

- [ ] Read the whole page and wrote down its scope in one sentence.
- [ ] Mapped the page to source with `source-map.md` and opened those files.
- [ ] Recorded the state of the OBI source: `go.mod` replace, `.obi-src` not
      checked out, vendored copy used, vendored-vs-pinned unverified
      (`source-map.md`).

## Accuracy

- [ ] Every YAML key and env var in tables, prose and examples was matched to a
      struct tag or the schema; Beyla's non-strict YAML decode means unknown keys
      are silent.
- [ ] Every default was traced through env -> YAML -> `normalizeConfig` ->
      `DefaultConfig` -> `obi.DefaultConfig`; Beyla's overrides were checked.
- [ ] `BEYLA_` env vars were checked against the `OTEL_EBPF_` tag where the
      field is an OBI type.
- [ ] Enum and feature lists were compared to their source of truth.
- [ ] Deprecated or renamed options were checked.
- [ ] Metric and attribute names were checked against the definition and
      Beyla's runtime renames; Prometheus names were derived, not recalled.
- [ ] Kernel, capability and language claims were compared to `os.go` and
      `gofile.go` row by row.
- [ ] Helm, Docker and systemd claims were checked against `charts/`,
      `Dockerfile`, `contrib/`; chart and image defaults were kept apart from
      binary defaults.
- [ ] Examples were run through `example-validation.md` (YAML checker, shell
      and env vars, sample output).
- [ ] Counts in prose ("three metrics") match the source.

## Completeness

- [ ] User-facing fields for the page's scope were enumerated from the structs
      and each was searched for by YAML key, env var and plain name.
- [ ] Gaps were classed as gap-in-page vs missing topic; deprecated items marked;
      experimental, development-only and undocumented fields listed under Not
      counted rather than reported.

## Evidence and report

- [ ] Every finding cites the doc `file:line` and the source `file:line`, and
      each cited file was opened (a search hit isn't a citation).
- [ ] OBI-dependent findings say they rest on `vendor/go.opentelemetry.io/obi/...`.
- [ ] Every finding proposes corrected text; nothing was edited.
- [ ] Unverified claims are under Open questions with the exact source needed;
      skipped checks (runtime verification, missing tools, other repositories) are
      listed under Skipped checks.
- [ ] Code defects (documented behavior the code doesn't deliver) are under
      Source defects, handled per `source-defects.md`, not mixed into
      Accuracy issues.
- [ ] No issue text, PR description or review reply was drafted.

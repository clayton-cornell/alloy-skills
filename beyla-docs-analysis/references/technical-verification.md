<!-- Adapted from alloy-docs-analysis/references/technical-verification.md and docs-ai/skills/docs-review/references/technical-verification.md. -->

# Technical verification: risk-tiered claim prioritization

Use this to decide which claims to verify first in Step 3, especially on long
pages. Combine it with the lookup lists in `accuracy-checklist.md` and the
routing in `source-map.md`. This file is about order and bar of proof, not where
to look.

## 1. Identify verifiable claims

Read the page and flag each statement that makes a factual claim about Beyla's
behavior: config keys, env vars, defaults, numeric limits, accepted values,
metric and attribute names, kernel/capability/language support, Helm values,
example output, and syntax in examples.

## 2. Prioritize

- **High risk** (always verify): specific numbers (defaults, limits, sizes,
  kernel versions), YAML keys and env var names, metric and attribute names,
  capability lists, anything users copy-paste (config, commands, Helm `--set`).
  A mismatch breaks configuration, and Beyla won't tell the user: its YAML
  decoding is non-strict, so wrong keys are silently ignored.
- **Medium risk** (verify when possible): behavioral descriptions, enum and
  feature lists, sample output, deprecation statements, chart-vs-binary
  defaults, claims that depend on OBI. If the evidence lives in code you can't
  see (OBI's eBPF C code; `.obi-src` isn't checked out), flag it for follow-up.
- **Low risk** (spot-check): general prose about well-established behavior.
  Don't let it block the report. Marketing prose that makes no checkable claim
  isn't verified at all.

Order within a page:

1. Anything with a specific number (defaults, limits, versions).
2. Key and env var names; Beyla-vs-OBI default overrides (`DefaultConfig`).
3. Metric and attribute names; Prometheus names.
4. Copy-paste examples: run the YAML checker first (`example-validation.md`).
5. Capability, kernel and language-support tables.
6. Enum and feature lists (is the list complete and current?).
7. Helm, Docker, systemd and Kubernetes claims.
8. Sample output.
9. General behavior prose.

## 3. Bar of proof

- Cite both sides (doc `file:line`, source `file:line`) and open the file before
  citing; a search hit isn't a citation.
- Trace the effective value: env -> YAML -> `normalizeConfig` -> `DefaultConfig`
  -> `obi.DefaultConfig` -> the type or its consumer (`accuracy-checklist.md`
  1.3). A struct declaration alone doesn't establish a default.
- Don't call a value "rejected" because of a `validate:"..."` tag: Beyla's
  `Validate` doesn't run OBI's validator.
- OBI behavior is evidenced by `vendor/go.opentelemetry.io/obi/...`. Say so, and
  note that the vendored copy hasn't been matched to the pinned submodule commit.
  Never use a newer upstream source as evidence.
- If you cannot locate the source, put the claim under Open questions with the
  exact file, type, function or OBI directory that would settle it. Never
  downgrade a confirmed divergence to Open questions because verification was
  hard.

## 4. When reading isn't enough

Some claims turn on what a standard-library function returns for realistic input
(`url.Parse`, `path.Match` glob semantics, duration parsing). If reading the
call site can't settle it:

- Prefer reading the function's source or documentation.
- A stdlib-only throwaway program is acceptable only with the person's
  agreement, outside the Beyla checkout, and deleted afterwards. It must not
  import Beyla or OBI packages (that would build them), and it must call the same
  function the source calls, not a reimplementation.
- Prometheus name derivation: read
  `vendor/github.com/prometheus/otlptranslator/metric_namer.go` and
  `unit_namer.go` instead of running anything; apply them to the OTLP name, unit
  and type from the metric definition.
- Otherwise report the claim as an Open question and say how to settle it.

## 5. Report

For each verified claim note: the claim as written, what the source says with
`file:line`, and whether they match. Put divergences under Accuracy issues.
Defects in the code itself go to `source-defects.md`, not here.

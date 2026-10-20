<!-- Adapted from alloy-docs-analysis/references/source-defects.md for Beyla's code structure. -->

# Source defects: when the code is wrong and the doc can't fix it

Use this when Step 3 (accuracy vs. source) finds that the documentation
describes what Beyla is meant to do and the **code** doesn't do it, or that the
documented thing is something the code cannot actually do. There's no doc edit
that makes the page both true and useful, so these get their own handling and
their own `## Source defects` report section, separate from `## Accuracy issues`.

Paths are relative to the Beyla repo; `OBI/` means
`vendor/go.opentelemetry.io/obi/` (write full paths in findings).

## What counts as a source defect worth reporting

Functional problems only. Shapes to look for in Beyla:

- **Documented option with no effect.** The key parses into a field that nothing
  downstream reads, or that a consumer ignores (check the whole path, including
  the Beyla -> OBI conversion in `pkg/beyla/config_obi.go`).
- **Supported key silently ignored.** A documented, supported YAML key whose tag
  doesn't match, or a mirrored Beyla struct that drifted from its OBI twin so
  `Convert` (`pkg/helpers/config/convert.go`) drops the value. Note the general
  case isn't a defect: Beyla's non-strict YAML decode ignores unknown keys by
  design. Only report a specific documented key that cannot work.
- **Environment variable that can't work.** A documented `BEYLA_X` whose mapped
  name `OTEL_EBPF_X` has no `env` tag on the field (`OverrideOBIGlobalConfig`
  rewrites the name; if nothing reads it, it's inert), or a Beyla-owned `BEYLA_*`
  tag that an OBI-side reader never sees.
- **Default that contradicts its own comment or the documented intent**, or a
  default set in `DefaultConfig` and then overwritten by `normalizeConfig`.
  (Intentional precedence, such as a deprecated `otel_metrics_export.features`
  overriding `metrics.features` in `normalizeConfig`, is not a defect.)
- **Validation that doesn't run.** A documented constraint enforced only by a
  `validate:"..."` tag that Beyla's `Validate` never evaluates, so invalid input
  reaches a crash, a silent fallback or a nonsensical value.
- **Gates that can never be satisfied.** A feature guarded by a condition Beyla
  never sets, so it's permanently inert.
- **Values lost in conversion.** `AsOBI`/`FromOBI` skip lists or `overrideOBI`
  discarding something the user configured.
- **Metrics derived from the wrong quantity**, labels that never materialize, or
  a metric whose Prometheus name doesn't follow from its OTLP definition because
  of a runtime rename (`OverrideOBIGlobalConfig`).
- **Capability or kernel gates that disagree with the code path.** For example
  an enforcement check that demands a capability the feature never uses, or a
  fallback that doesn't engage.

## What does NOT count

- Stale or wrong **source comments**, including comments naming the wrong env
  var or type. Zero runtime effect.
- **Naming** inconsistencies with no behavioral consequence.
- A **log message that misstates the fallback** with no user-visible effect on
  configuration (for example a warning whose text and action differ). Mention it
  in Open questions at most, unless a page quotes or relies on it. An observed
  illustration, read but not run: the default branch of `chooseUnmatchPolicy` in
  `OBI/pkg/transform/routes.go` (lines 442-446) warns "defaulting to heuristic"
  but sets the wildcard action.
- **Experimental and undocumented features** (`injector`, `pkg/webhook/`): the
  source says they're experimental and some options have no effect yet.
- The **non-strict YAML decode** itself, and options marked deprecated that still
  work.
- Anything you'd have to speculate about. See the bar below.
- Defects that exist only in the vendored OBI copy are reported as such (see
  "Where it belongs"); they aren't Beyla code changes.

## Verify before reporting

1. **Trace the whole path**, from the documented key or env var through
   `LoadConfig` (`pkg/beyla/config.go`), the conversion (`AsOBI`, `FromOBI`,
   `Convert`), and into the consumer, to the point where the value is read (or
   isn't). "The field exists" stops short of verification.
2. **Name a file and line for every hop.** If you can't get a line number for a
   hop, say so explicitly rather than guessing. An invented line number is
   worse than an acknowledged gap.
3. **Prove the negative properly.** "Nothing reads X" needs a repo-wide search
   across `pkg/`, `cmd/` and `vendor/go.opentelemetry.io/obi/pkg/`, plus a count
   of what the construction site does set; not an impression from one function.
4. **Open the code and the surrounding context** before citing. A search hit
   isn't a citation.
5. **Tests are corroboration only** (`pkg/beyla/config_test.go`, others): read
   what the test exercises. A passing test doesn't prove a feature works.
6. **Empirical checks need a supplied build.** If the person supplies a Beyla
   binary or image from this checkout, a runtime check can settle a path
   question (see `example-validation.md` D). The skill never builds Beyla or
   pulls images. Without one, state the confidence as "read from source, not
   run".
7. If the path leaves what you can see (OBI's eBPF C code; `.obi-src` isn't
   checked out), the claim is an Open question, not a defect.

## Where it belongs

State which repository would carry the fix. Code under `pkg/`, `cmd/`, `charts/`
is Beyla's. Code under `vendor/go.opentelemetry.io/obi/` comes from OBI via the
`.obi-src` submodule and is changed upstream, not edited in the vendor tree
(see `.github/instructions/obi-integration.instructions.md`). Say the finding
was made against the vendored copy and the vendored version may differ from the
pinned commit.

## Decide the doc's disposition with the person, never unilaterally

Present the options and the trade-offs; which applies is the person's call:

1. **Leave the doc unchanged**: it becomes correct once the code is fixed. Don't
   add a "currently has no effect" note in this case, and don't re-raise it as a
   doc finding on later reviews of the same page.
2. **Correct the doc to describe current behavior**, and record explicitly that
   the text must be **reverted** when the code is fixed.
3. **Keep a doc guard** that stops readers hitting the bug (for example saying a
   setting is required when omitting it crashes). **Never "correct" a doc toward
   buggy behavior** if that exposes users to a crash, data loss or a security
   problem.

Whichever is chosen, state the **revert condition** in the finding so a later
reviewer doesn't read the workaround as intended wording. Offer proposed doc
text for each option you present.

## Carry the finding forward

A source defect needs a home outside the page (a tracking issue or a fix PR in
the right repository). Say that plainly in the finding, and raise it again
unprompted when the person mentions preparing, titling or finishing the PR for
that work, so it doesn't stay in the transcript.

## GenAI policy boundary

The person writes PR descriptions, issue bodies, and all review and discussion
replies themselves.

- **You may** describe the defect in the analysis output, draft documentation
  content, and suggest a PR *title* that follows the repository's convention.
- **You may not** draft issue text, PR description sections, or review/discussion
  replies, and you don't open issues or PRs.

If asked to do any of the second group, refuse that part explicitly in your
reply, explain it conflicts with this skill's policy (which follows the
approach of Alloy's `docs/developer/genai.md`; no equivalent policy file was
found in the Beyla checkout on 2026-10-20, so check the repository's
contributing guidance), and continue with what you can do. Don't stage
"just a draft for you to paste" issue or reply text.

## Output

Report under `## Source defects`, separate from `## Accuracy issues`, with: the
option, env var, metric or behavior affected; root cause with `file:line` per
hop; which repository carries the fix; the doc disposition chosen and its revert
condition; and a confidence statement naming what was verified in source versus
inferred, and whether anything was run.

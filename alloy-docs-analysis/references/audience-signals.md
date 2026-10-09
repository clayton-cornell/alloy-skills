<!--
This file's inference method is adapted from docs-ai/skills/persona-check/SKILL.md
(grafana/docs-ai, path: skills/persona-check/SKILL.md), copied 2026-07-28.
It reads references/personas.md and references/agent_personas.yaml (also
copied from docs-ai) rather than the ad hoc "audience tier" heuristic this
file originally used. Vale readability scoring (Step A below) is this skill's
own addition, not part of the docs-ai source.
-->

# Audience assessment method

Combine an automated readability score with the persona model — neither alone
is reliable. Readability scores don't catch assumed prerequisites or content
positioning; the persona model without a score is too subjective to compare
consistently across topics.

## Step A: run readability metrics locally

Use the same mechanism as `references/style-consistency-vale.md` — prefer
`VALE_MINALERTLEVEL=suggestion make vale` from `alloy/docs/` (Docker/Podman,
matches CI) over a raw local `vale` call. **`VALE_MINALERTLEVEL=suggestion`
is required, not optional** — every `Grafana.Readability*` rule is
suggestion-level, so the bare `make vale` default (`error`-only, set in
`docs/make-docs`) silently produces zero readability output on every run,
which looks identical to "this page passes" but isn't confirmed at all. See
`references/style-consistency-vale.md`'s writeup of this confirmed gap.
`Grafana.Readability*` rules (Flesch-Kincaid, Gunning Fog, SMOG,
Coleman-Liau, LIX, Automated Readability, Flesch Reading Ease) are part of the
same `Grafana` style package `make vale` already runs — no separate invocation
needed. If you already ran Vale for Step 5 in this same session (with
`VALE_MINALERTLEVEL=suggestion`), reuse that output instead of running it twice.

If the initial `make vale` run fails with a Podman-specific error (for example,
"Failed to obtain podman configuration" or other read-only-filesystem errors),
retry `make vale` once, plain (no `PODMAN=docker` override — confirmed
ineffective here, see `references/style-consistency-vale.md`'s two
"Troubleshooting:" notes). This signature has been confirmed to sometimes reflect a transient,
stale rootless-Podman runtime/mount state rather than a permanently broken
install, and a plain retry (or a clean `make vale` run by the person
themselves in a normal terminal) has been observed to clear it. Only treat
Vale/readability as unavailable, via the raw fallback below, if the identical
signature recurs after that retry.

If terminal capture appears empty, redirect explicitly to a file in `$TMPDIR`
instead of `/tmp`, then inspect that file. Some sandboxed environments mount
`/tmp` read-only, which can create missing/empty capture artifacts unrelated to
Vale itself.

If Docker/Podman isn't available, the fallback is raw `vale` against
`writers-toolkit/.vale.ini` — same caveat as
`references/style-consistency-vale.md` applies (don't trust
`Grafana.Spelling` results from host Vale, but readability scores aren't
affected by that specific issue). If neither is available, this is a
structured skipped-check outcome per SKILL.md's prerequisite handling, not
an "Open questions" item — report it that way rather than fabricating a
score.

**Confirmed real gap, fixed here: these rules only produce output on
failure, not always.** Every `Grafana.Readability*` rule (checked directly:
`ReadabilityFleschKincaid.yml`) `extends: metric` with a numeric
`condition` — Vale computes the score internally but only emits an alert
(with the actual number embedded via `%s` in the message) when the
condition is met, i.e. the page has already crossed into "needs
improvement" territory. **A page that reads fine produces zero output for
that rule** — there is no way to see "your Flesch-Kincaid score is 6.2" for
a page that's already comfortably under the threshold; Vale simply stays
silent. Don't treat this silence as "couldn't determine the score" or try
to compute/estimate a number yourself — it's a legitimate, complete
success state and should be reported as such:

- **Alert fired**: cite the exact message, including the embedded numeric
  value, and treat it as a real style finding (dense/hard-to-read prose for
  the inferred persona).
- **No alert for a given metric**: report explicitly as "passes
  `Grafana.<Metric>` (no threshold violation) — Vale doesn't surface an
  exact score for a passing page." This is not a gap in your analysis; it's
  the correct, complete readability finding for that metric.

Also remember `make vale` is repo-wide, not per-file. So page-specific filtering
can legitimately return no matches even when Vale ran successfully; interpret
that as "no readability/style findings for this page" rather than a failed run.

Metrics of interest: `FleschKincaid`, `FleschReadingEase`, `GunningFog`,
`SMOG`, `ColemanLiau`, `LIX`, `AutomatedReadability`. Higher grade-level scores
(Flesch-Kincaid, Gunning Fog, SMOG, Coleman-Liau, LIX, ARI) mean denser/harder
text; higher Flesch Reading Ease means easier text (it's inverted).

## Step B: infer persona, use case, and entry state

Load `references/personas.md` and `references/agent_personas.yaml`. Read the
topic's body content (not the title/description front matter — those are
unreliable signals per `persona-check`) and infer:

- **Persona** — Learner, Practitioner, Expert, or Operator. Signals:

  | Signal | Suggests |
  |---|---|
  | Conceptual explanations, "what is X", scenario framing | Learner |
  | Step-by-step with guidance, defines terms inline | Learner |
  | Task-focused, assumes core concepts, includes examples | Practitioner |
  | Reference format, precise syntax, edge cases, no intro | Expert |
  | Architecture, setup, config, failure modes, scaling | Operator |

- **Use case** — Understand, Investigate, Implement, Operate, or Optimize.
- **Entry state** — unknown_goal, known_task, need_precision, or system_level.

Content can legitimately be layered (e.g., a short Learner-level intro
followed by Expert-level reference detail) — report this as "layered," not as
a mismatch.

### Red flags by persona (from `persona-check`)

Apply whichever set matches the inferred persona:

- **Learner**: jumps into commands without explaining why; undefined
  jargon/acronyms; no framing for why the task matters; dead-end with no next
  steps.
- **Practitioner**: too abstract with no concrete examples; steps hard to
  translate into action; missing connection between steps and outcomes.
- **Expert**: oversimplified explanations that waste the reader's time;
  missing edge cases/constraints/reference detail; unnecessary intro material.
- **Operator**: only covers the happy path; no failure modes or
  troubleshooting; missing system-level context.

**Alloy-specific calibration**: `reference/components/` pages are
near-exclusively Expert-tier by design — see the note at the end of
`references/personas.md`. Don't flag a component reference page for lacking a
Learner-level on-ramp; that's expected, not a gap.

## Step C: reconcile and report

State the inferred persona, use case, and entry state, backed by both the
readability outcome (per-metric: an alert's cited number, or an explicit
"passes, no violation" for metrics with no alert — never a fabricated
number) and at least one textual example. Then check whether that fit
matches the page's position in the docs (a page linked from a
getting-started flow implies Learner/Practitioner; deep `reference/` pages
imply Expert). Flag a mismatch only when the evidence is clear.

Per `persona-check`'s core lesson: identifying the persona is just setup.
Always answer **what's missing for this reader** — 1-3 concrete, actionable
items — not just a label. If nothing is missing, say so explicitly rather than
manufacturing a gap.

<!--
The persona inference method is adapted from docs-ai/skills/persona-check/SKILL.md
(grafana/docs-ai, path: skills/persona-check/SKILL.md) via the sibling
alloy-docs-analysis skill's audience-signals.md. It reads references/personas.md
and references/agent_personas.yaml (copied, not live-referenced). The Vale
readability extraction in Step A is specific to Beyla.
-->

# Audience assessment method

Combine automated readability scores with the persona model. Neither alone is
reliable. Readability scores don't catch assumed prerequisites or content
positioning. The persona model without scores is too subjective to compare
consistently across topics.

## Step A: get readability metrics from Vale

Readability metrics come from Vale, run the way
`references/style-consistency-vale.md` describes (`make vale` from
`beyla/docs/`). If you already ran Vale for the style pass in this session,
reuse that output instead of running it again.

In Beyla, `make vale` reports seven readability findings per page, each at
line 1, column 1:

- `Grafana.ReadabilityColemanLiau`
- `Grafana.ReadabilityFleschReadingEase`
- `Grafana.ReadabilityFleschKincaid`
- `Grafana.ReadabilityGunningFog`
- `Grafana.ReadabilitySMOG`
- `Grafana.ReadabilityLIX`
- `Grafana.ReadabilityAutomatedReadability`

The message carries the score, for example `11.63 aim for below 9.` for a
grade-level metric or `44.97 aim for above 70.` for Flesch Reading Ease.

Extract them for one page from the Vale results. From a whole-set line output file (here `vale-out.txt`):

```sh
grep -F 'sources/<path>:1:1:Grafana.Readability' vale-out.txt
```

From the per-file JSON run (see `references/style-consistency-vale.md`), take the findings whose `Check` starts with `Grafana.Readability`.

Replace `<path>` with the page's path under `docs/sources/`, for example
`configure/routes-decorator.md`. Keep the output file in your scratch directory (`$TMPDIR` if set), not in the repo.

Interpretation:

- Quote each score exactly as Vale reports it. Never estimate or compute a
  score yourself.
- If a metric is absent for a page, report "no `Grafana.<Metric>` finding for
  this page" and don't infer a number. Page-level filtering returning nothing
  can also mean Vale didn't run, so confirm the run completed first.
- If Vale couldn't run (no Docker or Podman), this is a skipped check per
  `SKILL.md`'s prerequisite handling. Report it under "Skipped checks" and
  don't fabricate scores.
- Higher grade-level scores (Coleman-Liau, Flesch-Kincaid, Gunning Fog, SMOG,
  LIX, Automated Readability) mean denser text. Higher Flesch Reading Ease
  means easier text (it's inverted).
- **Technical reference pages with a high grade level are expected for Expert
  pages.** Dense config tables, key names, and identifiers inflate the scores.
  Don't flag a score alone. Use it only as supporting evidence alongside a
  textual signal from Step B.

## Step B: infer persona, use case, and entry state

Load `references/personas.md` and `references/agent_personas.yaml`. Read the
topic's body content (not the title/description front matter, which are
unreliable signals per `persona-check`) and infer:

- **Persona**: Learner, Practitioner, Expert, or Operator. Signals:

  | Signal | Suggests |
  |---|---|
  | Conceptual explanations, "what is X", scenario framing | Learner |
  | Step-by-step with guidance, defines terms inline | Learner |
  | Task-focused, assumes core concepts, includes examples | Practitioner |
  | Reference format, precise syntax, edge cases, no intro | Expert |
  | Architecture, setup, config, failure modes, scaling, privileges | Operator |

- **Use case**: Understand, Investigate, Implement, Operate, or Optimize.
- **Entry state**: unknown_goal, known_task, need_precision, or system_level.

Content can legitimately be layered (for example, a short Learner-level intro
followed by Expert-level reference detail). Report that as "layered," not as a
mismatch.

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

**Beyla calibration**: `configure/` pages are Expert-leaning reference pages
by design, and `quickstart/` plus the top-level `_index.md` are the on-ramps.
See the note at the end of `references/personas.md`. Don't flag a `configure/`
page for lacking a beginner on-ramp. That calibration is a starting point based
on page structure, not user research.

## Step C: reconcile and report

State the inferred persona, use case, and entry state, backed by both the
readability outcome (the exact Vale messages, or an explicit "no finding" or
"Vale unavailable") and at least one textual example. Then check whether that
fit matches the page's position in the docs (a page linked from a quickstart or
the landing page implies Learner/Practitioner; `configure/` pages imply
Expert). Flag a mismatch only when the evidence is clear.

Identifying the persona is just setup. Always answer **what's missing for this
reader**: 1-3 concrete, actionable items, not just a label. If nothing is
missing, say so explicitly rather than manufacturing a gap.

# Provenance and sync notes

None of this is consulted at analysis time. It records where the skill's files
came from, so whoever maintains it next knows what to re-sync.

## Adapted from `alloy-docs-analysis`

| File | Origin | Notes |
|---|---|---|
| `references/personas.md` | Copied from `alloy-docs-analysis/references/personas.md`, which derives from `docs-ai/skills/shared/personas.md` | The Alloy calibration note was replaced with a Beyla calibration note. The calibration is a starting point based on page structure, not user research. |
| `references/agent_personas.yaml` | Copied from `alloy-docs-analysis/references/agent_personas.yaml`, which derives from `docs-ai/skills/shared/agent_personas.yaml` | Unchanged. |
| `references/audience-signals.md` | Method adapted from `alloy-docs-analysis/references/audience-signals.md` (itself adapted from `docs-ai/skills/persona-check/SKILL.md`) | Readability extraction rewritten for Beyla's Vale output. Alloy-only examples removed. |
| `references/delta-pr-mode.md` | Adapted from `alloy-docs-analysis/references/delta-pr-mode.md` | Retargeted at `grafana/beyla` `docs/sources/**`; adds head-SHA source verification. |
| `references/batch-modes.md` | Adapted from `alloy-docs-analysis/references/batch-modes.md` | The Alloy stability-badge sweep was dropped. A narrow deprecated-key sweep was added. Points to `references/triage-mode.md` for the lightweight overview. |
| `evals/evals.json` | Structure adapted from `alloy-docs-analysis/evals/evals.json` | All test cases are original to this skill. |

## Original to the Beyla skill

- `SKILL.md`
- `references/source-map.md`
- `references/triage-mode.md`
- The accuracy and completeness checklists
- `references/example-validation.md`
- `scripts/check_yaml_examples.py`
- `references/style-consistency-terminology.md`
- The `references/dont-flag.md` seed

## Verified environment (2026-10-20)

- Vale runs through Podman from `beyla/docs` and finishes in about 20 seconds.
- The baseline run reported 1,452 findings across 47 pages.
- `make vale` exits non-zero when findings exist.

## Triage findings

`reports/triage-overview.md` was produced on 2026-10-20 by parallel automated
reviewers. Its findings were **not independently verified**. Treat them as
"observed in the 2026-10-20 triage" and re-check against source before relying
on them. The evals refer to them that way, as likely-but-unconfirmed targets.

## Sync note

The Alloy-derived files above were copied, not live-referenced, and they will
drift from `alloy-docs-analysis` and from `docs-ai`. Re-sync them periodically
by hand. There's no automated link between the skills or the repos.

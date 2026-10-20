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

## Added after the first dry run (2026-10-20)

- `topic-scope.md` is original to this skill. It is grounded in the Writers' Toolkit topic types (`writers-toolkit/docs/sources/structure/topic-types/`: one topic type per page, concept excludes steps and lookup tables, section pages are landing pages, and the guidance on when tasks may be combined). Its size calibration comes from a one-time measurement of the 47 Beyla pages and has not been tested against real runs, so treat the numbers as a starting point.
- `handoff-editing.md` is original to this skill. It exists because the Keep/Undo review controls come from the host application, not the skill, and the rule has to continue after the analysis ends. It was not verified in every host or mode.

## Added for link style, line breaks, and review_date (2026-10-20)

- `scripts/check_source_format.py` is original to this skill. It reports inline links, lines holding several sentences, lines that wrap mid-sentence, and admonition reference-definition problems. It's read-only. The sentence splitter is a heuristic: its counts are approximate and each reported line must be read before it's reported.
- The reference-style link preference, the rule that an admonition holds its own link definitions, and one sentence per line are **house preferences**, not Writers' Toolkit rules and not Vale rules. The Toolkit Markdown guide describes both link forms and doesn't require one.
- Evidence behind the admonition rule, observed 2026-10-20: the website's admonition partial renders the block body with its own `RenderString` call (`website/layouts/partials/admonition.html`), and in the Alloy docs 55 admonition blocks define their reference links inside the block. No site build was run to confirm the rendering, and the `{{% admonition %}}` form is unverified.
- Counts used for calibration: Beyla (47 pages) had 401 inline links, 0 reference-style links, 379 multi-sentence lines, and 398 lines wrapped mid-sentence; the Alloy `collect/` pages (11 pages) had 28, mostly reference-style, 29, and 8. These came from the working tree on 2026-10-20 (the Beyla branch had local edits to `_index.md`).
- The closing `review_date` suggestion in `references/handoff-editing.md` follows a request to suggest it once all edits are complete. The value format (a quoted `YYYY-MM-DD`) follows the Writers' Toolkit examples.

## Triage findings

`reports/triage-overview.md` was produced on 2026-10-20 by parallel automated
reviewers. Its findings were **not independently verified**. Treat them as
"observed in the 2026-10-20 triage" and re-check against source before relying
on them. The evals refer to them that way, as likely-but-unconfirmed targets.

## Sync note

The Alloy-derived files above were copied, not live-referenced, and they will
drift from `alloy-docs-analysis` and from `docs-ai`. Re-sync them periodically
by hand. There's no automated link between the skills or the repos.

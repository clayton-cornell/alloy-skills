# Beyla docs cleanup proposal

Date: 2026-10-20
Based on: [triage-overview.md](./triage-overview.md) (47 pages: 16 Accurate, 12 Minor, 18 Major, 1 Unverified; ~83 in-page gaps; 9 missing topics)

## Goal

Make the Beyla docs match the code, cover the features users can actually configure, and follow house style. Accuracy and gaps come first. Vale and style come second, as a separate pass.

## Assumptions

- One technical writer drives the work; AI does first-draft verification and edits; the writer reviews every change.
- Estimates are human hours with that AI assistance. They are my estimates, not measured, and are ±30%. A pilot (Phase 0) calibrates them before committing.
- Docs describe the Beyla `main` checkout with the vendored OBI (`go.mod`: `obi v0.15.2`, replaced by the `.obi-src` submodule at commit `517630c`, which isn't checked out here). Phase 0 confirms `vendor/` matches that pin.
- Beyla maintainers are available for ~20–30 hours of review across all PRs (every PR needs `@grafana/beyla` approval).
- Docs-only PRs are accepted in the Beyla repo (its README directs non-doc PRs upstream).

## Phases

### Phase 0: Setup and pilot (20–26 h)

1. **Verify triage Majors.** The triage findings weren't independently re-checked. Re-verify the 18 Majors with the detailed `beyla-docs-analysis` mode (2–4 h).
2. **Add a fix-planning mode to `beyla-docs-analysis`:** per-topic output of proposed replacement text, grouped by edit type (fix, add, new section). The skill already proposes fixes in its detailed report; this adds a structured edit list a writer can apply (2–3 h).
3. **Adapt the style layer for Beyla.** The Alloy skill's style references (frontmatter schema, shortcodes, word list, "don't flag" list, cascade variables) are Alloy-specific. Create Beyla equivalents, or reuse `docs-review` with Beyla's `.vale.ini` (`Grafana` style, `MinAlertLevel = warning`) (4–6 h).
4. **Add a YAML example checker.** The docs have 103 YAML blocks, and Beyla silently ignores unknown keys. Several triage Majors are exactly that (`enable_context_propagation`, `disable_blackbox_cp`, `grafana.otlp.submit`, `k8s.src.pod.name`). Validate every block against `docs/config-schema.json`, applying strict unknown-key rejection in the checker if the schema doesn't enforce it (3–4 h). This catches future regressions too.
5. **Pilot on 3 pages** (one Major config page, one quickstart, one Accurate page with gaps) to measure real time per page, then adjust Phases 1–5.
6. **Confirm the OBI version.** Check that `vendor/` matches the pinned `.obi-src` commit (`517630c`). This needs `git submodule update --init`, which you run (1 h).
7. **Build a Docker test harness.** One compose file per language quickstart plus Kubernetes-free variants of the config examples, run privileged on this host (Linux 7.2.9 with BTF, Docker 29.9.1). Used to regenerate sample output and to run-verify defaults and examples (4–6 h).

### Phase 1: Correct errors (45–60 h)

Fix the 30 pages with confirmed deviations. Do the cross-cutting issues as sweeps first so each fix is applied once:

| Sweep | Pages | Effort |
|---|---|---|
| `routes.unmatched` default is `low-cardinality` | `routes-decorator.md`, 7 quickstarts, `quickstart/kubernetes.md` | 3 h |
| Context-propagation key/env names | `cilium-compatibility.md`, `security.md` | 2 h |
| Messaging metric name and Prometheus suffixes | `metrics.md`, `cardinality.md` | 2 h |
| Kernel 5.17 / `bpf_loop` wording | `_index.md`, `distributed-traces.md` | 2 h |
| Deprecated keys in examples | 3 Helm/network pages | 3 h |
| Regenerate trace-printer sample output | 7 quickstarts + `network/quickstart.md` | 3–4 h using the Phase 0 Docker harness |

Then page-level fixes:

- **11 non-quickstart Majors:** ~3 h each, ~33 h. The heaviest are `controlling-instrumentation.md`, `service-discovery.md`, `metrics-traces-attributes.md`, `metrics.md`, `security.md` (~4–5 h each).
- **12 Minors:** ~1 h each, ~12 h.

### Phase 2: Fill in-page gaps (25–35 h)

About 83 items, mostly table rows, option descriptions and missing enum values (~20 min each). Biggest pages: `export-data.md` (~8), `network/config.md` (~6), `service-discovery.md` (~5), `controlling-instrumentation.md` (~4), `metrics-traces-attributes.md` (~4).

Do this in the same PR as Phase 1 for each page, so a page is edited once for content.

### Phase 3: New topics (30–40 h writer, 8–12 h maintainer review)

| Topic | Writer | SME review |
|---|---|---|
| Kubernetes metadata cache service | 6 h | 2 h |
| TCP stats section (`stats:`) | 4 h | 2 h |
| Cloud metadata | 3 h | 1 h |
| GenAI export to Grafana AI (`sigil_export`) | 3 h | 2 h |
| .NET runtime metrics | 1 h | — |
| Single options (host ID, `metadata_retry`, `target_pids`, `log_config`, `override_bpfloop_enabled`) | 3 h | 1 h |
| Config JSON schema section | 1.5 h | — |
| Troubleshooting page (startup failures, silent key ignoring) | 8 h | 2 h |
| Upgrade/deprecation guide | 6 h | 1 h |
| Helm chart reference gaps (`preset`, `privileged`, `k8sCache`) and Alloy-integration pointer | 3 h | 1 h |

The task-style topics can reuse `develop-task-topic` for structure; the reference-style ones follow the existing `configure/` pages.

### Phase 4: House style (25–35 h)

Run Vale and the manual style checklist on all 47 pages (8,368 lines) as a separate pass: heading case, voice and tense, "refer to", frontmatter (`review_date`, `description`, `keywords`), shortcodes, link style, admonitions, and the `Grafana.Paragraphs = NO` suppressions. ~30 min per page, ~1 h for the larger prose pages (`cardinality.md`, `cilium-compatibility.md`, `obi.md`, `_index.md`).

Reuse `docs-review`, and `persona-check` for the audience question on the quickstarts and setup pages. Keep this separate from Phases 1–3 so accuracy PRs stay small and reviewable. For pages that get heavy rewrites in Phase 3, apply style once at the end of that work.

### Phase 5: QA and release (12–18 h)

SME review of Majors, a docs build, link check, the YAML checker run, and a final re-run of triage mode to confirm the counts dropped. Also set `review_date` on every touched page.

## Effort summary

| Phase | Writer hours | Beyla maintainer hours |
|---|---|---|
| 0. Setup, test harness, pilot | 20–26 | 1 |
| 1. Correct errors | 45–60 | 4–6 |
| 2. Fill in-page gaps | 25–35 | 2–4 |
| 3. New topics | 30–40 | 8–12 |
| 4. House style | 25–35 | 3–5 |
| 5. QA and release | 12–18 | 2–3 |
| **Total** | **~160–215 h (about 4–5.5 weeks, one person)** | **~20–31 h** |

Without AI-assisted verification and drafting, expect roughly double. Calendar time depends more on maintainer review turnaround than on writing time: with about 10–12 PRs needing `@grafana/beyla` approval, ask the team now for a review cadence (for example, a fixed weekly slot).

## Delivery plan

About 10–12 PRs, smallest and highest-value first:

1. Cross-cutting corrections (routes default, context propagation, metric name, kernel wording). Quick win, ~1 week.
2. Quickstarts, including regenerated output.
3. `configure/` accuracy and gaps, in 3 PRs split like the triage batches.
4. `setup/` and `network/`.
5. Top-level pages (`metrics.md`, `security.md`, `cardinality.md`, `cilium-compatibility.md`).
6. New topics, one PR each, each with SME review.
7. Style pass, in 3–4 PRs by section.

## Decisions

| # | Decision | Resolution | Effect on plan |
|---|---|---|---|
| 1 | Target version | Whatever Beyla builds against. `go.mod` pins `obi v0.15.2` and replaces it with the `.obi-src` submodule at commit `517630c`; `vendor/` is what the checkout compiles. | Phase 0 confirms `vendor/` matches the pinned commit. Until then, `obi.md`'s `application_jvm` stays an open item, not a deviation. |
| 2 | GenAI policy | Same as Alloy: Claude helps produce the docs. Beyla has no PR template, `CONTRIBUTING.md` or GenAI policy file that I could find; `.github/` only has `instructions/`, `prompts/` and workflows. | You write PR descriptions and all review replies. AI drafts doc content and PR titles only. Confirm with the maintainers that this is acceptable in the Beyla repo, since nothing is written down. |
| 3 | Reviewers | You author; Beyla maintainers approve. `CODEOWNERS` assigns `@grafana/beyla` to everything, so every PR needs that team. | Maintainer hours cover approvals on every PR, not just the new pages. |
| 4 | Sample output regeneration | Test runs are possible. This machine has Linux 7.2.9, BTF (`/sys/kernel/btf/vmlinux`) and Docker 29.9.1, which meet Beyla's kernel 5.8+/BTF requirement, so Beyla and the example apps can run in privileged containers here. | Phase 0 builds a reusable Docker harness (~4–6 h). It also lets us verify behavior claims (defaults, kernel fallbacks) by running Beyla, not only by reading code. |
| 5 | Scope | Everything. No pages or topics deferred. | The totals already include troubleshooting and the upgrade guide, so they don't change. |

## Risks

- Triage findings are unverified until Phase 0 step 1.
- Beyla has no written GenAI or contribution policy; confirm expectations with the maintainers before the first PR.
- Docs and code move; the longer this takes, the more drifts. Land the cross-cutting PR early and rerun triage mode before the style pass.
- Unknown keys are silently ignored, so correct-looking examples can still be wrong. The YAML checker mitigates this for config blocks but not for prose.
- Third-party content (Alloy, k8s-monitoring chart, Grafana Cloud UI, published images) can't be verified from this repo and needs separate owners.

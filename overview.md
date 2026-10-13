# Alloy component docs audit: code-side defect catalog

Compiled: 2026-10-09
Repo: [grafana/alloy]
Scope: `remote.*`, `pyroscope.*` and `prometheus.*` component reference validation (docs checked against component source code)

This catalog lists defects and open questions that the doc audits exposed in the **source code** and that were deferred to developers. It covers fixed, resolved and open items. Doc-wording fixes are excluded and listed in the appendix.

**Where things live:** items judged to be real code bugs are written up for the dev team in [code-issues.md](code-issues.md). Fixed and closed items are in [closed-items.md](closed-items.md). This file keeps a verdict and a link for each, plus anything still being checked.

Two evidence streams are merged here: the PR descriptions, commit lists and review threads for the audit PRs; and the agent session history plus repo-memory deferral notes written during those same reviews. Where they disagree, the discrepancy is called out in the item.

---

## 1. Summary

| Measure                                      | Count |
| -------------------------------------------- | ----- |
| Confirmed code defects                       | 16    |
| Fixed by a code change                       | 1     |
| Resolved by removing the component           | 1     |
| Open                                         | 14    |
| Lower-confidence findings and open questions | 6     |

Confirmed defects by type:

| Type                                 | Count | Items     |
| ------------------------------------ | ----- | --------- |
| Crash                                | 1     | 1         |
| Non-functional argument              | 2     | 2, 3      |
| Silently ignored arguments or config | 3     | 4, 10, 14 |
| Non-functional component             | 1     | 5         |
| Wrong metric                         | 1     | 6         |
| Bad or missing default               | 3     | 7, 9, 11  |
| Wrong output                         | 1     | 8         |
| Missing or misplaced validation      | 2     | 12, 15    |
| Missing implementation               | 1     | 13        |
| Silent data loss in the converter    | 1     | 16        |

Confirmed defects by area: 10 in `prometheus.*` (items 1, 2, 3, 4, 5, 8, 9, 10, 11, 12), 4 in `pyroscope.*` (items 6, 7, 13, 14), 0 in `remote.*`, 2 in shared `common/config` used by both `prometheus.*` and `remote.*` (items 15, 16).

Docs impact: the validated docs describe real behaviour rather than advertising features that do not work. For kafka, the doc keeps `kafka_uris` as required, which matches actual behaviour (the integration rejects an empty value at build; see Item 1). For mssql, mongodb, cloudwatch (`static`) and consul, the doc states or works around the current behaviour and needs reverting if the source is fixed.

> **Validation pass in progress (started 2026-10-13).** Items are being re-verified against source one at a time. The counts and type tables above are **not yet reconciled** and still reflect the original catalog. Reclassified so far:
>
> - **Item 1** (kafka): reclassified, low severity, see [code-issues.md](code-issues.md). The type table above still lists it under "Crash"; when the pass is complete, move it and update the totals.
> - **Item 2** (mongodb): confirmed on the Alloy side, medium severity, see [code-issues.md](code-issues.md).
> - **Item 3** (mssql): confirmed, low severity, see [code-issues.md](code-issues.md).
> - **Item 4** (cloudwatch `static`): confirmed, low severity, see [code-issues.md](code-issues.md).
> - **Item 8** (consul): confirmed, medium severity, see [code-issues.md](code-issues.md).
> - **Item 9** (github `github_rate_limit`): confirmed, medium severity, see [code-issues.md](code-issues.md).
> - **Item 10** (github partial App config): confirmed, low severity, see [code-issues.md](code-issues.md).
> - **Item 11** (cadvisor `allowlisted_container_labels`): not a bug, `Convert()` normalises `[]` to `[""]`, so the doc is right. Moved to [closed-items.md](closed-items.md).
> - **Item 12** (`prometheus.echo` `format`): possible issue, low severity, needs a dev decision, see [code-issues.md](code-issues.md).
> - **Item 5** (catchpoint): fixed by removal in #7309, merged 2026-10-13 (reported by the author). Moved to [closed-items.md](closed-items.md). When reconciling, it still counts under "Resolved by removing the component" above, which is now correct.
> - **Item 6** (`pyroscope.ebpf` samples counter): fixed by #7119. Moved to [closed-items.md](closed-items.md).
> - **Item 7** (`pyroscope.scrape` timeout): not a bug, the scrape loop extends the timeout for delta profiles. Moved to [closed-items.md](closed-items.md).
> - **Item 14** (`pyroscope.java` `thread` block): not applicable to the current source, the block is not in the tree. Moved to [closed-items.md](closed-items.md).
> - **Items 15 and 16** (shared `oauth2` block): cannot be verified against the current source. The JWT fields are not in the tree, and the feature branch's PR number is unverified.
> - **Item 13** (`pyroscope.ebpf` debug information): a doc error, not a source defect, fixed in the doc and committed on a branch (PR and merge unconfirmed). Moved to [closed-items.md](closed-items.md). When the pass is complete, remove both from the type tables and the confirmed and open totals above, which still count them.

---

## 2. Confirmed code defects

Items 1 to 8 keep their original catalog numbering so earlier cross-references still resolve. Items 9 to 16 come from the agent session history and repo-memory deferral notes.

Fixed items keep a one-line pointer here, in numeric position (**Item N:** Fixed, linked to the entry). All details are in [closed-items.md](closed-items.md). Their numbers are not reused.

### Item 1: `prometheus.exporter.kafka`: `instance` ignored with one URI; `kafka_uris` not validated

- **Verdict:** real, low severity. `instance` is ignored when there is one URI, and `kafka_uris` is required but tagged optional. Details and evidence: [code-issues.md](code-issues.md#item-1-prometheusexporterkafka-instance-ignored-with-one-uri-kafka_uris-not-validated)
- **Type:** Silently ignored argument (`instance`) and Misplaced validation (`kafka_uris`).
- **Source PR:** [#7335]

### Item 2: `prometheus.exporter.mongodb`: `enable_profile` has no effect

- **Verdict:** real, medium severity. Alloy never sets the upstream option that profile collection depends on. The upstream condition itself is for the devs to confirm. Details: [code-issues.md](code-issues.md#item-2-prometheusexportermongodb-enable_profile-has-no-effect)
- **Type:** Non-functional argument
- **Source PR:** [#7335]
- **Docs:** left unchanged on purpose; accurate once fixed. Do not add a "no effect" note, and do not add a `mongos` caveat here (that applies to `currentop_slow_time`).

### Item 3: `prometheus.exporter.mssql`: `connection_name` never becomes a metric label

- **Verdict:** real, low severity. A non-empty `connection_name` enables the `up` and `scrape_duration_seconds` metrics but no label is created, because Alloy passes a non-nil empty label map to the SQL exporter library. Details: [code-issues.md](code-issues.md#item-3-prometheusexportermssql-connection_name-never-becomes-a-metric-label)
- **Type:** Non-functional argument
- **Source PR:** [#7335]
- **Docs:** the doc at HEAD describes a label. If the source is fixed, keep describing the label. The part-06 doc wording was not checked.

### Item 4: `prometheus.exporter.cloudwatch`: `static` block accepts `period`, `length` and `delay` but ignores them

- **Verdict:** real, low severity. The static-job conversion never reads the three job-level values, so they have no effect. Details: [code-issues.md](code-issues.md#item-4-prometheusexportercloudwatch-static-block-accepts-period-length-and-delay-but-ignores-them)
- **Type:** Silently ignored arguments
- **Source PR:** [#7281] (open)
- **Docs:** the `static` table at HEAD does not list them. Per the part-04 PR description, that branch documents them as having no effect (a note in `static` and an inheritance sentence in `metric`). That text was not read. Revert both if the source is fixed.

**Item 5:** [Fixed](closed-items.md#item-5-prometheusexportercatchpoint-non-functional-component-removed)

**Item 6:** [Fixed](closed-items.md#item-6-pyroscopeebpf-pyroscope_ebpf_pprof_samples_total-counts-bytes)

**Item 7:** [Not a bug](closed-items.md#item-7-pyroscopescrape-default-scrape_timeout-shorter-than-the-default-cpu-profile-duration--not-a-bug)

### Item 8: `prometheus.exporter.consul`: `server` without a scheme gives `instance` the value `unknown`

- **Verdict:** real, medium severity. A `server` address without a scheme, including the doc's own `localhost:8500` example, gives every target `instance="unknown"`. Details: [code-issues.md](code-issues.md#item-8-prometheusexporterconsul-server-without-a-scheme-gives-instance-the-value-unknown)
- **Type:** Wrong output
- **Source PR:** [#7281] (open)
- **Docs:** part-04 (unmerged, head `c5dc82d`) tells users to set `server` to an address that includes a scheme. That is a workaround, since the exporter accepts the address. Revisit it if the source is fixed.

### Item 9: `prometheus.exporter.github`: `github_rate_limit` has no Alloy default, so GitHub App re-auth never triggers

- **Verdict:** real, medium severity. The component default is `0` instead of the intended `15000`, so the re-authentication threshold is never met. Details: [code-issues.md](code-issues.md#item-9-prometheusexportergithub-github_rate_limit-has-no-alloy-default-so-github-app-re-auth-never-triggers)
- **Type:** Missing default
- **Source PR:** none yet. [#7284] (docs part 05) merged without it.
- **Docs:** leave the default at `15000`. It is the intended value.

### Item 10: `prometheus.exporter.github`: a partial GitHub App configuration is silently ignored

- **Verdict:** real, low severity. Setting only one or two of the three GitHub App arguments gives no error and no log line, and the exporter runs unauthenticated or on the token. Details: [code-issues.md](code-issues.md#item-10-prometheusexportergithub-a-partial-github-app-configuration-is-silently-ignored)
- **Type:** Silently ignored config
- **Source PR:** none yet. [#7284] (docs part 05) merged without it.
- **Docs:** not documented, by choice. The health section already covers invalid configuration in general.

**Item 11:** [Not a bug](closed-items.md#item-11-prometheusexportercadvisor-allowlisted_container_labels-default--not-a-bug)

### Item 12: `prometheus.echo`: an unknown `format` is accepted and falls back to `text`

- **Verdict:** possible issue, low severity, needs a dev decision. An unknown `format` gives a warning and `text` output with no error or health signal, where the doc says it "Must be `text` or `openmetrics`". Whether the leniency is intended is the open question. Details: [code-issues.md](code-issues.md#item-12-prometheusecho-an-unknown-format-is-accepted-and-falls-back-to-text)
- **Type:** Missing validation
- **Source PR:** [#7270] (part 03)
- **Docs:** updated to describe the current behaviour (working tree, uncommitted). Revisit if validation is added.

**Item 13:** [Fixed](closed-items.md#item-13-pyroscopeebpf-documented-debug-information-capability-is-not-implemented)

**Item 14:** [Not applicable](closed-items.md#item-14-pyroscopejava-thread-block-silently-no-ops-when-both-frame-and-label_name-are-unset--not-applicable)

### Item 15: `oauth2` block: `signature_algorithm` is validated under the wrong grant type

- **Verdict:** cannot be verified against the current source. The current shared `oauth2` block has no grant type, `signature_algorithm` or other JWT fields: `OAuth2Config` in `internal/component/common/config/types.go` has only the basic fields, and its `Validate()` (from `:432`) checks `client_id`, a client secret, and `token_url`. The finding comes from the feature branch `feat/http-oauth2-add-client-private-key`. Its fetch history names PR 7130, which is **unverified**, and the branch code was not read.
- **Type:** Validation under the wrong condition, in the branch
- **Scope note:** the shared `oauth2` block is used by many `prometheus.*`, `remote.*` and `discovery.*` pages, so the PR matters for the docs when it merges.
- **Finding to raise on that PR (from earlier notes, not re-verified):** the RS256/RS384/RS512 check sits under the client-credentials case. Upstream `prometheus/common` validates it under jwt-bearer. The fix is to move it.
- **Next step:** confirm 7130 is the right PR and whether it is relevant. If so, raise the finding there. If not, close as not applicable.

### Item 16: `oauth2` converter drops `Iss`, `Audience` and `Claims`

- **Verdict:** cannot be verified against the current source, for the same reason as Item 15. In the current tree `toOAuth2` (`internal/converter/internal/common/http_client_config.go`) maps only `ClientID`, `ClientSecret`, `ClientSecretFile`, `Scopes`, `TokenURL`, `EndpointParams`, the proxy config and TLS config, which matches the current `OAuth2Config`. The three fields would only matter once the shared block supports JWT bearer.
- **Type:** Silent data loss in the converter, in the branch
- **Finding to raise on that PR (from earlier notes, not re-verified):** the converter omits `Iss`, `Audience` and `Claims`, so a converted config loses JWT-bearer claims. The fix is to carry them through.
- **Next step:** as for Item 15.

---

## 3. Lower-confidence findings and open questions

These are behaviours or open questions, not confirmed defects. Each needs a developer answer before it can be filed or documented.

| # | Component | Finding | Status | Source |
|---|---|---|---|---|
| L1 | `pyroscope.java` | `per_thread` does not apply to async-profiler JFR mode; korniltsev believes enabling it would break profiling (untested) and suggests removing or deprecating the flag. Tracked in [issue #5340]. Earlier notes record a `thread` block replacement on a local branch (`threads_fix`). It is not in the current tree: `args.go` still has `tlab` and no `thread` block, and the doc at HEAD (`pyroscope.java.md:196-199`) only says `per_thread` doesn't apply to JFR output. | Open, tracked | [#7099] |
| L2 | `pyroscope.ebpf` | `pyroscope_ebpf_profiling_sessions_total` is incremented right after `controller.Start` succeeds, so it counts sessions started, not completed. Same family of metric-semantics mismatch as item 6 (now in [closed-items.md](closed-items.md)). **The doc is not wrong** — it already reads "Number of profiling sessions started by the eBPF component" (verified 2026-10-09), so this is a metric-naming question only. | Open | [#7099] |
| L3 | `remote.vault` | `data` handling accepts `string` and `[]byte` values and silently ignores other types (`internal/component/remote/vault/vault.go:279-293`). Possibly intended. | Open | [#7097], backport [#7118] |
| L5 | `prometheus.exporter.azure` | `azure_cloud_environment` also accepts `ussec`, `azuresecret` and `azurepsecretcloud` in the vendored `webdevops/go-common` cloudconfig library (`cloudconfig.NewCloudConfig()`), none of which are documented. These and the documented `azurepprivatecloud` need `AZURE_CLOUD_CONFIG` / `AZURE_CLOUD_CONFIG_FILE` env vars to work. Needs a developer answer on whether these values are supported before documenting them. | Needs confirmation | [#7107], backport [#7267] |
| L7 | `pyroscope.write` | `pyroscope_ebpf_debug_info_upload_bytes_total` is emitted by `pyroscope.write` but carries an `ebpf` prefix. Introduced in PR [#4948] alongside the ebpf `debug_info` block, and named for the feature rather than the emitting component. Git history shows no earlier or parallel copy in the `ebpf` package, so an initial "copy-paste bug" characterisation was explicitly withdrawn. **Explained by the code owner (Slack):** the metric was meant for the ebpf component and was then moved to `pyroscope.write`, which is why the name carries `ebpf`. He does not mind renaming it, but wants the whole debug-info feature to stay undocumented. Low severity, and moot for docs since the metric is undocumented. | Explained; rename optional and low priority | [#7099] |
| L8 | `prometheus.exporter.cloudwatch` | A reviewer (dehaansa) asked what the sentence about `length` and `period` request windows means. The author reworked it from `config.go` comments but could not validate the behaviour inside YACE requests. The head commit of part-04 (`c5dc82d`, 2026-10-07) rewords it again: with no `length`, each metric's `length` equals its `period`, so Alloy takes the maximum period as `length` and the minimum as `period`. That wording still comes from `config.go` and was not checked against YACE. | Needs developer or YACE confirmation | [#7281] |

---

## 4. Intentionally undocumented surface

Not defects. Functionality that exists in code and was deliberately left out of the docs at the code owner's request. Recorded here so the gap is traceable rather than mistaken for a completeness failure in a later review.

**Reason (confirmed by the code owner, korniltsev-grafanista, in Slack; undated export, but before #7099 merged on Sep 16 and #7119 was opened):** the debug-info feature is highly experimental. It is mostly needed to dogfood server-side code, and both the Alloy side and the database side are expected to change significantly. It is deliberately undocumented so it can be removed or broken later without a compatibility commitment. There is no timeline or condition for documenting it.

| Component | Withheld from the docs | Source |
|---|---|---|
| `pyroscope.ebpf` | The `debug_info` block and its arguments (`cache_size`, `on_target_symbolization`, `queue_size`, `strip_text_section`, `upload`, `worker_num`); debug metrics `pyroscope_ebpf_pprofs_dropped_total`, `pyroscope_ebpf_pprof_bytes_total`, `pyroscope_ebpf_pprof_samples_total`, `pyroscope_forwarded_entries_total`. The Blocks section was restored to "doesn't support any blocks." | [#7099] |
| `pyroscope.write` | The `tracing` block (`jaeger_propagator`, `trace_context_propagator`), the `debug_info_upload_timeout` endpoint argument, and `pyroscope_ebpf_debug_info_upload_bytes_total`. | [#7099] |
| `pyroscope.receive_http` | `debug_info_upload_timeout`, the debug-info upload proxy endpoint (`POST /debuginfo.v1alpha1.DebuginfoService/Upload/{gnu_build_id}`) with its first-receiver-only forwarding behaviour, and metric `pyroscope_receive_http_debuginfo_downstream_calls_total`. | [#7099] |

**Per-item notes from the same Slack conversation:**

- **`pyroscope.ebpf` `debug_info` block:** history is PR #4948 (added), #5391 (removed, with its docs), #5891 (added back to the component, docs not restored). The missing docs after #5891 were intentional, not an oversight, so there is nothing to restore.
- **`pyroscope.write` `tracing` block:** added in #4354. The code owner has only tested the Jaeger knob and expects Pyroscope to move from Jaeger to OpenTelemetry, which would add a new knob and deprecate the others. Left undocumented to keep the freedom to remove it.
- **`pyroscope_ebpf_debug_info_upload_bytes_total` on `pyroscope.write`:** see L7. The code owner prefers it stay undocumented.

**Source comments:** the agreed convention is to mark intentionally undocumented items with inline comments in the **source**, not in the docs. The code owner referenced PR #7127 for these comments. Its merge status and exact wording were not checked. The audit skill already looks for such comments when it finds something undocumented. Reason for source-only: one place to maintain, and a docs comment could mislead an agent that reads an older doc version after the feature is documented.

Two sub-questions from the same review:

- **Unanswered:** what is the intended default for `strip_text_section`? The Go zero value `false` was used, since `NewDefaultArguments` does not set it.
- **Answered by the code owner:** is `debug_info` meant to be user-facing? No. It is intentionally undocumented and experimental (see Reason above).

---

## 5. PR index

| PR                                        | Title / scope                                      | Status                        | Backports                 | Items                                 |
| ----------------------------------------- | -------------------------------------------------- | ----------------------------- | ------------------------- | ------------------------------------- |
| [#7097]                                   | Validate `remote.*` topics                         | Merged                        | [#7118] merged (v1.19)    | L3                                    |
| [#7099]                                   | Validate `pyroscope.*` topics                      | Merged Sep 16                 | [#7124] merged (v1.19)    | Items 6, 7, 13; L1, L2, L7; section 4 |
| [#7107]                                   | `prometheus.*` part 01                             | Merged                        | [#7267] merged (v1.20)    | L5                                    |
| [#7111]                                   | `prometheus.*` part 02                             | Merged Sep 29                 | [#7266] merged (v1.20)    | Item 5                                |
| [#7270]                                   | `prometheus.*` part 03, second pass                | Merged Oct 7                  | [#7328] merged            | Items 11, 12                          |
| [#7281]                                   | `prometheus.*` part 04 (consul, cloudwatch)        | Open                          | Labelled `backport/v1.20` | Items 4, 8; L8                        |
| [#7284]                                   | `prometheus.*` part 05                             | Merged Oct 7                  | [#7332] merged            | **Items 9, 10 — merged without them** |
| [#7335]                                   | `prometheus.*` part 06                             | Open (shown as draft)         | None yet                  | Items 1, 2, 3                         |
| [#7320]                                   | Second pass, `pyroscope.*`                         | Merged Oct 7                  | [#7331] merged            | None (style only)                     |
| [#7321]                                   | Second pass, `remote.*`                            | Merged                        | [#7330] merged            | None (content split from [#7270])     |
| [#7119]                                   | Fix `pyroscope.ebpf` samples counter               | Merged (per author)           | Unknown                   | Resolves item 6                       |
| [#7309]                                   | Remove `prometheus.exporter.catchpoint`            | Merged Oct 13 (per author)    | Unknown                   | Resolves item 5 (see [closed-items.md](closed-items.md))                       |
| `feat/http-oauth2-add-client-private-key` | oauth2 block partial review, 2026-10-08            | Branch; fetch history names PR 7130 (unverified) | —                         | Items 15, 16                          |

---

## 6. Verification checklist

Open questions that should be settled before this catalog is presented.

- **Items 9 and 10 have no home.** [#7284] merged Oct 7 without them. Both are written up in [code-issues.md](code-issues.md) and still need a tracking issue or a follow-up PR.
- **#7119:** backported to any release branch?
- **Items 15 and 16:** is PR 7130 (named in the branch's fetch history) the right PR, and is it relevant to the audit? Not verified.
- **Items 1, 2, 3, 4, 8, 13 and L1 to L3:** does a tracking issue or fix PR already exist for each?
- **Total number of components audited**, for any defects-per-component rate. Not known.

Closed during this pass, 2026-10-09:

- `remote.vault` `AWS_SESSION` versus `AWS_SESSION_TOKEN` — resolved. See the appendix.
- L2's doc wording — already correct, says "started".
- Item 9 — re-verified live against the current tree.

---

## 7. Method and limits

- **Stream one:** PR descriptions, commit lists and review threads for the PRs above, read through GitHub page fetches and the public GitHub API in a browser session. No GitHub connector was available. Bot comments from `github-actions` were excluded. Only the first 100 comments per endpoint per PR were read.
- **Stream two:** agent session history for the audit branches (`docs/validate-update-remote`, `docs/validate-update-pyroscope`, `docs/validate-prometheus-component-docs-part-01` through `part-06`, plus `threads_fix` and a skill stress-test session), and the deferral notes written into repo memory during those reviews.
- A small number of checks were re-run against the local working tree on 2026-10-09 and are marked inline where that happened. Everything else was verified at the time it was recorded and has not been re-verified.
- Nothing here was reproduced by running Alloy, with two exceptions: the consul instance-key behaviour (scratch Go program, 2026-10-01) and the `remote.kubernetes.secret` example (`alloy validate`, exit 0).
- Causes are as stated in the PR notes, review comments and session transcripts, which in several cases came from Claude or Copilot analysis.
- "Open" means no fix or tracking issue was seen. Some may already be fixed.

---

## Appendix: excluded docs-only fixes

Doc-side issues the review turned up that are **not yet fixed**. None are source defects. Re-checked against the `alloy` working tree on 2026-10-13 (branch `docs/correct-minor-errors-component-docs`, cut from `main`). The seven rows that are fixed have moved to [closed-items.md](closed-items.md#docs-only-fixes-from-the-overview-appendix).

Two open branches are not in that tree: `docs/validate-prometheus-component-docs-part-04` (consul, cloudwatch; [#7281], open, head `c5dc82d`) and `docs/validate-prometheus-component-docs-part-06` ([#7335]). Rows whose fix belongs on one of them are marked. For part-04, only the consul scheme wording and the head commit's cloudwatch `length`/`period` wording were read; the cloudwatch rows below were not checked on that branch.

| Component | Issue | Resolution |
|---|---|---|
| `prometheus.exporter.cloudwatch` | `dimension_name_requirements` Default cell renders `{}` (map syntax) on a `list(string)`. | Doc cell notation only. **Still unfixed at HEAD:** the cell reads `{}` at `prometheus.exporter.cloudwatch.md:219` and `:324`. **Fix belongs on part-04** ([#7281]), which is unmerged and not in this tree. Lowest priority. |
| `prometheus.exporter.cloudwatch` | The Usage section is not a minimal `"<LABEL>"` skeleton, unlike every other validated exporter topic. | Structure, not source. Raised for a developer opinion but carries no code change. **Still the case at HEAD:** Usage is a full example with a `discovery` block. **Belongs on part-04** if it changes. |
| `prometheus.scrape` | `scheme` default is `"http"` in source but documented as empty; `body_size_limit` typed `int` in the doc versus `units.Base2Bytes` in source, which accepts both `104857600` and `"100MiB"`. | Doc drift found in a pre-audit stress-test session. **Still unfixed at HEAD, source re-verified 2026-10-13:** `scrape.go:163` sets `Scheme: "http"` while the doc Default cell is blank (`prometheus.scrape.md:82`), and `scrape.go:92` types `BodySizeLimit` as `units.Base2Bytes` while the doc says `int` (`prometheus.scrape.md:54`). Doc-only fix. **Deferred:** the `prometheus.scrape` topic is due for a full audit, and these fixes will be applied then. `prometheus.scrape` is not among the components known to be in the two open branches. |
| `oauth2` block | `client_id` Required documented as `no`; `Validate()` enforces it identically to `token_url`. | **Changed, but the doc and the code still disagree (checked 2026-10-13).** The shared partial (`shared/reference/components/oauth2-block.md`) now shows `client_id` and `token_url` both as Required `no`, so the original inconsistency between them is gone. But `OAuth2Config.Validate()` (`internal/component/common/config/types.go`, from line 432) rejects a block that lacks `client_id`, lacks `token_url`, or has neither `client_secret` nor `client_secret_file`, while the struct tags mark all of these `optional`. Whether the table should say `yes` depends on how the docs treat attributes enforced in `Validate()`, which I did not check. **Needs a convention decision.** |

[auth.go]: https://github.com/grafana/alloy/blob/main/internal/component/remote/vault/auth.go
[catchpoint_exporter.go]: https://github.com/grafana/alloy/blob/main/internal/static/integrations/catchpoint_exporter/catchpoint_exporter.go
[cloudwatch-config.go]: https://github.com/grafana/alloy/blob/main/internal/component/prometheus/exporter/cloudwatch/config.go
[consul_exporter.go]: https://github.com/grafana/alloy/blob/main/internal/static/integrations/consul_exporter/consul_exporter.go
[exporter.go]: https://github.com/grafana/alloy/blob/main/internal/component/prometheus/exporter/exporter.go
[github.go]: https://github.com/grafana/alloy/blob/main/internal/component/prometheus/exporter/github/github.go
[github_exporter.go]: https://github.com/grafana/alloy/blob/main/internal/static/integrations/github_exporter/github_exporter.go
[http_client_config.go]: https://github.com/grafana/alloy/blob/main/internal/converter/internal/common/http_client_config.go
[metrics.go]: https://github.com/grafana/alloy/blob/main/internal/component/pyroscope/ebpf/metrics.go
[send.go]: https://github.com/grafana/alloy/blob/main/internal/component/pyroscope/ebpf/send.go
[types.go]: https://github.com/grafana/alloy/blob/main/internal/component/common/config/types.go

[grafana/alloy]: https://github.com/grafana/alloy
[issue #5340]: https://github.com/grafana/alloy/issues/5340
[#4948]: https://github.com/grafana/alloy/pull/4948
[#7097]: https://github.com/grafana/alloy/pull/7097
[#7099]: https://github.com/grafana/alloy/pull/7099
[#7107]: https://github.com/grafana/alloy/pull/7107
[#7111]: https://github.com/grafana/alloy/pull/7111
[#7118]: https://github.com/grafana/alloy/pull/7118
[#7119]: https://github.com/grafana/alloy/pull/7119
[#7124]: https://github.com/grafana/alloy/pull/7124
[#7266]: https://github.com/grafana/alloy/pull/7266
[#7267]: https://github.com/grafana/alloy/pull/7267
[#7270]: https://github.com/grafana/alloy/pull/7270
[#7281]: https://github.com/grafana/alloy/pull/7281
[#7284]: https://github.com/grafana/alloy/pull/7284
[#7309]: https://github.com/grafana/alloy/pull/7309
[#7320]: https://github.com/grafana/alloy/pull/7320
[#7321]: https://github.com/grafana/alloy/pull/7321
[#7328]: https://github.com/grafana/alloy/pull/7328
[#7330]: https://github.com/grafana/alloy/pull/7330
[#7331]: https://github.com/grafana/alloy/pull/7331
[#7332]: https://github.com/grafana/alloy/pull/7332
[#7335]: https://github.com/grafana/alloy/pull/7335

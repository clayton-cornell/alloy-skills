# Alloy component docs audit: overview

Compiled: 2026-10-09. Last updated: 2026-10-13.
Repo: [grafana/alloy]
Scope: `remote.*`, `pyroscope.*` and `prometheus.*` component reference validation (docs checked against component source code).

This file tracks the source-code issues and open questions that the docs audit exposed. It keeps a verdict and a link for each item.

- **[code-issues.md](code-issues.md):** items judged to be real code issues, written up for the dev team.
- **[closed-items.md](closed-items.md):** items that are fixed, were not bugs, or do not apply, plus docs-only fixes that are done.

---

## 1. Summary

Of the 16 numbered items, 8 are open code issues, 3 are fixed, 3 turned out not to be bugs, and 2 are findings on an unmerged branch.

| Status                                                 | Count | Items                    |
| ------------------------------------------------------ | ----- | ------------------------ |
| Open code issues (in [code-issues.md](code-issues.md)) | 8     | 1, 2, 3, 4, 8, 9, 10, 12 |
| Fixed                                                  | 3     | 5, 6, 13                 |
| Not a bug, or not applicable                           | 3     | 7, 11, 14                |
| Pre-merge review findings (unmerged branch)            | 2     | 15, 16                   |

- **Open code issues:** 3 medium (items 2, 8, 9) and 5 low (items 1, 3, 4, 10, 12). Item 12 is a possible issue that needs a dev decision. All 8 are in `prometheus.*`.
- **Also tracked:** 3 new unvalidated findings (section 2), 6 lower-confidence findings (section 5), and 4 doc-side items not yet fixed (appendix).

---

## 2. Items

Item numbers are stable and match [closed-items.md](closed-items.md). [code-issues.md](code-issues.md) numbers its issues separately, and its index maps them to these items. Each verdict links to its details.

| Item | Component | Issue | Verdict |
|---|---|---|---|
| 1 | `prometheus.exporter.kafka` | `instance` is ignored when there is one URI; `kafka_uris` is required but tagged optional | [Real, low](code-issues.md#issue-1-prometheusexporterkafka-instance-ignored-with-one-uri-kafka_uris-not-validated) |
| 2 | `prometheus.exporter.mongodb` | `enable_profile` has no effect | [Real, medium](code-issues.md#issue-2-prometheusexportermongodb-enable_profile-has-no-effect) |
| 3 | `prometheus.exporter.mssql` | `connection_name` enables `up` and scrape-duration metrics but never becomes a label | [Real, low](code-issues.md#issue-3-prometheusexportermssql-connection_name-never-becomes-a-metric-label) |
| 4 | `prometheus.exporter.cloudwatch` | `static` block accepts `period`, `length` and `delay` but ignores them | [Real, low](code-issues.md#issue-4-prometheusexportercloudwatch-static-block-accepts-period-length-and-delay-but-ignores-them) |
| 5 | `prometheus.exporter.catchpoint` | Component did not function | [Fixed](closed-items.md#item-5-prometheusexportercatchpoint-non-functional-component-removed) (removed, [#7309]) |
| 6 | `pyroscope.ebpf` | `pyroscope_ebpf_pprof_samples_total` counted bytes | [Fixed](closed-items.md#item-6-pyroscopeebpf-pyroscope_ebpf_pprof_samples_total-counts-bytes) ([#7119]) |
| 7 | `pyroscope.scrape` | Default `scrape_timeout` shorter than the default CPU profile | [Not a bug](closed-items.md#item-7-pyroscopescrape-default-scrape_timeout-shorter-than-the-default-cpu-profile-duration--not-a-bug) |
| 8 | `prometheus.exporter.consul` | A `server` address without a scheme sets `instance` to `unknown` | [Real, medium](code-issues.md#issue-5-prometheusexporterconsul-server-without-a-scheme-gives-instance-the-value-unknown) |
| 9 | `prometheus.exporter.github` | `github_rate_limit` defaults to `0`, so GitHub App re-auth never triggers | [Real, medium](code-issues.md#issue-6-prometheusexportergithub-github_rate_limit-has-no-alloy-default-so-github-app-re-auth-never-triggers) |
| 10 | `prometheus.exporter.github` | A partial GitHub App configuration is silently ignored | [Real, low](code-issues.md#issue-7-prometheusexportergithub-a-partial-github-app-configuration-is-silently-ignored) |
| 11 | `prometheus.exporter.cadvisor` | `allowlisted_container_labels` is `[""]` in code, `[]` in the doc | [Not a bug](closed-items.md#item-11-prometheusexportercadvisor-allowlisted_container_labels-default--not-a-bug) |
| 12 | `prometheus.echo` | An unknown `format` is accepted and falls back to `text` | [Possible issue, low](code-issues.md#issue-8-prometheusecho-an-unknown-format-is-accepted-and-falls-back-to-text), needs a dev decision |
| 13 | `pyroscope.ebpf` | `## Debug information` documented output the component can't produce | [Fixed](closed-items.md#item-13-pyroscopeebpf-documented-debug-information-capability-is-not-implemented) (doc fix) |
| 14 | `pyroscope.java` | `thread` block does nothing when `frame` and `label_name` are unset | [Not applicable](closed-items.md#item-14-pyroscopejava-thread-block-silently-no-ops-when-both-frame-and-label_name-are-unset--not-applicable) (block not in the tree) |
| 15 | Shared `oauth2` block | `signature_algorithm` is validated under the wrong grant type | [Pre-merge finding](#3-pre-merge-review-findings), unmerged branch |
| 16 | Shared `oauth2` converter | `iss`, `audience` and `claims` are dropped | [Pre-merge finding](#3-pre-merge-review-findings), unmerged branch |

### New unvalidated findings

Found during the part 07 validation pass, after the numbered items above. They're recorded in [code-issues.md](code-issues.md)'s "New unvalidated issues" section, haven't been through the same review, and have no item numbers yet.

| Component | Issue | Severity |
|---|---|---|
| `prometheus.exporter.oracledb` | Embedded credentials aren't stripped correctly from `connection_string`. The connection URL is corrupted and a password fragment reaches the `instance` label. | [Medium](code-issues.md#issue-9-prometheusexporteroracledb-embedded-credentials-are-not-stripped-correctly-from-connection_string) |
| `prometheus.exporter.postgres` | `query_length` has no Alloy default, so `include_query` is expected to produce empty query text. | [Low](code-issues.md#issue-10-prometheusexporterpostgres-query_length-has-no-alloy-default-so-query-text-is-truncated-to-nothing) |
| `prometheus.exporter.postgres` | A single keyword/value DSN stops the component from starting, although two of them work. | [Medium](code-issues.md#issue-11-prometheusexporterpostgres-a-single-keywordvalue-dsn-stops-the-component-from-starting) |

All three were found by diffing the reference doc against source, and all three are source fixes rather than doc fixes.

---

## 3. Pre-merge review findings

Items 15 and 16 are not defects in shipped code. The JWT-bearer feature (`grant_type`, `signature_algorithm`, `iss`, `audience`, `claims`, client private key) is not in the current tree or on `main`. It lives on the branch `feat/http-oauth2-add-client-private-key` (tip `b43a715`, 2026-10-05, which matches the local ref). The findings below come from a separate check of that branch. The branch was not read here, so treat them as reported, not verified. They belong in a review of the open PR, not in a tracking issue. The PR number is unconfirmed: the branch's fetch history names 7130.

The shared `oauth2` block is used by many `prometheus.*`, `remote.*` and `discovery.*` pages, so its doc partial needs updating when the PR merges.

**Item 15: `signature_algorithm` is validated under the wrong grant type**
- `OAuth2Config.Validate()` switches on `GrantType`. The jwt-bearer case (`:481`) validates only the client certificate key pair. The client-credentials case (`:489`) validates the client secret pair and then checks `signature_algorithm` against `RS256`, `RS384` and `RS512` (`:496-498`).
- Upstream `prometheus/common` documents `SignatureAlgorithm` as used only with the jwt-bearer grant (`http_config.go:258-261`). So the check sits under the grant type that doesn't use the field and is missing from the one that does. A bad value passes silently under jwt-bearer, and a harmless one is rejected under client-credentials.
- Fix: move the check to the jwt-bearer case.

**Item 16: the converter drops `iss`, `audience` and `claims`**
- `toOAuth2` (`internal/converter/internal/common/http_client_config.go:78-92`) maps 12 fields. The branch's `OAuth2Config` declares `iss`, `audience` and `claims`, and upstream has them, but none is mapped. Converted Promtail and Prometheus configs lose them with no warning.
- The branch tip's own commit is "refactor: fix the promtail converter for http's oauth2 config" (2026-10-05), so the commit that touched this function did not close the gap.
- Fix: map all three.
- Check: the separate check cites upstream v0.70.1, while the current tree pins `prometheus/common` v0.71.0 (`go.mod`). The branch may pin a different version.

---

## 4. Docs to revisit if the source is fixed

| Item | Doc guidance |
|---|---|
| 2 | Doc left unchanged on purpose and accurate once fixed. Don't add a "no effect" note. Don't add a `mongos` caveat (that applies to `currentop_slow_time`). |
| 3 | The doc at HEAD describes a label, so keep describing it. The part-06 wording was not checked. |
| 4 | The `static` table at HEAD doesn't list the three attributes. Per the part-04 PR description, that branch documents them as having no effect (a note in `static` and an inheritance sentence in `metric`). That text was not read. Revert both if the source is fixed. |
| 8 | Part-04 (unmerged, head `c5dc82d`) tells users to set `server` to an address that includes a scheme. That is a workaround, since the exporter accepts the address. Revisit it if the source is fixed. |
| 9 | Leave the default at `15000`, the intended value. |
| 10 | Not documented, by choice. The health section already covers invalid configuration in general. |
| 12 | Updated to describe the current behaviour (working tree, uncommitted). Revisit if validation is added. |

---

## 5. Lower-confidence findings

Behaviours or open questions, not confirmed defects. Each needs a developer answer before it can be filed or documented.

| # | Component | Finding | Status | Source |
|---|---|---|---|---|
| L1 | `pyroscope.java` | `per_thread` does not apply to async-profiler JFR mode. korniltsev believes enabling it would break profiling (untested) and suggests removing or deprecating the flag. Tracked in [issue #5340]. The doc at HEAD says the option has no effect (`pyroscope.java.md:196-199`). Earlier notes mention a `thread` block replacement on a local branch; it is not in the current tree. | Open, tracked | [#7099] |
| L2 | `pyroscope.ebpf` | `pyroscope_ebpf_profiling_sessions_total` is incremented right after `controller.Start` succeeds, so it counts sessions started, not completed. The doc is not wrong: it already says "started". This is a metric-naming question only. | Open | [#7099] |
| L3 | `remote.vault` | `data` handling accepts `string` and `[]byte` values and silently ignores other types (`internal/component/remote/vault/vault.go:279-293`). Possibly intended. | Open | [#7097], backport [#7118] |
| L5 | `prometheus.exporter.azure` | `azure_cloud_environment` also accepts `ussec`, `azuresecret` and `azurepsecretcloud` in the vendored `webdevops/go-common` library, none of which are documented. These and the documented `azurepprivatecloud` need `AZURE_CLOUD_CONFIG` or `AZURE_CLOUD_CONFIG_FILE` to work. A developer should say whether these values are supported before they are documented. | Needs confirmation | [#7107], backport [#7267] |
| L7 | `pyroscope.write` | `pyroscope_ebpf_debug_info_upload_bytes_total` is emitted by `pyroscope.write` but carries an `ebpf` prefix. Per the code owner, the metric was meant for the ebpf component and later moved to `pyroscope.write`. He doesn't mind renaming it but wants the debug-info feature to stay undocumented. Low severity, and moot for docs. | Explained; rename optional | [#7099] |
| L8 | `prometheus.exporter.cloudwatch` | A reviewer (dehaansa) asked what the sentence about `length` and `period` request windows means. Part-04's head commit (`c5dc82d`) rewords it: with no `length`, each metric's `length` equals its `period`, so Alloy takes the maximum period as `length` and the minimum as `period`. The wording comes from `config.go` comments and was not checked against YACE. | Needs developer or YACE confirmation | [#7281] |

---

## 6. Intentionally undocumented surface

Not defects. Functionality that exists in code and was left out of the docs at the code owner's request.

**Reason (code owner, korniltsev-grafanista, in Slack):** the debug-info feature is highly experimental. It is mostly needed to dogfood server-side code, and both the Alloy side and the database side are expected to change significantly. It is deliberately undocumented so it can be removed or broken later without a compatibility commitment. There is no timeline for documenting it.

| Component | Withheld from the docs | Source |
|---|---|---|
| `pyroscope.ebpf` | The `debug_info` block and its arguments (`cache_size`, `on_target_symbolization`, `queue_size`, `strip_text_section`, `upload`, `worker_num`); debug metrics `pyroscope_ebpf_pprofs_dropped_total`, `pyroscope_ebpf_pprof_bytes_total`, `pyroscope_ebpf_pprof_samples_total`, `pyroscope_forwarded_entries_total`. | [#7099] |
| `pyroscope.write` | The `tracing` block (`jaeger_propagator`, `trace_context_propagator`), the `debug_info_upload_timeout` endpoint argument, and `pyroscope_ebpf_debug_info_upload_bytes_total`. | [#7099] |
| `pyroscope.receive_http` | `debug_info_upload_timeout`, the debug-info upload proxy endpoint (`POST /debuginfo.v1alpha1.DebuginfoService/Upload/{gnu_build_id}`) with its first-receiver-only forwarding, and metric `pyroscope_receive_http_debuginfo_downstream_calls_total`. | [#7099] |

- **`pyroscope.ebpf` `debug_info`:** history is #4948 (added), #5391 (removed, with its docs), #5891 (added back to the component, docs not restored). The docs were left out on purpose, so there is nothing to restore.
- **`pyroscope.write` `tracing`:** added in #4354. The code owner has only tested the Jaeger knob and expects a move from Jaeger to OpenTelemetry, which would add a new knob and deprecate the others.
- **Source comments:** the agreed convention is to mark intentionally undocumented items with inline comments in the source, not in the docs. The code owner referenced #7127 for these. Its merge status was not checked. One place to maintain, and a docs comment could mislead an agent reading an older doc version.
- **Open question:** what is the intended default for `strip_text_section`? The Go zero value `false` was used, since `NewDefaultArguments` does not set it.

---

## 7. PR index

| PR | Scope | Status | Backports | Items |
|---|---|---|---|---|
| [#7097] | Validate `remote.*` topics | Merged | [#7118] merged (v1.19) | L3 |
| [#7099] | Validate `pyroscope.*` topics | Merged Sep 16 | [#7124] merged (v1.19) | 6, 7, 13; L1, L2, L7; section 6 |
| [#7107] | `prometheus.*` part 01 | Merged | [#7267] merged (v1.20) | L5 |
| [#7111] | `prometheus.*` part 02 | Merged Sep 29 | [#7266] merged (v1.20) | 5 |
| [#7270] | `prometheus.*` part 03, second pass | Merged Oct 7 | [#7328] merged | 11, 12 |
| [#7281] | `prometheus.*` part 04 (consul, cloudwatch) | Open, head `c5dc82d` | Labelled `backport/v1.20` | 4, 8; L8 |
| [#7284] | `prometheus.*` part 05 | Merged Oct 7 | [#7332] merged | **9, 10 (merged without them)** |
| [#7335] | `prometheus.*` part 06 | Open, draft | None yet | 1, 2, 3 |
| [#7320] | Second pass, `pyroscope.*` | Merged Oct 7 | [#7331] merged | None (style only) |
| [#7321] | Second pass, `remote.*` | Merged | [#7330] merged | None |
| [#7119] | Fix `pyroscope.ebpf` samples counter | Merged (per author) | Unknown | Fixes 6 |
| [#7309] | Remove `prometheus.exporter.catchpoint` | Merged Oct 13 (per author) | Unknown | Fixes 5 |
| `feat/http-oauth2-add-client-private-key` | Shared `oauth2` block, JWT bearer | Open PR per a separate check; fetch history names 7130 (unverified) | None | 15, 16 |

---

## 8. Open questions and follow-ups

- **Items 9 and 10:** [#7284] merged without them. Both are written up in [code-issues.md](code-issues.md) and need a tracking issue or a follow-up PR.
- **#7335 description:** the draft's "Notes for reviewers" still describes a kafka panic, a 19-field mongodb options struct, and `connection_name` as log-only. Replacement text was drafted in conversation but not saved. Update it before moving the PR out of draft.
- **Items 15 and 16:** confirm the PR number and check which `prometheus/common` version the branch pins.
- **Backports:** was [#7119] backported (Item 6)? Is the [#7309] removal backported (Item 5)?
- **Tracking issues:** does an issue or fix PR already exist for Items 1, 2, 3, 4, 8 and 12, and for L1 to L3?
- **Doc edits to commit:** the `pyroscope.scrape.md` and `prometheus.echo.md` edits on `docs/correct-minor-errors-component-docs` were uncommitted when written. Commit them and open a PR.

---

## 9. Method and limits

- **Evidence:** PR descriptions and review threads, the `alloy` working tree on branch `docs/correct-minor-errors-component-docs` (cut from `main`), the published docs, and upstream sources where they were readable. Some earlier analysis was AI-generated, so each item was re-checked against the source one at a time.
- **What "checked" means:** each entry in [code-issues.md](code-issues.md) and [closed-items.md](closed-items.md) says what was read and what wasn't. Nothing was run, except the consul address parsing (scratch Go program, 2026-10-01) and the `remote.kubernetes.secret` example (`alloy validate`, exit 0).
- **Unmerged branches:** part-04, part-06 and the oauth2 branch were only partly readable. Each place says what was read.
- **"Open"** means no fix or tracking issue was seen. Some may already have one.

---

## Appendix: doc-side issues not yet fixed

None of these are source defects. Checked against the `alloy` working tree on 2026-10-13. The fixed rows are in [closed-items.md](closed-items.md#docs-only-fixes-from-the-overview-appendix).

Two open branches are not in that tree: part-04 ([#7281], consul and cloudwatch) and part-06 ([#7335]). Rows whose fix belongs on one of them are marked. For part-04, only the consul scheme wording and the head commit's cloudwatch `length` and `period` wording were read.

| Component | Issue | Resolution |
|---|---|---|
| `prometheus.exporter.cloudwatch` | `dimension_name_requirements` Default cell renders `{}` (map syntax) on a `list(string)` (`prometheus.exporter.cloudwatch.md:219`, `:324`). | Doc cell notation only. **Still unfixed at HEAD.** The fix belongs on part-04. Lowest priority. |
| `prometheus.exporter.cloudwatch` | The Usage section is a full example with a `discovery` block, not a minimal `"<LABEL>"` skeleton like every other validated exporter topic. | Structure, not source. Raised for a developer opinion. **Still the case at HEAD.** Belongs on part-04 if it changes. |
| `prometheus.scrape` | `scheme` defaults to `"http"` in source (`scrape.go:163`), but the doc Default cell is blank (`prometheus.scrape.md:82`). `body_size_limit` is `units.Base2Bytes` in source (`scrape.go:92`), accepting `104857600` and `"100MiB"`, but the doc says `int` (`prometheus.scrape.md:54`). | Doc-only fix. **Deferred** to the full audit of the `prometheus.scrape` topic. |
| Shared `oauth2` block | `client_id` and `token_url` are both documented as Required `no` (`shared/reference/components/oauth2-block.md`), but `OAuth2Config.Validate()` (`internal/component/common/config/types.go:432`) rejects a block that lacks `client_id`, lacks `token_url`, or has neither `client_secret` nor `client_secret_file`. The struct tags mark all of these `optional`. | **Needs a convention decision** on whether attributes enforced in `Validate()` are documented as required. Not checked. |

[grafana/alloy]: https://github.com/grafana/alloy
[issue #5340]: https://github.com/grafana/alloy/issues/5340
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

# Alloy component docs audit: code-side defect catalog

Compiled: 2026-10-09
Repo: [grafana/alloy]
Scope: `remote.*`, `pyroscope.*` and `prometheus.*` component reference validation (docs checked against component source code)

This catalog lists defects and open questions that the doc audits exposed in the **source code** and that were deferred to developers. It covers fixed, resolved and open items. Doc-wording fixes are excluded and listed in the appendix.

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

Docs impact: the validated docs describe real behaviour rather than advertising features that do not work. For kafka, the doc deliberately keeps `kafka_uris` as required so it does not expose the panic. For mssql, mongodb, cloudwatch (`static`) and consul, the doc states or works around the current behaviour and needs reverting if the source is fixed.

---

## 2. Confirmed code defects

Items 1 to 8 keep their original catalog numbering so earlier cross-references still resolve. Items 9 to 16 come from the agent session history and repo-memory deferral notes.

### Item 1: `prometheus.exporter.kafka`: panic when `kafka_uris` is omitted

- **Status:** Open
- **Type:** Crash
- **Source PR:** [#7335] (part 06, draft or open)
- **Cause:** `KafkaURIs` is tagged `alloy:"kafka_uris,attr,optional"`. In `customizeTarget`, when `len(a.KafkaURIs) > 1` the instance label comes from `a.Instance`; otherwise it uses `a.KafkaURIs[0]`. With length 0 that index is out of range. `Validate()` only guards the `len > 1` case.
- **Fix options:** make the tag required, or add a length check in `customizeTarget`.
- **Doc state:** the doc says Required: yes, which is the only thing preventing the panic today. Do not change it to optional.
- **User impact (author's reading):** a config that omits the argument crashes the component instead of producing a clear error.

### Item 2: `prometheus.exporter.mongodb`: `enable_profile` is a no-op

- **Status:** Open
- **Type:** Non-functional argument
- **Source PR:** [#7335]
- **Cause:** upstream `percona/mongodb_exporter@v0.47.2` (`exporter.go:227`) gates profiling on `e.opts.EnableProfile && nodeType != typeMongos && limitsOk && requestOpts.EnableProfile && e.opts.ProfileTimeTS != 0`. `ProfileTimeTS` is only set by the upstream CLI flag `collector.profile-time-ts` (`main.go:78`, `:196`). `exporter.New()` defaults only `Logger`. Alloy never sets it (`grep -rn 'ProfileTimeTS' internal/` returns nothing, and `mongodb_exporter.go:96` builds `exporter.Opts{}` with 19 fields, omitting it). The value is always 0, so the gate never passes.
- **Fix options:** expose a `profile_time_ts` argument, or set a non-zero default in `Convert()`.
- **Doc state:** deliberately unchanged; becomes correct once the source is fixed. Do not add a "currently has no effect" note, and do not add a `mongos` caveat to this argument — that caveat is correct for `currentop_slow_time`, whose own gate Alloy does satisfy.
- **User impact (author's reading):** users enable profiling and get no profiling metrics, with no warning.

### Item 3: `prometheus.exporter.mssql`: `connection_name` never produces a metric label

- **Status:** Open
- **Type:** Non-functional argument (two independent defects, both must be fixed)
- **Source PR:** [#7335]
- **Cause (a):** `internal/static/integrations/mssql/sql_exporter.go:137` passes `prometheus.Labels{}`, which is non-nil, so the `if constLabels == nil` branch at `target.go:62` never runs. `constLabelPairs` (`target.go:73-74`) stays empty, so `upDesc` and `scrapeDurationDesc` (`target.go:91-92`) get no constant labels.
- **Cause (b):** passing nil alone still fails. `config.TargetLabel` is an unassigned package var (`config/config.go:36`), set only by a flag in `cmd/sql_exporter/main.go:51` that Alloy never runs. The result would be `prometheus.Labels{"": tname}`, an invalid empty label name. Alloy calls `NewTarget` directly (`sql_exporter.go:129`), so the `job.go:39` path that sets `config.TargetLabel` is not reached.
- **Fix:** pass nil, and set `config.TargetLabel` before constructing the target.
- **Doc state:** corrected to describe log-message behaviour, which is all `connection_name` does today (`target.go:61`). If the source is fixed, the description reverts to a label — and that label lands on **both** `up` and `scrape_duration_seconds`, not just uptime.
- **User impact (author's reading):** users cannot tell SQL Server connections apart in metrics.

### Item 4: `prometheus.exporter.cloudwatch`: `static` block silently drops `period`, `length`, `delay`

- **Status:** Open
- **Type:** Silently ignored arguments
- **Source PR:** [#7281] (open)
- **Cause:** `StaticJob` declares all three as optional attributes ([internal/component/prometheus/exporter/cloudwatch/config.go][cloudwatch-config.go] L86-88), so a config setting them parses and runs with no warning. The conversion discards them: `toYACEMetrics(sj.Metrics, 0, 0)` at L330 hardcodes zeros, where discovery (L355) and custom_namespace (L381) pass the job values through. Root cause is that upstream `yaceConf.Static` has no `JobLevelMetricFields`.
- **Precedent:** `StaticJob.NilToZero` hit the same problem and is patched in `toYACEStaticJob`. The in-code comment at config.go L89-93 reasons that this should either be removed from Alloy in a major release or contributed to YACE, and that it is patched in the static-job function to avoid breaking existing configs. The same argument applies to these three fields. Commit `e729082c1b` (2026-01-26) added `StaticJob.Period`/`.Length` and the zero-passing call site in the same change.
- **Doc state:** documented in two places: the `static` section's no-effect note at cloudwatch.md L419-421, and the inheritance sentence in the `metric` section. Both need reverting if the source is fixed.
- **User impact (author's reading):** the config parses cleanly and runs, but the user's timing settings are ignored.

### Item 5: `prometheus.exporter.catchpoint`: non-functional component, removed

- **Status:** Resolved by removal in [#7309]. Approved by kalleep and clayton-cornell on Oct 8; **merge not confirmed**. Confirm before presenting.
- **Type:** Non-functional component
- **Source PRs:** audit finding in [#7111] (part 02) and backport [#7266]
- **Cause (audit finding):** `port` and `webhook_path` are copied into the upstream `collector.Config`, but the collector package never reads either field (only struct declarations and defaults exist). The listener is started by the upstream binary (`cmd/catchpoint-exporter/main.go:55-62` calls `http.HandleFunc(*webhookPath, collector.HandleWebhook)` and `ListenAndServe`). Alloy imports only `collector`, never `cmd`, and `HandleWebhook` has zero references in the Alloy repo. Alloy's integration passes only `WithLogger` and `WithCollectors` ([internal/static/integrations/catchpoint_exporter/catchpoint_exporter.go][catchpoint_exporter.go] L64-65), so no runner is installed and `Run()` falls back to a no-op that blocks on `ctx.Done()`. `port` is used only locally as the instance key — `InstanceKey()` returns `c.Port`, so that one argument does do something.
- **Secondary discrepancy (now moot):** upstream `NewConfig()` defaults `webhook_path` to `/webhook` while Alloy's `DefaultArguments` used `/catchpoint-webhook` (`collector/config.go:27` vs `catchpoint.go:29`).
- **Resolution (from #7309):** testing found the component "did not function, and hasn't since its addition". It had zero open issues or PRs and no usage in anonymous usage stats, so it was removed rather than fixed. The PR deletes the component, the static `catchpoint_exporter` integration, the reference page (with a redirect), and the `github.com/grafana/catchpoint-prometheus-exporter` dependency. The component was experimental, so removal is outside backward-compatibility guarantees.
- **Attribution caveat:** #7309 does not mention the audit. The audit finding (Sep 29) predates the removal PR (Oct 6), but a causal link is not shown.
- **Doc state:** superseded by removal. Before that, the doc redescribed `port` as setting the `instance` label and `webhook_path` as having no effect, with a caution admonition.

### Item 6: `pyroscope.ebpf`: `pyroscope_ebpf_pprof_samples_total` counts bytes

- **Status:** Fixed by [#7119] (merged, confirmed by author)
- **Type:** Wrong metric
- **Source PR:** [#7099] (merged), backport [#7124] (merged to `release/v1.19`)
- **Cause:** in [send.go][send.go], both `pprofSamplesTotal` (L31, `len(p.Raw)`) and `pprofBytesTotal` (L36, `len(rawProfile)`) were incremented from the same byte slice, making the samples counter a duplicate of the bytes counter rather than merely inaccurate. The Help string in [metrics.go][metrics.go] was a stale copy-paste ("Total number of pprof profiles collected...").
- **Fix:** #7119 records the number of `pprof.Profile.Sample` entries with each generated profile and uses it for the samples counter. The bytes counter keeps counting raw profile bytes. Help text and reference docs corrected. Regression tests cover the counters independently.
- **Verified 2026-10-09:** `pyroscope.ebpf.md` line 150 now reads "Total number of samples in pprof profiles collected by the eBPF component, per `service_name`." The doc describes sample counting.
- **Open follow-up — conflict with section 4:** on 2026-09-16 the code owner had `pprof_bytes_total`, `pprof_samples_total`, `pprofs_dropped_total` and `pyroscope_forwarded_entries_total` **removed** from the docs as part of the deliberately-undocumented debug-info surface. #7119 re-added two of the four; `pprofs_dropped_total` and `pyroscope_forwarded_entries_total` are still absent. Confirm the re-add was intended.
- **Open follow-up:** whether #7119 was backported to a release branch is unknown.
- **User impact (author's reading):** dashboards and alerts built on the samples metric showed byte counts.

### Item 7: `pyroscope.scrape`: default `scrape_timeout` is shorter than the default CPU profile duration

- **Status:** Open
- **Type:** Bad default
- **Source PR:** [#7099] (Copilot review thread on the args table; korniltsev-grafanista commented "this looks like a legit issue")
- **Cause (Copilot's analysis, not independently verified):** the default `scrape_timeout` is `10s`. `ProcessCPU` delta profiling is enabled by default and the default delta duration is `scrape_interval - 1` (`14s`). The scrape loop applies `ScrapeTimeout` as the request context deadline, so an unconfigured component times out every default CPU profile request.
- **Corroboration from the audit:** the `10s` default is confirmed — the doc wrongly claimed `"18s"` and was corrected to `"10s"`, and a fabricated "Must be larger than `scrape_interval`" constraint was removed at the same time. The 14s delta-duration half of the trace has no independent confirmation.
- **Fix options:** change the source defaults, or choose and document a timeout that accommodates the 14-second request.
- **User impact (author's reading):** a default-configured scrape of CPU profiles would time out.

### Item 8: `prometheus.exporter.consul`: scheme-less server address labels every target `instance="unknown"`

- **Status:** Open
- **Type:** Wrong output
- **Source PR:** [#7281] (Copilot review; the doc statement was then simplified in commit "Simplify a statement to avoid documenting a bug")
- **Cause:** [internal/static/integrations/consul_exporter/consul_exporter.go][consul_exporter.go] L59-65 parses `server` directly and returns `u.Host`. Go reads `consul.example.com:8500` as Scheme=`consul.example.com`, Opaque=`8500`, Host=`""`.
- **Correction to the earlier catalog wording:** the label is not left empty. The empty key hits [internal/component/prometheus/exporter/exporter.go][exporter.go] L93, `if instanceKey == "" { instanceKey = "unknown" }` — a line whose own comment says "in case of a bug". Every target is therefore labelled `instance="unknown"`. Verified empirically 2026-10-01 with a scratch Go program, for `consul.example.com:8500`, `localhost:8500` and a bare hostname.
- **Correction to the earlier fix options:** "document that the scheme is required" is not a valid option, because it is false. Upstream normalises scheme-less input (`consul_exporter@v0.8.0/pkg/exporter/consul_exporter.go` L132-141, `if !strings.Contains(uri, "://") { uri = "http://" + uri }`) but only on a local variable, so `c.Server` is never mutated and connections succeed. Only the instance key breaks.
- **Fix:** apply the same `strings.Contains(uri, "://")` normalisation before deriving the instance key.
- **Doc state:** a workaround shipped on part-04 — consul.md now says to set `server` to an address that includes a scheme. If the source is fixed, the doc can go back to describing the scheme as optional.
- **User impact (author's reading):** metrics carry a useless `instance` label, which breaks per-server grouping and alerting.

### Item 9: `prometheus.exporter.github`: `github_rate_limit` has no Alloy default, so GitHub App re-auth never fires

- **Status:** Open. **Missed its intended PR** — recorded 2026-10-01 to be raised at part-05 PR creation; [#7284] merged Oct 7 without it.
- **Type:** Missing default
- **Source branch:** `docs/validate-prometheus-component-docs-part-05`
- **Cause:** [github.go][github.go] `DefaultArguments` is `Arguments{ APIURL: github_exporter.DefaultConfig.APIURL }` — it pulls `APIURL` from `DefaultConfig` but not `GitHubRateLimit`, and `Convert()` passes `a.GitHubRateLimit` straight through. The static YAML path gets `15000` via `UnmarshalYAML` (`*c = DefaultConfig` in [github_exporter.go][github_exporter.go]); the Alloy path gets the float64 zero value.
- **Consequence:** traced in `githubexporter/github-exporter@v1.3.1`, `exporter/prometheus.go` L26-37 `Collect()` → `if e.Config.GitHubApp()` → `isTokenExpired()` → L87-90 `if limit < e.Config.GitHubRateLimit()`. With 0, `limit < 0` is never true, so `SetAPITokenFromGitHubApp()` never runs.
- **Re-verified 2026-10-09** against the current tree: `DefaultArguments` still sets only `APIURL`.
- **Fix options:** add `GitHubRateLimit` to `DefaultArguments` (preferred), or correct the doc to `0`.
- **Doc state:** the doc claims default `15000`, which is wrong for Alloy. The description "Threshold for GitHub App rate limit to trigger re-authentication" is accurate and needs no change.
- **User impact (author's reading):** GitHub App credentials silently stop refreshing unless the user sets the value explicitly.

### Item 10: `prometheus.exporter.github`: partial GitHub App configuration is silently ignored

- **Status:** Open. Raised 2026-10-01, then dropped by the author's call; never filed and never documented. Same missed PR as item 9.
- **Type:** Silently ignored config
- **Source branch:** `docs/validate-prometheus-component-docs-part-05`
- **Cause:** the GitHub App auth guard in `New()` ([github_exporter.go][github_exporter.go]) requires all three of `github_app_id`, `github_app_installation_id` and `github_app_key_path`. A config that sets only one or two falls through the conjunction quietly instead of erroring, and the component starts unauthenticated. Exact line numbers were not recorded.
- **Fix options:** reject a partial set in `Validate()`, or log a warning.
- **Doc state:** not documented. Documenting it was considered and rejected, because the health section already covers the general case and the specific case is silent misconfiguration rather than an error state.
- **User impact (author's reading):** a typo'd or half-finished GitHub App block looks accepted and silently degrades to the unauthenticated rate limit.
- **Confidence:** medium. The guard shape was read from source; the exact lines were not recorded.

### Item 11: `prometheus.exporter.cadvisor`: `allowlisted_container_labels` default is `[""]`, not `[]`

- **Status:** Open
- **Type:** Bad default, or a doc/source mismatch — needs a developer decision on which
- **Source PR:** [#7270] (part 03)
- **Cause:** `SetToDefault` sets `[]string{""}` at cadvisor.go L58, reinforced by a guard at L81-82. The doc documents `[]`.
- **Open question:** is the doc wrong, or is `[""]` an implementation detail that should not surface to users? Settled separately and not in dispute: `[]` **is** the correct rendering for a nil optional `list(string)` — the precedent is cadvisor's own `enabled_metrics`. Only the `[""]` case is genuinely open.
- **Not to be confused with** the `disabled_metrics` default, which was a doc-only issue and is resolved — see the appendix.
- **User impact (author's reading):** unclear without the developer answer; at minimum the documented default does not match the code.

### Item 12: `prometheus.echo`: `format` is never validated, so the component can never report unhealthy

- **Status:** Open
- **Type:** Missing validation
- **Source PR:** [#7270] (part 03)
- **Cause:** `Component.Update()` never validates `Format` and never returns a non-nil error. An unrecognised `format` value falls through to a logged warning and a `text` default. `New()` only fails if `Update()` fails, so the component has no path to an unhealthy state.
- **Fix options:** validate the enum in `Validate()` or `Update()` and return an error, or accept the fall-through as intended.
- **Doc state:** handled as a doc fix — the standard "only reported as unhealthy if given an invalid configuration" boilerplate was false on this page and was corrected. The source side was never raised with developers.
- **User impact (author's reading):** a misspelled `format` produces `text` output and a log line, with no health signal.

### Item 13: `pyroscope.ebpf`: documented debug information capability is not implemented

- **Status:** Open. Needs a maintainer decision (code or docs).
- **Type:** Missing implementation
- **Source PR:** [#7099]
- **Cause:** the `## Debug information` section describes a `DebugInfo()`-style capability. The component implements no `DebugInfo()` at all.
- **Fix options:** implement `DebugInfo()` to match the documented behaviour, or replace the section with the standard "doesn't expose any component-specific debug information" boilerplate.
- **Doc state:** deliberately left untouched in #7099 pending the decision. The equivalent gap on `pyroscope.receive_http` and `pyroscope.relabel` — both missing the section entirely — was fixed with the boilerplate, after confirming neither implements `DebugInfo()` in source.
- **User impact (author's reading):** readers look for debug output that does not exist.

### Item 14: `pyroscope.java`: `thread` block silently no-ops when both `frame` and `label_name` are unset

- **Status:** Open; outcome unknown
- **Type:** Silently ignored config
- **Source branch:** `threads_fix`, reviewed 2026-08-10 (pre-dates the audit; no PR number recorded)
- **Cause:** `loop.go` treats the both-unset case as a no-op. The block is accepted and does nothing, with no error or warning.
- **Fix options:** reject the combination in `Validate()`, or document "at least one of `frame` or `label_name` must be set for the block to have any effect". A doc note was proposed at review time; whether that or a source fix landed is unknown.
- **Distinct from L1**, which concerns `per_thread` in JFR mode.
- **User impact (author's reading):** a `thread` block that looks configured produces no per-thread data.

### Item 15: `oauth2` block: `signature_algorithm` is validated under the wrong grant type

- **Status:** Open
- **Type:** Validation under the wrong condition
- **Source branch:** `feat/http-oauth2-add-client-private-key`, reviewed 2026-10-08 (no PR number recorded)
- **Scope note:** this is the shared `oauth2` block partial, used by `prometheus.*` and `remote.*` component pages, so it is in scope for the audit even though it lives in `common/config`.
- **Cause:** [internal/component/common/config/types.go][types.go] L489-498 places the RS256/RS384/RS512 check under `case grantTypeClientCredentials`. Upstream validates it under jwt-bearer (`prometheus/common` `http_config.go:444-450`). Invalid algorithms are therefore silently accepted for the grant type that actually uses them.
- **Confirmed reachable:** `OAuth2Config.Validate()` is called by the syntax decoder via `syntax.Validator` (`syntax/internal/value/decode.go:105-108`, `syntax/vm/vm.go:99`). It is not dead code. `HTTPClientConfig.Validate()` does not call it.
- **Fix:** move the check to the jwt-bearer branch to match upstream.
- **User impact (author's reading):** a bad signature algorithm is accepted at load time and fails later, or silently misbehaves.

### Item 16: `oauth2` converter drops `Iss`, `Audience` and `Claims`

- **Status:** Open
- **Type:** Silent data loss in the converter
- **Source branch:** `feat/http-oauth2-add-client-private-key`, reviewed 2026-10-08 (no PR number recorded)
- **Cause:** `toOAuth2` in [internal/converter/internal/common/http_client_config.go][http_client_config.go] omits the three fields when building the Alloy config.
- **Fix:** carry all three through the conversion.
- **User impact (author's reading):** a converted static or Prometheus config loses JWT-bearer claims with no warning, and authentication changes behaviour after migration.

---

## 3. Lower-confidence findings and open questions

These are behaviours or open questions, not confirmed defects. Each needs a developer answer before it can be filed or documented.

| # | Component | Finding | Status | Source |
|---|---|---|---|---|
| L1 | `pyroscope.java` | `per_thread` does not apply to async-profiler JFR mode; korniltsev believes enabling it would break profiling (untested) and suggests removing or deprecating the flag. Tracked in [issue #5340]. A replacement already exists: the `threads_fix` branch adds a `thread` block (`frame`, `label_name`, `regex`) under `profiling_config` and removes `tlab`, and the doc now points from the `per_thread` admonition to it. | Open, tracked | [#7099] |
| L2 | `pyroscope.ebpf` | `pyroscope_ebpf_profiling_sessions_total` is incremented right after `controller.Start` succeeds, so it counts sessions started, not completed. Same family of metric-semantics mismatch as item 6. **The doc is not wrong** — it already reads "Number of profiling sessions started by the eBPF component" (verified 2026-10-09), so this is a metric-naming question only. | Open | [#7099] |
| L3 | `remote.vault` | `data` handling accepts `string` and `[]byte` values and silently ignores other types (`internal/component/remote/vault/vault.go:279-293`). Possibly intended. | Open | [#7097], backport [#7118] |
| L5 | `prometheus.exporter.azure` | `azure_cloud_environment` also accepts `ussec`, `azuresecret` and `azurepsecretcloud` in the vendored `webdevops/go-common` cloudconfig library (`cloudconfig.NewCloudConfig()`), none of which are documented. These and the documented `azurepprivatecloud` need `AZURE_CLOUD_CONFIG` / `AZURE_CLOUD_CONFIG_FILE` env vars to work. Needs a developer answer on whether these values are supported before documenting them. | Needs confirmation | [#7107], backport [#7267] |
| L7 | `pyroscope.write` | `pyroscope_ebpf_debug_info_upload_bytes_total` is emitted by `pyroscope.write` but carries an `ebpf` prefix. Introduced in PR [#4948] alongside the ebpf `debug_info` block, and named for the feature rather than the emitting component. Git history shows no earlier or parallel copy in the `ebpf` package, so an initial "copy-paste bug" characterisation was explicitly withdrawn. Low severity, and currently moot for docs since the metric is undocumented. | Open naming question | [#7099] |
| L8 | `prometheus.exporter.cloudwatch` | A reviewer (dehaansa) asked what the sentence about `length` and `period` request windows means. The author reworked it from `config.go` comments but could not validate the behaviour inside YACE requests. | Needs developer or YACE confirmation | [#7281] |

---

## 4. Intentionally undocumented surface

Not defects. Functionality that exists in code and was deliberately removed from the docs at the code owner's request, with no stated condition for when it becomes documentable. Recorded here so the gap is traceable rather than mistaken for a completeness failure in a later review.

| Component | Withheld from the docs | Source |
|---|---|---|
| `pyroscope.ebpf` | The `debug_info` block and its arguments (`cache_size`, `on_target_symbolization`, `queue_size`, `strip_text_section`, `upload`, `worker_num`); debug metrics `pyroscope_ebpf_pprofs_dropped_total`, `pyroscope_ebpf_pprof_bytes_total`, `pyroscope_ebpf_pprof_samples_total`, `pyroscope_forwarded_entries_total`. The Blocks section was restored to "doesn't support any blocks." | [#7099] |
| `pyroscope.write` | The `tracing` block (`jaeger_propagator`, `trace_context_propagator`), the `debug_info_upload_timeout` endpoint argument, and `pyroscope_ebpf_debug_info_upload_bytes_total`. | [#7099] |
| `pyroscope.receive_http` | `debug_info_upload_timeout`, the debug-info upload proxy endpoint (`POST /debuginfo.v1alpha1.DebuginfoService/Upload/{gnu_build_id}`) with its first-receiver-only forwarding behaviour, and metric `pyroscope_receive_http_debuginfo_downstream_calls_total`. | [#7099] |

**This list is now partially stale.** As of 2026-10-09, `pyroscope.ebpf.md` documents `pyroscope_ebpf_pprof_bytes_total` and `pyroscope_ebpf_pprof_samples_total` again — re-added by [#7119] when it fixed item 6. `pprofs_dropped_total` and `pyroscope_forwarded_entries_total` are still absent. Confirm with the code owner whether the re-add was intended.

Two sub-questions from the same review were never answered:

- What is the intended default for `strip_text_section`? The Go zero value `false` was used, since `NewDefaultArguments` does not set it.
- Is `debug_info` meant to be user-facing at all, or was it deliberately left out of the re-add PR?

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
| [#7309]                                   | Remove `prometheus.exporter.catchpoint`            | Open, approved Oct 8          | Unknown                   | Resolves item 5                       |
| `feat/http-oauth2-add-client-private-key` | oauth2 block partial review, 2026-10-08            | Branch; no PR number recorded | —                         | Items 15, 16                          |
| `threads_fix`                             | `pyroscope.java` `thread` block review, 2026-08-10 | Branch; no PR number recorded | —                         | Item 14                               |

---

## 6. Verification checklist

Open questions that should be settled before this catalog is presented.

- **Items 9 and 10 have no home.** [#7284] merged Oct 7 without them. They need a tracking issue or a follow-up PR.
- **#7309 (catchpoint removal):** has it merged, and on what date?
- **#7119:** backported to any release branch?
- **Section 4 staleness:** was re-adding `pprof_bytes_total` and `pprof_samples_total` to `pyroscope.ebpf.md` in #7119 intended, given #7099 removed them at the code owner's request?
- **Item 7:** does the source behave as Copilot described (10s timeout against a 14s default CPU delta)? The 10s default is confirmed; the 14s half is not independently verified.
- **Item 10:** exact line numbers for the GitHub App auth guard were never recorded. Re-read before filing.
- **Item 12:** is the missing `format` validation worth fixing, or is the fall-through intended?
- **Item 14:** did a doc note or a source fix land on the `threads_fix` branch?
- **Items 15 and 16:** no PR number was recorded for `feat/http-oauth2-add-client-private-key`. Find it before filing.
- **Items 1, 2, 3, 4, 8, 11, 13 and L1 to L3:** does a tracking issue or fix PR already exist for each?
- **Total number of components audited**, for any defects-per-component rate. Not known.

Closed during this pass, 2026-10-09:

- `remote.vault` `AWS_SESSION` versus `AWS_SESSION_TOKEN` — resolved. See the appendix.
- "Does `pyroscope.ebpf.md` on `main` describe sample counting?" — yes, line 150.
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

Resolved or doc-side issues the review turned up. Kept for traceability; none require developer action.

| Component | Issue | Resolution |
|---|---|---|
| `prometheus.exporter.cadvisor` | `disabled_metrics` documented `[]`, but when the argument is omitted the integration subtracts a built-in disabled set from `AllMetrics`, so the effective default is not empty. Previously tracked as L6. | Doc fix on part 02. The Default cell reads `_see below_`, matching `prometheus.exporter.unix`, `.windows` and `.oracledb`. It was briefly changed to `[]`, caught as a regression, and restored. Not a code defect — do not confuse with item 11. |
| `remote.vault` | `auth.azure` `resource_url` and `auth.kubernetes` `service_account_file` defaults were missing from their tables. | Doc fix. Values read directly from [auth.go][auth.go]: `DefaultAuthAzure.ResourceURL = "https://management.azure.com/"` and `AuthKubernetes.ServiceAccountTokenFile = "/var/run/secrets/kubernetes.io/serviceaccount/token"`. Correct as written; only reviewer sign-off is outstanding. |
| `remote.vault` | The doc named `AWS_SESSION`; the AWS SDK uses `AWS_SESSION_TOKEN`. Previously tracked as L4. | Resolved. Verified 2026-10-09: remote.vault.md line 109 reads `AWS_SESSION_TOKEN`. [auth.go][auth.go] contains no `AWS_` environment reads at all — it delegates to `hashicorp/vault/api/auth/aws`, which uses the SDK credential chain. The vendored SDK was not traced. |
| `remote.kubernetes.secret` | The example wrapped a ConfigMap value in `convert.nonsensitive()` that was never secret. | Doc fix. The example was restructured so the Secret holds both `username` and `password`, and `convert.nonsensitive` is demonstrated on `username` where it is genuinely needed. Validated with `alloy validate`, exit 0. |
| `prometheus.exporter.cloudwatch` | `dimension_name_requirements` Default cell renders `{}` (map syntax) on a `list(string)`. | Doc cell notation only. Unfixed; lowest priority. |
| `prometheus.exporter.cloudwatch` | The Usage section is not a minimal `"<LABEL>"` skeleton, unlike every other validated exporter topic. | Structure, not source. Raised for a developer opinion but carries no code change. |
| `pyroscope.scrape` | `scrape_timeout` default documented as `"18s"`, and a "Must be larger than `scrape_interval`" constraint that does not exist in source. | Doc fix. Corrected to `"10s"` and the fabricated constraint removed. This is the corroboration behind item 7. |
| `prometheus.enrich` | Debug metrics table named `prometheus_target_cache_size`; the registered metric is `alloy_prometheus_target_cache_size` (`enrich.go:153`). `prometheus_fanout_latency` and `prometheus_forwarded_samples_total` are correct — they come from the shared `Fanout` type and carry no `alloy_` prefix. | Doc fix. |
| `prometheus.scrape` | `scheme` default is `"http"` in source but documented as empty; `body_size_limit` typed `int` in the doc versus `units.Base2Bytes` in source, which accepts both `104857600` and `"100MiB"`. | Doc drift found in a pre-audit stress-test session. No record of a fix. |
| `oauth2` block | `client_id` Required documented as `no`; `Validate()` enforces it identically to `token_url`. | Doc cell. The code behaves correctly; only the table is wrong. |
| `pyroscope.java` | On the `threads_fix` branch, the `otel.scope.name` and `otel.scope.version` auto-injected labels table was deleted while the code behaviour was unchanged. | Doc regression flagged for restoration before merge. Outcome unknown; likely moot. |

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

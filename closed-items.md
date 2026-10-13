# Alloy component docs audit: closed and fixed items

Compiled: 2026-10-13
Repo: [grafana/alloy]
Companion to: [overview.md](overview.md), the code-side defect catalog of open items and open questions.

This file indexes items from the audit that are **fixed or closed** and need no further developer action. Each entry keeps the full evidence from the original catalog entry, so an item can be reopened or cited without going back to the overview. Original item numbers are kept so earlier cross-references still resolve.

An item moves here when its fix has merged, or when it turned out to need no source change and the doc fix is done. Where a fix exists but is not yet merged, the status says so.

**When an item moves here, leave a one-line pointer in [overview.md](overview.md)** at the item's original position: `**Item N:** [Fixed](closed-items.md#anchor)`. Nothing else on the line. The word "Fixed" is the link to the entry below (use the anchor shown in the Index table), and all details, including any caveat such as a PR that has not merged yet, go in the entry here.

---

## Index

| Item | Component | Issue | Final type | Resolution | PR or branch | Status | Remaining follow-up |
|---|---|---|---|---|---|---|---|
| [5](#item-5-prometheusexportercatchpoint-non-functional-component-removed) | `prometheus.exporter.catchpoint` | Component did not function: the webhook listener was never started | Non-functional component (source defect) | Component removed | [#7309] (removal); audit finding in [#7111], backport [#7266] | Closed. Merged 2026-10-13 (reported by the author; not independently checked). | Whether the removal is backported to a release branch is unknown. |
| [6](#item-6-pyroscopeebpf-pyroscope_ebpf_pprof_samples_total-counts-bytes) | `pyroscope.ebpf` | `pyroscope_ebpf_pprof_samples_total` counted bytes, not samples | Wrong metric (source defect) | Source fix | [#7119] (fix); [#7099] (found in); [#7124] (backport of #7099 to `release/v1.19`) | Closed. Merged, confirmed by author. | Whether #7119 was backported to a release branch is unknown. |
| [7](#item-7-pyroscopescrape-default-scrape_timeout-shorter-than-the-default-cpu-profile-duration--not-a-bug) | `pyroscope.scrape` | Default `scrape_timeout` (10s) is shorter than the default CPU profile (14s) | Not a bug | None needed | n/a | Closed. Checked by reading source; not run. | Optional doc note on the effective timeout (tracked in the overview appendix). |
| [11](#item-11-prometheusexportercadvisor-allowlisted_container_labels-default--not-a-bug) | `prometheus.exporter.cadvisor` | `allowlisted_container_labels` is `[""]` in code but `[]` in the doc | Not a bug | None needed | n/a | Closed. Checked by reading source; not run. | None. |
| [13](#item-13-pyroscopeebpf-documented-debug-information-capability-is-not-implemented) | `pyroscope.ebpf` | `## Debug information` section documented output the component cannot produce | Doc error (originally logged as Missing implementation) | Doc fix | Alloy branch `docs/correct-minor-errors-component-docs`; origin [#7099] | Fixed and committed on the branch. **PR and merge not confirmed.** | Optional: find out who added the `targets` bullet (see entry). |
| [14](#item-14-pyroscopejava-thread-block-silently-no-ops-when-both-frame-and-label_name-are-unset--not-applicable) | `pyroscope.java` | A `thread` block does nothing when `frame` and `label_name` are both unset | Not applicable | None needed | n/a | Closed. The block is not in the current tree. | Reopen if a `thread` block lands. |

### Not moved here, and why

- **Appendix rows that are still unresolved** stay in the appendix of [overview.md](overview.md). Resolved appendix rows are in [Docs-only fixes](#docs-only-fixes-from-the-overview-appendix) below.

---

## Items

### Item 5: `prometheus.exporter.catchpoint`: non-functional component, removed

- **Status:** Resolved by removal in [#7309]. Approved by kalleep and clayton-cornell on Oct 8. **Merged 2026-10-13** (reported by the author; I did not check the PR page). Whether the removal was backported is unknown.
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
- **Open follow-up:** whether #7119 was backported to a release branch is unknown.
- **User impact (author's reading):** dashboards and alerts built on the samples metric showed byte counts.

### Item 7: `pyroscope.scrape`: default `scrape_timeout` shorter than the default CPU profile duration — not a bug

- **Concern:** the default `scrape_timeout` is 10s, but the default CPU delta profile takes 14s, so a default configuration would time out on every CPU scrape.
- **Verdict:** not a bug. The scrape loop extends the timeout for any target that has a `seconds` parameter, so the default effective timeout is 24s.
- **Evidence (source, checked 2026-10-13, all under `internal/component/pyroscope/scrape/`):**
  - Defaults: `scrape_interval` 15s (`scrape.go:202`), `scrape_timeout` 10s (`:203`), delta profiling duration 14s (`:35`, `:205`). The CPU target is enabled with `Delta: true` (`:152-156`).
  - Delta targets get a `seconds` query parameter: `scrape_interval - 1s`, or `delta_profiling_duration` if it is not the default (`target.go:362-367`).
  - `newScrapeLoop` adds `scrape_interval - 1s` to the timeout when the target has a `seconds` parameter (`scrape_loop.go:167-169`). The request context uses the extended value (`:218`). With defaults: 10s + 14s = 24s for a 14s profile.
  - A non-default `delta_profiling_duration` is capped at `scrape_interval - 1s` by validation (`scrape.go:227-233`), so the extension is always at least as long as the profile.
- **Checked:** by reading the source. Not run; a live scrape with default settings would confirm it.
- **Doc gap (optional):** the `scrape_timeout` description does not say the timeout is extended for delta profiles. Tracked in the overview appendix.

### Item 11: `prometheus.exporter.cadvisor`: `allowlisted_container_labels` default — not a bug

- **Concern:** the code default for `allowlisted_container_labels` is `[""]`, but the doc shows `[]`.
- **Verdict:** not a bug, and the doc is right. `Convert()` replaces an empty list with `[""]` before handing it to cAdvisor, so `[]` and `[""]` behave the same. The `[""]` is an internal detail for upstream compatibility.
- **Evidence (source, checked 2026-10-13, `internal/component/prometheus/exporter/cadvisor/cadvisor.go`):**
  - `SetToDefault` sets `AllowlistedContainerLabels: []string{""}` (`:58`).
  - `Convert()` sets `[""]` whenever the list is empty (`:81-83`), so a user value of `[]` produces the same upstream configuration as the default.
  - The sibling arguments `env_metadata_allowlist` and `raw_cgroup_prefix_allowlist` follow the same pattern (`:59-60`, `:84-89`), and the doc shows `[]` for all three (`prometheus.exporter.cadvisor.md:129`, `:140`, `:142`).
- **Checked:** by reading the source. Not run. How cAdvisor itself treats `[""]` was not checked, since both forms reach it identically.
- **Doc:** no change needed.

### Item 13: `pyroscope.ebpf`: documented debug information capability is not implemented

- **Status:** **Fixed 2026-10-13, committed by the author** on alloy branch `docs/correct-minor-errors-component-docs`. PR and merge not confirmed. The `## Debug information` section in `pyroscope.ebpf.md` now reads "`pyroscope.ebpf` doesn't expose any component-specific debug information." **Validated: this is a doc bug, not a source bug.** Implementing `DebugInfo()` is the only source-side alternative and nothing suggests it is wanted. No developer action needed unless maintainers want the feature.
- **Validity:** Valid. The section documented debug output the component cannot produce.
- **Type:** was Missing implementation. Reclassified as a doc error.
- **Source PR:** [#7099]
- **Cause:** the `## Debug information` section listed `elf_cache`, `pid_cache` and `targets` as debug output. The component implements no `DebugInfo()`, so none of these is ever shown.
- **Evidence (source, validated 2026-10-13):**
  - `component.DebugComponent` requires `DebugInfo() any` (`internal/component/component.go:103-114`). A component without that method exposes no debug info.
  - No `DebugInfo` method exists in any file of the `internal/component/pyroscope/ebpf` package: `ebpf_linux.go` (the real `Component`), `ebpf_placeholder.go` (the non-Linux stub), `args.go`, `pool.go`, `metrics.go` and `send.go` were all searched. The sub-packages (`reporter`, `symb`, `discovery`) were **not** searched, but `Component` is defined in `ebpf_linux.go`, so a `DebugInfo` method on it would have to be in the package's top-level files.
  - `elf_cache` and `pid_cache` have no references in the package. The only related symbol is `pid_cache_size` in `args.go:51`, which the doc itself marks Deprecated (no-op).
  - `targets` is not debug info. The only thing tracking active targets is the gauge `pyroscope_ebpf_active_targets` (`ebpf_linux.go:233`, `c.metrics.targetsActive.Set(...)`), which is already in the Debug metrics table.
- **Provenance (published docs, checked 2026-10-13):** the `elf_cache` / `pid_cache` bullets are legacy. They appear in the Grafana Agent Flow reference for `pyroscope.ebpf` and carried over into the Alloy docs, from an older implementation. The published Alloy `latest` page lists only those two bullets. The local branch had a third, `targets`, so that bullet was added after the published version. It reads like a conflation with the `pyroscope_ebpf_active_targets` metric.
- **Fix applied:** replaced the section with the standard "`pyroscope.ebpf` doesn't expose any component-specific debug information." boilerplate, as used on `pyroscope.write` and, after this audit, `pyroscope.receive_http` and `pyroscope.relabel`. The alternative, implementing `DebugInfo()` to report the caches, would be a feature request, not a bug fix.
- **Not established:** I could not retrieve the #7099 diff (the PR description and the review threads I could read do not mention this section, and the diff URL was not retrievable), so I cannot confirm whether #7099 added the `targets` bullet. To check locally: `git log -S"the active targets the component tracks" --oneline -- docs/sources/reference/components/pyroscope/pyroscope.ebpf.md`.
- **Doc state before the fix:** the earlier note that this section was deliberately left untouched in #7099 pending a decision conflicts with the `targets` bullet, which is not in the published version. Treat "untouched" as unconfirmed. The equivalent gap on `pyroscope.receive_http` and `pyroscope.relabel` (both missing the section entirely) was fixed with the boilerplate after confirming neither implements `DebugInfo()` in source.
- **User impact (author's reading):** readers looked for debug output that does not exist.

### Item 14: `pyroscope.java`: `thread` block silently no-ops when both `frame` and `label_name` are unset — not applicable

- **Concern:** a `thread` block (`frame`, `label_name`, `regex`) under `profiling_config` is accepted and does nothing when both `frame` and `label_name` are unset.
- **Verdict:** not applicable to the current source. The `thread` block does not exist in the current tree: `args.go` has `per_thread` and `tlab` and no `thread` block, and `loop.go` only uses `PerThread` (`:237`). The doc at HEAD does not mention a `thread` block, and neither do the published docs through v1.19 and `next`.
- **Where the code was:** earlier notes place it on a local branch, `threads_fix`. That branch's origin was not established: its fetch history names a pull request that is not relevant to this audit and may have been mistyped. The branch's code was not read, so the claim about what `loop.go` does with an empty block was never verified.
- **Reopen if:** a `thread` block lands in `pyroscope.java`. Then check that the both-unset case is rejected or documented.

---

## Docs-only fixes (from the overview appendix)

Doc errors the audit found that are now corrected. Not numbered items, so they have no pointer line in [overview.md](overview.md), which notes only that these rows moved.

**Checked 2026-10-13 against the `alloy` working tree** on branch `docs/correct-minor-errors-component-docs` (cut from `main`). "Present at HEAD" means the corrected text is in that tree. It does not show whether it reached release branches.

| Component | Issue | Fix | Verified at HEAD |
|---|---|---|---|
| `prometheus.exporter.cadvisor` | `disabled_metrics` documented `[]`, but when the argument is omitted the integration subtracts a built-in disabled set from `AllMetrics`, so the effective default is not empty. Previously tracked as L6. | Doc fix on part 02. The Default cell reads `_see below_`, matching `prometheus.exporter.unix`, `.windows` and `.oracledb`. It was briefly changed to `[]`, caught as a regression, and restored. Not a code defect. Do not confuse with item 11, which is closed as not a bug. | Default cell is `_see below_` (`prometheus.exporter.cadvisor.md:133`). |
| `remote.vault` | `auth.azure` `resource_url` and `auth.kubernetes` `service_account_file` defaults were missing from their tables. | Doc fix. Values read from [auth.go][auth.go]: `DefaultAuthAzure.ResourceURL = "https://management.azure.com/"` and `AuthKubernetes.ServiceAccountTokenFile = "/var/run/secrets/kubernetes.io/serviceaccount/token"`. | Both defaults present (`remote.vault.md:142`, `:195`) and match the source (`auth.go:231`, `:342`). The earlier note that reviewer sign-off was outstanding was not rechecked. |
| `remote.vault` | The doc named `AWS_SESSION`; the AWS SDK uses `AWS_SESSION_TOKEN`. Previously tracked as L4. | Resolved. [auth.go][auth.go] contains no `AWS_` environment reads at all. It delegates to `hashicorp/vault/api/auth/aws`, which uses the SDK credential chain. The vendored SDK was not traced. | Line 109 reads `AWS_SESSION_TOKEN`. `auth.go` has no `AWS_` matches. |
| `remote.kubernetes.secret` | The example wrapped a ConfigMap value in `convert.nonsensitive()` that was never secret. | Doc fix. The example was restructured so the Secret holds both `username` and `password`, and `convert.nonsensitive` is demonstrated on `username` where it is genuinely needed. Validated with `alloy validate`, exit 0 (earlier run). | Example uses `convert.nonsensitive` on `username` only (`remote.kubernetes.secret.md:173-174`). `alloy validate` not re-run. |
| `pyroscope.scrape` | `scrape_timeout` default documented as `"18s"`, and a "Must be larger than `scrape_interval`" constraint that does not exist in source. | Doc fix. Corrected to `"10s"` and the invented constraint removed. This is the corroboration behind item 7, which is closed as not a bug. | Default is `"10s"` with no such constraint (`pyroscope.scrape.md:75`). |
| `pyroscope.scrape` | `delta_profiling_duration` was documented as "can't be larger than `scrape_interval`". Validation requires at most `scrape_interval - 1s` (`scrape.go:231-233`). | Doc fix: reworded to "must be, at most, `scrape_interval` minus 1 second". | Present in the working tree (`pyroscope.scrape.md:433`) and matches the validation. The 16s/17s example is consistent. Whether it is committed was not checked. |
| `pyroscope.scrape` | The `profile.custom` section said `seconds` "is equal to `scrape_interval - 1`". When `delta_profiling_duration` is not the default, `seconds` takes that value (`target.go:362-366`). | Doc fix: now says `seconds` is `scrape_interval - 1` unless `delta_profiling_duration` is set, and links to the delta argument section. | Present in the working tree (`pyroscope.scrape.md`, `profile.custom` section). Edited 2026-10-13 on `docs/correct-minor-errors-component-docs`; not committed when written. |
| `pyroscope.scrape` | The `scrape_timeout` description did not say the timeout is extended for delta profiles (`scrape_loop.go:167-169`). | Doc addition: new `#### scrape_timeout` section after `scrape_interval`, with the 10s + 14s = 24s default example. | Present in the working tree. Edited 2026-10-13 on the same branch; not committed when written. |
| `prometheus.echo` | The Component health section said the component is "only reported as unhealthy if given an invalid configuration", and the `format` text did not say what happens with an unrecognised value. A decode error such as a wrong-typed argument does make the component unhealthy (`node_builtin_component.go:265-275`), but an unrecognised `format` value does not: it logs a warning and uses `text` (`echo.go:234-242`). | Doc fix: added "If you set any other value, the component logs a warning each time it writes metrics and uses the `text` format" under `format`, reworded the health sentence to "if its configuration can't be evaluated, for example because an argument has the wrong type", and added that an unrecognised `format` doesn't make the component unhealthy. | Present in the working tree (`prometheus.echo.md:40`, `:57`, `:60`). Edited 2026-10-13 on `docs/correct-minor-errors-component-docs`; not committed when written. Revisit if validation is added (Item 12). |
| `prometheus.enrich` | Debug metrics table named `prometheus_target_cache_size`; the registered metric is `alloy_prometheus_target_cache_size` (`enrich.go:153`). `prometheus_fanout_latency` and `prometheus_forwarded_samples_total` are correct. They come from the shared `Fanout` type and carry no `alloy_` prefix. | Doc fix. | Table reads `alloy_prometheus_target_cache_size` (`prometheus.enrich.md:89`). The other two names are unchanged and correct. |
| `pyroscope.java` | On the `threads_fix` branch, the `otel.scope.name` and `otel.scope.version` auto-injected labels table was deleted while the code behaviour was unchanged. | Doc regression flagged for restoration before merge. | Table is present (`pyroscope.java.md:124-125`). `threads_fix` is not in the current tree, so the table is intact here. |

---

[grafana/alloy]: https://github.com/grafana/alloy
[auth.go]: https://github.com/grafana/alloy/blob/main/internal/component/remote/vault/auth.go
[#7099]: https://github.com/grafana/alloy/pull/7099
[#7119]: https://github.com/grafana/alloy/pull/7119
[#7111]: https://github.com/grafana/alloy/pull/7111
[#7266]: https://github.com/grafana/alloy/pull/7266
[catchpoint_exporter.go]: https://github.com/grafana/alloy/blob/main/internal/static/integrations/catchpoint_exporter/catchpoint_exporter.go
[#7124]: https://github.com/grafana/alloy/pull/7124
[#7309]: https://github.com/grafana/alloy/pull/7309
[send.go]: https://github.com/grafana/alloy/blob/main/internal/component/pyroscope/ebpf/send.go
[metrics.go]: https://github.com/grafana/alloy/blob/main/internal/component/pyroscope/ebpf/metrics.go

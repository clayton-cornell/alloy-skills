# Beyla docs: accuracy and gaps triage

Date: 2026-10-20
Scope: all 47 pages under `docs/sources/`, checked against the Beyla `main` checkout and the vendored OBI source (`vendor/go.opentelemetry.io/obi/`; the `.obi-src` submodule isn't checked out).
Method: `beyla-docs-analysis` in triage mode. Each page was checked by an automated reviewer for high-risk claims only (keys, env vars, defaults, metric names, capabilities, versions, examples). Counts are approximate.

Caveat: findings were produced by parallel reviewers and haven't been independently re-verified. Treat each Major as "confirmed by a reviewer, worth a maintainer's glance" before editing.

## Summary

| Verdict | Pages |
|---|---|
| Accurate | 16 |
| Minor | 12 |
| Major | 18 |
| Unverified | 1 |

## Cross-cutting issues

These explain most of the Major verdicts and are fixed in one pass across pages.

1. **`routes.unmatched` default is wrong.** Beyla defaults to `low-cardinality` (`pkg/beyla/config.go:83`), not `heuristic` or `/**`. Affects `routes-decorator.md` and all 7 language quickstarts, plus a comment in `quickstart/kubernetes.md`.
2. **Stale or invalid context-propagation names.** `enable_context_propagation`, `BEYLA_ENABLE_CONTEXT_PROPAGATION` and `disable_blackbox_cp` don't exist. Current names are `context_propagation` / `BEYLA_BPF_CONTEXT_PROPAGATION` and `disable_black_box_cp`. The YAML loader is non-strict, so wrong keys are silently ignored. Affects `cilium-compatibility.md`, `security.md`.
3. **Wrong metric name.** `messaging.publish.duration` should be `messaging.client.operation.duration`. Affects `metrics.md`, `cardinality.md`.
4. **5.17 `bpf_loop` requirement overstated.** Older kernels fall back to legacy programs. Affects `_index.md`, `distributed-traces.md`. `override_bpfloop_enabled` is undocumented.
5. **Incomplete feature and option lists.** `metrics.features` values (`application_red`, `application_sizes`, `ebpf`, `all`, `stats_*`), selectors (`languages`, `cmd_args`, `target_pids`, `k8s_job_name`) and several tuning options are missing. Affects `service-discovery.md`, `export-data.md`, `tune-performance.md`, `quickstart/kubernetes.md`.
6. **Deprecated keys in examples.** `otel_metrics_export.features`, `application_span` and `discovery.services` still work but are deprecated. Affects `setup/kubernetes-helm-appolly.md`, `setup/kubernetes-helm-k8s-monitoring.md`, `network/inter-az.md`.
7. **Stale sample output.** The trace-printer output in the quickstarts no longer matches the current printer. Affects the 7 language quickstarts and `network/quickstart.md`.

## Per-page results

### Top level

| Page | Verdict | Dev. | Gaps | Main issue |
|---|---|---|---|---|
| `_index.md` | Minor | 3 | ~1 | "Runs in any Linux environment" contradicts kernel/BTF startup check; 5.17 and Go "3 versions" claims unsupported |
| `beyla-dashboard.md` | Accurate | 0 | 0 | |
| `cardinality.md` | Minor | 2 | ~1 | Wrong messaging metric name; body-size bucket count off by one |
| `cilium-compatibility.md` | Major | 2 | ~1 | Demo config uses removed `enable_context_propagation` and misspelled `disable_blackbox_cp` |
| `distributed-traces.md` | Minor | 2 | ~2 | 5.17 claim; lockdown claim imprecise; `CAP_SYS_ADMIN` need not stated |
| `metrics.md` | Major | ~5 | ~6 | Wrong messaging metric and Prometheus suffixes; `db.collection.name` default wrong; many metrics missing |
| `obi.md` | Accurate | 0 | ~1 | `application_jvm` not in vendored OBI (see Open) |
| `requesttime.md` | Accurate | 0 | 0 | |
| `security.md` | Major | 3 | ~2 | Nonexistent env var; `CAP_CHECKPOINT_RESTORE` omitted; `kernel.sys_paranoid` inconsistent with page's own `perf_event_paranoid` |

### configure/

| Page | Verdict | Dev. | Gaps | Main issue |
|---|---|---|---|---|
| `_index.md` | Accurate | 0 | 0 | |
| `controlling-instrumentation.md` | Major | ~8 | ~4 | Wrong AWS/Elasticsearch env vars; wrong `enabled` defaults; wrong buffer limits; Aerospike listed twice |
| `example.md` | Accurate | 0 | 0 | |
| `export-data.md` | Minor | ~4 | ~8 | YAML syntax error in example; `BEYLA_OTEL_METRICS_FEATURES` mapping; `application_span_otel` missing |
| `export-modes.md` | Minor | 1 | 0 | Prose says `open_port`, key is `open_ports` |
| `filter-metrics-traces.md` | Accurate | 0 | ~2 | Numeric matchers (`greater_than`, etc.) undocumented |
| `internal-metrics-reporter.md` | Accurate | 0 | ~2 | `bpf_metric_scrape_interval` undocumented |
| `language-agents.md` | Minor | 1 | ~3 | Node.js agent also drives runtime metrics; options missing |
| `metrics-histograms.md` | Accurate | 0 | ~3 | GenAI, v8js, JVM buckets missing |
| `metrics-traces-attributes.md` | Major | ~2 | ~4 | `kubernetes.enable` default is `autodetect`; default-on trace attributes list incomplete |
| `name-resolver.md` | Accurate | 0 | 2 | `ecs`, `route53` sources undocumented |
| `options.md` | Minor | 1 | 2 | bpffs warning text differs; `target_pids`, `log_config` undocumented |
| `routes-decorator.md` | Major | 3 | 2 | Default `unmatched` wrong; `routes` has no env vars; deprecated options not marked |
| `sample-traces.md` | Accurate | 0 | 2 | Silent fallback on bad sampler config |
| `service-discovery.md` | Major | 3 | ~5 | Java harvest delay is 5s, not 60s; harvester languages incomplete; many selectors/options undocumented |
| `tune-performance.md` | Major | 2 | ~3 | `wakeup_len` default is 500, not unset; wrong YAML section heading; batch options missing |

### quickstart/

| Page | Verdict | Dev. | Gaps | Main issue |
|---|---|---|---|---|
| `_index.md` | Accurate | 0 | 1 | Kubernetes quickstart not listed |
| `cpp.md` | Major | ~3 | 0 | `/**` claim; sample output shows `generic`, OBI detects `cpp`; stale output |
| `golang.md` | Major | ~2 | 0 | `/**` claim; stale output |
| `java.md` | Major | ~2 | 0 | `/**` claim; stale output |
| `kubernetes.md` | Minor | ~3 | ~1 | Secret name mismatch (`grafana-secrets` vs `grafana-credentials`); selector list incomplete |
| `nodejs.md` | Major | ~2 | 0 | `/**` claim; stale output |
| `python.md` | Major | ~2 | 0 | `/**` claim; stale output |
| `ruby.md` | Major | ~2 | 0 | `/**` claim; stale output |
| `rust.md` | Major | ~2 | 0 | `/**` claim; stale output |

### setup/

| Page | Verdict | Dev. | Gaps | Main issue |
|---|---|---|---|---|
| `_index.md` | Accurate | 0 | 0 | |
| `docker.md` | Accurate | 0 | 0 | |
| `helm-alloy.md` | Unverified | 0 | 0 | Alloy chart and component live outside this repo |
| `kubernetes-helm-appolly.md` | Minor | 3 | ~3 | Deprecated keys; filename typo; `preset`, `privileged`, `k8sCache` undocumented |
| `kubernetes-helm-k8s-monitoring.md` | Minor | 1 | 0 | Deprecated `discovery.services` |
| `kubernetes-helm.md` | Accurate | 1 (typo) | ~4 | Chart defaults match; `preset`, `privileged`, `k8sCache` undocumented |
| `kubernetes.md` | Major | 2 | ~3 | `grafana.otlp.submit` should be `cloud_submit` (silently ignored); RBAC prose and YAML disagree |
| `standalone.md` | Accurate | 0 | ~2 | `BEYLA_CONFIG_PATH` and fine-grained capabilities not documented |

### network/

| Page | Verdict | Dev. | Gaps | Main issue |
|---|---|---|---|---|
| `_index.md` | Minor | ~4 | ~3 | Default attributes incomplete; `geoip` should be `geo_ip`; node-name keys use dots instead of underscores |
| `asserts.md` | Minor | ~1 | 0 | `values.yml` vs `values.yaml` |
| `config.md` | Accurate | 0 | ~6 | `deduper`, `guess_ports`, `listen_interfaces`, `geo_ip`, `reverse_dns` undocumented; `network.enable` deprecated but not marked |
| `inter-az.md` | Major | ~2 | ~1 | Nonexistent `k8s.src.pod.name` attributes (silently ignored); wrong defaults claim; uses deprecated `features` location |
| `quickstart.md` | Major | ~5 | ~1 | Says Prometheus export unsupported for network metrics (it is supported); wrong printer setting; stale output |

## Topic-level gaps (source behavior with no page or section)

The per-page "Gaps" counts above only cover missing detail inside existing pages. This section covers source features that have no coverage anywhere in `docs/sources/`. It comes from a keyword-coverage survey of the config structs and `cmd/`, not a page-by-page review, so treat it as a candidate list.

### Missing topics (no page, or no mention anywhere)

| Topic | Source | Suggested home |
|---|---|---|
| Kubernetes metadata cache service (`beyla-k8s-cache`): config (`BEYLA_K8S_CACHE_*`), Helm `k8sCache` values, when to use it | `cmd/k8s-cache/`, `cmd/k8s-cache/cfg/config.go`, `charts/beyla/values.yaml:296` | New page under `setup/` or `configure/` |
| TCP stats metrics (`stats:` section: `agent_ip`, `agent_ip_iface`, `interfaces`, etc.). Only the `stats_tcp_*` feature names are mentioned in `export-data.md` | `vendor/.../obi/stats_cfg.go:15` | New page, parallel to `network/config.md` |
| Cloud metadata (`cloud_metadata`: `cluster_name`, `region`, `refresh_interval`, Route53) | `vendor/.../transform/name_resolver.go:82` | Section in `configure/` |
| GenAI export to Grafana AI (`sigil_export`, `BEYLA_GRAFANA_AI_*`). GenAI payload extraction is documented, the export path isn't | `pkg/export/otel/sigil_export.go`, `pkg/beyla/config.go` (`SigilExport`) | Section in `configure/export-data.md` |
| .NET runtime metrics (`dotnet_runtime_metrics`). JVM equivalent is documented | `vendor/.../obi/config.go:750` | Next to the JVM section in `export-data.md` |
| Host ID override (`attributes.host_id.override`), `metadata_retry`, `target_pids`, `log_config`, `override_bpfloop_enabled` | `pkg/beyla/config.go`, `vendor/.../config/ebpf_tracer.go:89` | `configure/options.md` or `metrics-traces-attributes.md` |
| Config JSON schema (`docs/config-schema.json`, `cmd/beyla-schema`) for editor validation | `cmd/beyla-schema/main.go` | Short section in `configure/` |
| Troubleshooting and common errors (startup capability/kernel/BTF failures, silent ignore of unknown keys) | `vendor/.../obi/os.go`, `pkg/beyla/config.go` (`Validate`) | New page |
| Upgrade and breaking-change guidance (deprecated `application_span`, `otel_metrics_export.features`, `discovery.services`, `executable_name`, service name/namespace) | `pkg/beyla/config.go` (`normalizeConfig`, deprecations) | New page |

### Thinly covered (mentioned but not explained)

- **Kubernetes metadata attributes:** options such as `drop_external`, `meta_cache_address`, `resource_labels` and `kubernetes.cluster_name` exist in source (`transform/k8s.go:43-85`) but aren't documented.
- **Alloy integration:** listed as a feature in `_index.md`, but there's no page in this repo explaining the `beyla.ebpf` Alloy component or how it differs from standalone Beyla.
- **Helm chart reference:** `preset`, `privileged`, `extraCapabilities` and `k8sCache` aren't documented in any setup page.

### Not counted as gaps

- **OpenTelemetry SDK injection and the mutating webhook** (`injector`, `external_deployment_name`, `pkg/webhook/`). The source marks these "purely experimental and undocumented" (`pkg/beyla/config.go`, `Injector` field), so the absence is intentional.
- **Developer-only options** (`channel_buffer_len`, `profile_port`, `bpf_pid_filter_off`, etc.), which `config.go` says are deliberately undocumented.

## Open items (not counted)

- `controlling-instrumentation.md`: `enable_context_propagation` row has no matching field in the vendored source. Needs a maintainer check.
- `obi.md`: `application_jvm` isn't in the vendored `FeatureMapper`. The page may describe a newer upstream OBI than this checkout vendors.
- `tune-performance.md`: whether an explicitly empty `traffic_control_backend` is accepted wasn't traced.
- `service-discovery.md`: Java harvest delay finding assumes the Beyla-to-OBI config copy preserves the field; the Go harvester wasn't confirmed to exist.
- `kubernetes.md`, `quickstart/kubernetes.md`: whether the `get` RBAC verb is required wasn't confirmed.
- `asserts.md`: unquoted `k8s.grafana.com/scrape: true` annotation value may be rejected by Kubernetes.
- Third-party behavior (Alloy, k8s-monitoring chart, Grafana Cloud, published images, Prometheus native-histogram thresholds) is not verifiable in this repo.

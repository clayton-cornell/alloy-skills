# Accuracy checklist (Step 3)

Use with `source-map.md` (where to look) and `technical-verification.md`
(what to check first). Paths are relative to the Beyla repo root; `OBI/` below
means `vendor/go.opentelemetry.io/obi/` (write the full path in findings).
Every path in this file was opened and confirmed on 2026-10-20.

## Citation rule (applies to every item)

Cite both sides: the documentation `file:line` AND the source `file:line`.
Open the source file and read the surrounding code before citing it; a grep hit
is not a citation. A discrepancy missing either side isn't reportable yet: go
find the other side, or move the claim to Open questions. A cited path that
doesn't resolve is no evidence at all. If a claim depends on OBI behavior, say
it rests on the vendored copy (see `source-map.md`).

## Triage order (risk-tiered)

Verify in this order and stop early on clean pages:

1. Config keys, env vars and defaults in tables and prose.
2. YAML/shell/Helm examples users copy (run `example-validation.md` first; it
   is cheap and catches wrong keys fast).
3. Metric and attribute names, and Prometheus names derived from them.
4. Kernel, OS, capability and language-support claims.
5. Helm values, image, systemd, Kubernetes manifest claims.
6. Enum and feature lists (completeness of the list, not just each entry).
7. Sample output (trace printer, flow printer, log lines).
8. Narrative behavior claims.

## 1. Config keys, env vars, defaults, types

### 1.1 The key exists, under the right parent

- [ ] Find the `yaml:"..."` tag in `pkg/beyla/config.go`; if the field's type is
      imported, open that type (see the table in `source-map.md`). Compare
      spelling, case, singular/plural and nesting level exactly.
- [ ] **Silent-unknown-key rule.** `LoadConfig` decodes YAML with
      non-strict `yaml.Unmarshal` (`pkg/beyla/config.go`, in `LoadConfig`), so a
      misspelled or renamed key is silently ignored and the feature just doesn't
      turn on. Every YAML key in a doc table or example must be matched to a tag
      or to `docs/config-schema.json`. Don't assume the key works because the
      example "looks right".
- [ ] Not everything is silent. Selector keys under `discovery.instrument`,
      `exclude_instrument`, `services`, `exclude_services` that aren't known
      fields land in the inline metadata map and are rejected at startup
      (`OBI/pkg/appolly/services/criteria.go` `Validate`;
      `AllowedAttributeNames`). `filter.*` attribute names that don't exist fail
      pipeline setup (`OBI/pkg/filter/attribute.go`, "unknown attribute name").
      `attributes.select` names that don't exist match nothing silently
      (`OBI/pkg/export/attributes/attr_select.go`, "TODO: validate too"). Use the
      right expectation when a page says what happens on a typo.
- [ ] Beyla and OBI don't always name the same option the same way:
      Beyla `executable_name` / `BEYLA_EXECUTABLE_NAME` (deprecated) vs OBI
      `executable_path`. If the page, an example or a copied snippet uses an OBI
      name, check the Beyla tag, not the OBI one.
- [ ] Check removed keys. Observed in the 2026-10-20 triage: stale or renamed
      keys such as `enable_context_propagation` (not present in the checkout;
      the key is `ebpf.context_propagation`), `disable_blackbox_cp` (actual
      `ebpf.disable_black_box_cp`), `grafana.otlp.submit` (actual
      `grafana.otlp.cloud_submit`) and `open_port` vs `open_ports` (top-level
      `open_port` vs the discovery selector `open_ports`). Grep the checkout for
      the key to prove it doesn't exist before calling it removed.

### 1.2 Environment variables

- [ ] Find the `env:"..."` tag on the field. Which type owns the field decides
      the name:
      - Beyla-owned field: the tag is the name (`BEYLA_*`; also
        `GRAFANA_CLOUD_*`, `OTEL_SERVICE_NAME`, `KUBECONFIG` where the tag says
        so). `OTEL_EBPF_*` isn't accepted for these.
      - Field in an OBI type: the tag says `OTEL_EBPF_*`. **`BEYLA_` ->
        `OTEL_EBPF_` mapping check:** `OverrideOBIGlobalConfig`
        (`pkg/beyla/config_obi.go`, called first in `LoadConfig`) rewrites each
        `BEYLA_*` variable with regex `^BEYLA_(OTEL_)?` to `OTEL_EBPF_` and sets it
        only when that variable isn't already set. So the documented
        `BEYLA_X` is valid if `OTEL_EBPF_X` is a tag on the field; both spellings
        work and an explicit `OTEL_EBPF_X` wins. Confirm the tag exists; a
        `BEYLA_X` with no matching tag is silently ignored.
- [ ] Env var names aren't derived from the YAML path. Examples:
      `network.enable` is `OTEL_EBPF_NETWORK_METRICS` (so `BEYLA_NETWORK_METRICS`);
      `trace_printer` is `BEYLA_TRACE_PRINTER`; Grafana Cloud uses
      `GRAFANA_CLOUD_*`. Always read the tag.
- [ ] A YAML-only field (no `env` tag) documented with an env var, or an
      env-only field documented with a YAML key, is wrong. Tags like
      `yaml:"-"` mean not configurable in YAML (`TracesReceiver`, internal
      caches).
- [ ] `${VAR}` substitution inside YAML files: `pkg/config/env_replacer.go`
      supports `${VAR}`, `${env:VAR}`, `${VAR:-default}`, and `$${VAR}` as an
      escape. Check any doc claim about substitution against that regex.

### 1.3 Defaults: trace the effective value

Do not stop at the struct. Trace in this order and stop at the first layer that
sets the value (later layers win):

1. Env var, if the field has an `env` tag (`env.Parse` in `LoadConfig`).
2. YAML as parsed.
3. `normalizeConfig` (`pkg/beyla/config.go`): may rewrite values (deprecated
   `otel_metrics_export.features` / `prometheus_export.features` override
   `metrics.features`; `network.enable` ORs the `network` feature; default
   `app` extra group attributes; appended default span resource labels).
4. `DefaultConfig()` (`pkg/beyla/config.go`): Beyla's overrides of OBI.
5. `FromOBI(&obi.DefaultConfig)`: `OBI/pkg/obi/config.go`, `var DefaultConfig`.
6. The type itself: `envDefault` tags, `UnmarshalYAML`/`UnmarshalText`, or a
   consumer that applies a fallback when it reads the value (for example OTLP
   protocol resolved from `OTEL_EXPORTER_OTLP_*` in `OBI/pkg/export/otel/otelcfg/`).
7. Zero value.

Beyla-vs-OBI overrides to check first (observed in `DefaultConfig`, re-read it):
`routes.unmatched` is `low-cardinality` in Beyla and `heuristic` in OBI;
`grafana.otlp.cloud_submit` defaults to traces; `name_resolver.sources` is
`k8s` + `rdns` in Beyla (OBI: `k8s` + `ecs`); `processes` run mode and
interval; `discovery.default_exclude_*`. Observed-but-not-overridden (so OBI's
value is Beyla's): `ebpf.wakeup_len` is 500 in `OBI/pkg/obi/config.go`;
`attributes.kubernetes.enable` is `autodetect`
(`OBI/pkg/kube/kubeflags/kubeflags.go`), which `IsKubeEnabled` in
`OBI/pkg/kube/informer_provider.go` resolves to enabled only when a Kubernetes
config (in-cluster or kubeconfig) loads, so state both the value and the
effective behavior.

- [ ] The doc default matches the traced effective default, not the struct
      comment, not an OBI doc page, not a deployment sample. Chart, `contrib/`
      and example defaults are not binary defaults (e.g. `contrib/beyla.yaml`
      sets `ebpf.wakeup_len: 100`).
- [ ] Default for a durations/size is expressed in the unit the code parses
      (`time.Duration` strings like `5s`; bytes vs entries vs bits).
- [ ] A source comment that says a section is "optional" or "not set" can be
      stale. `Config.Routes` is commented as optional ("If not set, data will be
      directly forwarded to exporters"), but `DefaultConfig()` always sets it,
      so the section is never nil. Check `DefaultConfig()` before trusting a
      comment about whether a section is present by default.
- [ ] A default given as "unset"/"disabled" matches the zero-value semantics
      (e.g. `ebpf.context_propagation` is `disabled`; `network.source` is
      `socket_filter`).

### 1.4 Types, enums, validation, deprecation

- [ ] Type in the doc (string, int, duration, list, map, bool) matches the Go
      field. YAML list vs comma-separated env var is a frequent mismatch: check
      `envSeparator`.
- [ ] Enum lists are exhaustive and current. Sources: `UnmarshalText`/switch on
      the type (`ContextPropagationMode` in `OBI/pkg/config/ebpf_tracer.go`:
      `all`, `headers`, `tcp`, `disabled`, with `ip` accepted but a no-op),
      `validate:"oneof=..."` tags (documentation hints only), `.Valid()` methods
      (`trace_printer`: `disabled`, `counter`, `text`, `json`, `json_indent` in
      `OBI/pkg/export/debug/debug.go`; `traffic_control_backend`), and
      `FeatureMapper` for metrics features (`OBI/pkg/export/feature.go`).
- [ ] "Beyla rejects X" claims: `Config.Validate` doesn't run OBI's
      struct-tag `validator`, so a `validate:"..."` tag alone doesn't prove
      rejection. Find the check that actually runs (`Validate` in
      `pkg/beyla/config.go`, `UnmarshalText`, or the consumer). Invalid
      `routes.unmatched` logs a warning and falls back
      (`OBI/pkg/transform/routes.go`).
- [ ] Deprecations: grep `Deprecated` on the field and its type. Known, observed
      in the checkout: `discovery.services` / `exclude_services` /
      `default_exclude_services` (use `instrument` / `exclude_instrument` /
      `default_exclude_instrument`, `pkg/services/criteria.go`);
      `executable_name`, `service_name`, `service_namespace`;
      `otel_metrics_export.features` and `prometheus_export.features` (use
      `metrics.features`); metrics features `application_span` (use
      `application_span_otel`) and `application_span_sizes` (no replacement),
      from `deprecatedFeatures` in `OBI/pkg/export/feature.go`. A deprecated item
      used in an example without a deprecation note is a finding; so is a doc
      that presents a deprecated key as current.
- [ ] Required-together and conflicting settings that `Validate` enforces
      (`pkg/beyla/config.go`): at least one exporter, network/stats need a
      metrics exporter or print flag, only one span-metrics format,
      `routes.wildcard_char` is one character, internal OTEL metrics can't be
      combined with an internal Prometheus port, `ebpf.batch_length` >= 1.
- [ ] Per-service overrides: `discovery.instrument[].metrics.features`,
      `exports`, `sampler`, `routes` exist per selector
      (`OBI/pkg/appolly/services/attr_glob.go`). Check that a doc claiming a
      global-only setting isn't also per-service, and vice versa.

### 1.5 Following the Beyla -> OBI conversion

Runtime consumers mostly read OBI's config type, not Beyla's. For a claim about
effective behavior:

- [ ] `Config.AsOBI()` (`pkg/beyla/config_obi.go`) copies same-named fields
      from Beyla's `Config` into `obi.Config` with `Convert`
      (`pkg/helpers/config/convert.go`), then applies `overrideOBI`: when
      `grafana.otlp` submits metrics or traces, the OTLP endpoint and the
      `Authorization` header are replaced with the Grafana Cloud ones
      (`pkg/export/otel/grafana.go`; endpoint is
      `https://otlp-gateway-<cloud_zone>.grafana.net/otlp`, and Grafana is
      considered enabled when any of `cloud_instance_id`, `cloud_api_key`,
      `cloud_zone` is set). The result is cached; `invalidateOBICache` rebuilds it
      after Beyla's config is mutated.
- [ ] Fields skipped in `FromOBI` are Beyla-only (`Grafana`, `Processes`,
      `Injector`, `Topology`, `SigilExport`, `TracesReceiver`,
      `Discovery.Survey`): their behavior lives in `pkg/`, not in OBI.
- [ ] Pipeline wiring is in `pkg/components/beyla.go`; Beyla-specific
      exporters are in `pkg/export/otel/` and `pkg/export/prom/`, OBI's in
      `OBI/pkg/export/otel/` and `OBI/pkg/export/prom/`. Find which one a
      setting reaches before citing a consumer.

## 2. CLI and config-file loading

- [ ] The only flag is `-config` (stdlib `flag`, so `-config` and `--config` both
      parse) in `cmd/beyla/main.go`. Any other flag in a doc is wrong.
- [ ] `BEYLA_CONFIG_PATH` overrides `-config` when set (main.go reads the env
      after `flag.Parse`). The page must not say the flag wins.
- [ ] Precedence is defaults -> YAML (after `${ENV}` replacement) -> env vars
      (`LoadConfig`, `pkg/beyla/config.go`); env always wins over YAML.
- [ ] No config file is allowed (file optional) but `Validate` still demands an
      app-discovery, network or stats section.
- [ ] Documented startup behavior matches the order in `main.go`
      (`CheckOSSupport` before config load; capabilities checked after config
      validation; missing capabilities are a warning unless `enforce_sys_caps`).

## 3. Metric and attribute names

- [ ] Metric names: find the definition, not a copy. OBI definitions:
      `OBI/pkg/export/attributes/metric.go`, `metric_service_graph.go`,
      `metric_spanmetrics.go`, `metric_internal.go`; exporter-specific emitters
      in `OBI/pkg/export/otel/` and `OBI/pkg/export/prom/`. Beyla's own:
      `pkg/export/extraattributes/metric.go` (process metrics),
      `pkg/export/otel/metrics_proc.go`, `pkg/export/prom/prom_proc.go`,
      `metrics_survey.go`/`prom_survey.go`.
- [ ] **Beyla renames OBI names at runtime.** Don't flag or confirm a name from
      OBI's vendored definition until you've checked
      `OverrideOBIGlobalConfig` in `pkg/beyla/config_obi.go` (vendor prefix
      `obi` becomes `beyla`; `beyla.network.flow.bytes`,
      `beyla.network.flow.packets`, `beyla.network.inter.zone.bytes`,
      `beyla.stat.tcp.*`; attribute `beyla.ip`).
- [ ] OTel (OTLP) name vs Prometheus name. The Prometheus name is derived,
      never written by hand: `metric()` in
      `OBI/pkg/export/attributes/metric.go` (and `beylaMetric` in
      `pkg/beyla/config_obi.go`) call `otlptranslator.MetricNamer{WithMetricSuffixes: true}`
      on name + unit + instrument type. Derive, don't recall: dots become
      underscores, counters gain `_total`, unit suffixes are appended
      (`_seconds`, `_bytes`), histograms add `_bucket`/`_sum`/`_count` at scrape
      time. Check a doc's Prometheus name against the OTLP name and unit in
      the definition. Observed in the 2026-10-20 triage: wrong messaging metric
      name (the definition is `messaging.client.operation.duration`, not
      `messaging.publish.duration`) and a suffix mismatch.
- [ ] Span-metrics and service-graph metric families are separate definitions
      with different naming (`application_span` legacy `traces_spanmetrics_*`,
      `application_span_otel` `traces_span_metrics_*`, in
      `OBI/pkg/export/feature.go` comments and `metric_spanmetrics.go`).
- [ ] Attribute names: `OBI/pkg/export/attributes/names/attrs.go` and
      `pkg/export/extraattributes/names/attrs.go`. A name that isn't defined
      there doesn't exist; selecting it matches nothing.
- [ ] Default-on vs opt-in attributes: the `Default` map in each
      `NewAttrReportGroup` call in `OBI/pkg/export/attributes/attr_defs.go` and
      `pkg/export/extraattributes/attr_defs.go` (a `true` entry is on by
      default). Check both the list a doc gives and the groups that
      are conditional (Kubernetes, Prometheus-only, container).
- [ ] Attribute-selector syntax claims (`attributes.select.<metric>.include` /
      `exclude`, wildcards, dots vs underscores): `attr_select.go`
      (`Normalize` strips metric suffixes; matching is on underscore form).
- [ ] Feature list for `metrics.features` is complete and spelled as
      `FeatureMapper` in `OBI/pkg/export/feature.go` (`stats*`, `network*`,
      `application`, `application_red`, `application_sizes`,
      `application_span`, `application_span_otel`, `application_span_sizes`,
      `application_service_graph`, `application_runtime`, `ebpf`, `all`, `*`);
      flag deprecated entries and what `application` expands to.
- [ ] Instrumentation names (`instrumentations`), selector keys, and bucket
      defaults (`OBI/pkg/export/bucket.go`) come from their types; don't assume.

## 4. Kernel, OS, capability and language support

- [ ] Minimum kernel and BTF: `OBI/pkg/obi/os.go` (`minKernMaj`/`minKernMin` =
      5.8; RHEL-based 4.18 exception that applies only at exactly 4.18; BTF
      required, `hasBTF`). The check runs at startup in `cmd/beyla/main.go`.
- [ ] Capabilities: `OBI/pkg/obi/os.go` `CheckOSCapabilities` and
      `checkCapabilitiesForSetOptions`. `CAP_SYS_ADMIN` satisfies all on kernels
      >= 5.8; below 5.8 only `CAP_SYS_ADMIN` is accepted; `CAP_BPF` always;
      `CAP_SYS_RESOURCE` only below 5.11; app observability needs
      `CAP_CHECKPOINT_RESTORE`, `CAP_DAC_READ_SEARCH`, `CAP_SYS_PTRACE`,
      `CAP_PERFMON`, `CAP_NET_RAW`; `CAP_NET_ADMIN` when any context propagation
      mode is enabled (the check is `IsEnabled()`, which is true for `headers`
      too) or when the network source is `tc`; network `socket_filter` needs
      `CAP_NET_RAW` + `CAP_PERFMON`; stats needs `CAP_SYS_PTRACE`, `CAP_PERFMON`,
      `CAP_NET_RAW`. Compare the doc's table row by row, including the
      condition on each capability.
- [ ] Go-level context propagation also depends on `CAP_SYS_ADMIN` and kernel
      lockdown state on kernels >= 5.10
      (`SupportsContextPropagationWithProbe`,
      `OBI/pkg/ebpf/common/common.go`).
- [ ] `bpf_loop` requires kernel 5.17; older kernels use a legacy program set
      unless `ebpf.override_bpfloop_enabled` is true
      (`SupportsEBPFLoops`, `FixupSpec` in `OBI/pkg/ebpf/common/common.go`).
- [ ] Go version support: minimum Go 1.17 (`minGoVersion` in
      `OBI/pkg/internal/goexec/gofile.go`), with higher minimums for some runtime
      metrics in the same file. Other language/protocol support lists: follow
      `OBI/pkg/internal/ebpf/` (generictracer, gotracer, etc.) and
      `OBI/pkg/ebpf/common/` transforms. Support lists in docs go stale
      silently; for a "supports X" claim find the code that handles X.
- [ ] Architecture, container and distro claims: what you can't see in Go (eBPF
      C, `.obi-src` not checked out) goes to Open questions with the exact OBI
      file or directory to inspect.
- [ ] Cilium/TC claims: `EnsureCiliumCompatibility`
      (`OBI/pkg/ebpf/tcmanager/cilium_support.go`) and `Validate` in
      `pkg/beyla/config.go` (`willUseTC`).

## 5. Deployment, Helm, Docker, Kubernetes

- [ ] Helm value names, nesting and defaults: `charts/beyla/values.yaml` (top
      level includes `image`, `privileged`, `contextPropagation`,
      `extraCapabilities`, `securityContext`, `service`, `config`, `env`,
      `envValueFrom`, `preset`, `serviceMonitor`, `k8sCache`, `injector`,
      `rbac`, `extraObjects`). Check the rendering in `charts/beyla/templates/`
      (`configmap.yaml`, `daemon-set.yaml`, `cluster-role.yaml`,
      `cache-deployment.yaml`) because the template decides what a value does.
      Values passed under `config.data` are Beyla YAML: check them as Beyla
      config too.
- [ ] Chart defaults aren't binary defaults: `preset` (`application` adds
      `discovery.instrument` with `k8s_namespace: "*"` only if the user gave no
      `discovery`; `network` adds `network.enable`), `config.data` defaults
      (`attributes.kubernetes.enable: true`, `prometheus_export.port: 9090`),
      `k8sCache.replicas: 0` (cache disabled). Chart version and app version
      are in `charts/beyla/Chart.yaml`.
- [ ] Image names, entrypoint and user: `Dockerfile` (`FROM scratch`,
      `ENTRYPOINT ["/beyla"]`), `k8scache.Dockerfile`, `javaagent.Dockerfile`.
      The image has no shell, which breaks `docker exec ... sh` instructions.
- [ ] systemd/standalone: `contrib/beyla.service` (`ExecStart`,
      `EnvironmentFile`, `User=root`), `contrib/beyla.env`, `contrib/beyla.yaml`.
- [ ] Kubernetes: RBAC rules in `charts/beyla/templates/cluster-role.yaml`,
      DaemonSet host settings in `daemon-set.yaml` (host PID, volumes, env
      `BEYLA_CONFIG_PATH`, `BEYLA_KUBE_META_CACHE_ADDRESS`), cache service in
      `cmd/k8s-cache/cfg/config.go` (`BEYLA_K8S_CACHE_*`).
- [ ] Alloy-chart and Kubernetes-Monitoring-chart pages
      (`setup/helm-alloy.md`, `kubernetes-helm-k8s-monitoring.md`) describe
      other repositories. Verify only what Beyla's side defines; list the rest
      as Open questions naming the repo.
- [ ] Commands and image tags in setup pages (`docker run`, `helm install`,
      versions): see `example-validation.md` (shell commands); never pull or
      run anything yourself.

## 6. Sample output

- [ ] Trace printer text lines: compare field set and order to `printSpan` in
      `OBI/pkg/export/debug/debug.go` (time, duration pair, type/subType,
      status, method, path, route in parentheses, peer/host with `as`,
      `contentLen`, `responseLen`, `svc=`, `traceparent=`). JSON
      printers marshal the span struct directly; `counter` prints
      `Processed N requests`.
- [ ] Network flow lines: `printFlow` in
      `OBI/pkg/internal/netolly/export/printer.go` (prefix `network_flow:`,
      `transport=`, `<prefix>.ip=` where the prefix is `beyla` at runtime,
      `iface=`, `iface_direction=`, `src.address`, `dst.address`, `src.name`,
      `dst.name`, `src.port`, `dst.port`, then metadata). Stats printer:
      `OBI/pkg/internal/statsolly/export/printer.go`.
- [ ] Log lines: grep the message literal, open the file, check the level and
      the key names (`slog` text format prints `key=value`). Message text in the
      docs that doesn't exist verbatim is paraphrase; report it and propose the
      real text, or Open question when no close match exists. Sample 3 to 5 and
      say which you checked.
- [ ] Startup log lines in `cmd/beyla/main.go` (`Grafana Beyla`,
      `configuration loaded`, capability warnings) when a page quotes them.

## 7. Narrative behavior claims

- [ ] Find the code that does it, trace one call path from config to consumer,
      and cite it. Claims about "how Beyla decides", discovery timing
      (`poll_interval`, `min_process_age`), exclusion defaults
      (`default_exclude_*`), cardinality limits (`routes`,
      `metric_span_names_limit`, `max_path_segment_cardinality`), or trace
      context propagation modes are checkable; "lightweight" or "low overhead"
      is marketing and isn't.
- [ ] Beyla-vs-OBI statements (`obi.md`): the vendored dependency and what
      `pkg/beyla/config_obi.go` changes are the evidence.
- [ ] Tests (`pkg/beyla/config_test.go` and others) corroborate a default or an
      error; read what the test exercises before relying on it. Generated test
      directories aren't in this checkout.
- [ ] When the source is ambiguous, say so as an Open question. Never convert
      an unverified claim into a finding.

## 8. Error classes observed in the 2026-10-20 triage

Cheap detectors, one per class (from a read-only triage of all 47 pages, not
independently re-verified by a person):

| Class | Cheap detection |
|---|---|
| Wrong default because Beyla overrides OBI | Re-read `DefaultConfig()`; compare every "default" cell against the layered trace in 1.3 |
| Stale or renamed key / env var, silently ignored | Run the YAML checker; grep the key in `pkg/` and `vendor/go.opentelemetry.io/obi/pkg/`; look up the env tag |
| Wrong metric or attribute name; wrong Prometheus derivation | Open the `attributes/metric*.go` definition, check `config_obi.go` renames, derive the Prometheus name |
| Deprecated config used in examples | Grep `Deprecated`/`deprecatedFeatures`; see the list in 1.4 |
| Kernel, OS, capability, language claims | Table in section 4 against `os.go` and `gofile.go` |
| Sample output no longer matches printer | Section 6 field-by-field |
| Incomplete enum or feature lists | Section 1.4 and 3 enumerations against `FeatureMapper`, `UnmarshalText`, discovery selector fields |
| Default-on attribute lists wrong | `attr_defs.go` `Default` maps in OBI and Beyla |
| Helm values wrong | Section 5 against `values.yaml` and templates |
| Example with YAML syntax errors | `example-validation.md` |

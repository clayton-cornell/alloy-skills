# Beyla documentation-to-source map

Use this as a starting point, then follow the implementation to the behavior
the documentation claims. Paths are relative to the Beyla repository root.
The current checkout is authoritative; this map isn't a substitute for
verifying the exact source and its version. Every path below was opened and
confirmed to exist on 2026-10-20; if one no longer resolves, find the moved
file and use the real path in findings.

**Path shorthand.** `OBI/` means `vendor/go.opentelemetry.io/obi/`. Write the
full `vendor/go.opentelemetry.io/obi/...` path in findings, never `OBI/`.

## Where a setting is defined

Beyla is a wrapper around OpenTelemetry eBPF Instrumentation (OBI), so a
documented option is defined in one of three places. Work out which before you
look for its default or env var:

| Kind | Where | Env var tag looks like | How `BEYLA_*` works |
|---|---|---|---|
| Beyla-owned type | `pkg/beyla/config.go`, `pkg/services/criteria.go`, `pkg/export/otel/grafana.go`, `pkg/export/otel/spanscfg/traces.go`, `pkg/internal/infraolly/process` | literal `BEYLA_*` (or `GRAFANA_CLOUD_*`, `OTEL_*`) | Read directly from the tag |
| OBI type shared with Beyla | `OBI/pkg/obi/`, `OBI/pkg/config/`, `OBI/pkg/export/...`, `OBI/pkg/transform/`, `OBI/pkg/filter/`, `OBI/pkg/appolly/services/` | `OTEL_EBPF_*` | `OverrideOBIGlobalConfig` in `pkg/beyla/config_obi.go` copies each `BEYLA_*` / `BEYLA_OTEL_*` variable to `OTEL_EBPF_*` unless that variable is already set |
| Mirror of an OBI type | Beyla field copied with `Convert` in `pkg/helpers/config/convert.go` (`FromOBI` / `AsOBI` in `pkg/beyla/config_obi.go`) | `BEYLA_*` | Read directly; the OBI twin keeps `OTEL_EBPF_*` |

Consequences worth remembering: a Beyla-owned field with a `BEYLA_*` tag does
not accept the `OTEL_EBPF_*` spelling; a shared OBI field accepts both, with
`OTEL_EBPF_*` winning when both are set; some env vars have neither prefix
(`GRAFANA_CLOUD_*`, `OTEL_EXPORTER_OTLP_*`, `OTEL_SERVICE_NAME`,
`OTEL_TRACES_SAMPLER`, `KUBECONFIG`, `BEYLA_CONFIG_PATH`).

## Configuration

- Beyla's top-level configuration and its direct YAML/environment tags live in
  `pkg/beyla/config.go` (`Config` struct, `DefaultConfig`, `LoadConfig`,
  `normalizeConfig`, `Validate`).
- Defaults that Beyla changes from OBI defaults are set by `DefaultConfig` in
  `pkg/beyla/config.go`. It starts from `OBI/pkg/obi/config.go`
  (`var DefaultConfig`, converted with `FromOBI`), then overrides, among
  others: Grafana OTLP `cloud_submit` = `traces`, `processes`,
  `discovery.default_exclude_*`, `name_resolver.sources` = `k8s` + `rdns`,
  `injector.enabled_sdks`, and `routes.unmatched` = `low-cardinality`. Re-read
  the function; it's the source of truth, not this list.
- Beyla's `Config.Validate` doesn't run OBI's struct-tag `validator`; the
  `validate:"..."` tags in OBI types document intent but aren't enforced by
  Beyla's startup path. Check the consumer or an `UnmarshalText` method before
  claiming a value is rejected.
- Nested settings live in other packages. Follow the imported type:
  - eBPF tuning: `OBI/pkg/config/ebpf_tracer.go`, `payload_extraction.go`,
    `log_enricher.go`, `tcbackend.go`, `cudamode.go`, `ebpf_map_reader.go`.
  - Network and stats: `OBI/pkg/obi/network_cfg.go`, `stats_cfg.go`.
  - Discovery selectors: `pkg/services/criteria.go` (Beyla-specific
    `BeylaDiscoveryConfig`, `survey`, `socket_apps`) plus
    `OBI/pkg/appolly/services/criteria.go`, `attr_glob.go`, `attr_regex.go`,
    `export.go`, `samplerconfig.go`, `custom_routes.go`.
  - Exporters: `OBI/pkg/export/otel/otelcfg/` (`config_metrics.go`,
    `config_traces.go`), `OBI/pkg/export/otel/perapp/decfg.go`,
    `OBI/pkg/export/prom/prom.go`, `OBI/pkg/export/feature.go`,
    `OBI/pkg/export/bucket.go`, `OBI/pkg/export/debug/debug.go`,
    `OBI/pkg/export/imetrics/`.
  - Attributes and decoration: `OBI/pkg/export/attributes/`,
    `OBI/pkg/transform/` (`k8s.go`, `routes.go`, `name_resolver.go`,
    `span_name_limiter.go`), `OBI/pkg/kube/kubeflags/`, `OBI/pkg/filter/`.
  - Runtime/language agents: `OBI/pkg/obi/config.go` (`NodeJSConfig`,
    `JavaConfig`, `HealthCheckConfig`, JVM/.NET runtime metrics).
- `docs/config-schema.json` is generated from these types by
  `cmd/beyla-schema` (`make generate-config-schema`). It is a corroborating
  index of key names, not a replacement for the source: it can lag the code,
  includes development-only keys, and its root has no `additionalProperties:
  false` (so it can't prove a key is unsupported).
- CLI and config-file handling is in `cmd/beyla/main.go`. The only flag is
  `-config`; `BEYLA_CONFIG_PATH` overrides it. Verify behavior in code; don't
  infer from help text.
- Binary startup order (`cmd/beyla/main.go`): `obi.CheckOSSupport` ->
  `flag.Parse` -> `loadConfig` -> `Config.Validate` -> log setup ->
  `obi.CheckOSCapabilities` (warns, or exits when `enforce_sys_caps` is true)
  -> `components.RunBeyla` (`pkg/components/beyla.go`).

## Routing by page family

### Top-level concept pages (`docs/sources/*.md`)

| Page | Primary source |
|---|---|
| `_index.md` | Supported-language/protocol/platform claims: `OBI/pkg/internal/goexec/gofile.go` (Go), `OBI/pkg/ebpf/common/`, `OBI/pkg/internal/ebpf/` (probes by language/protocol), `OBI/pkg/obi/os.go` (kernel) |
| `metrics.md` | `OBI/pkg/export/attributes/metric*.go`, `pkg/beyla/config_obi.go` (Beyla renames of `obi.*` metrics), `pkg/export/extraattributes/metric.go`, exporters in `OBI/pkg/export/otel/` and `OBI/pkg/export/prom/`, `pkg/export/prom/prom_proc.go` |
| `cardinality.md` | `OBI/pkg/transform/routes.go`, `span_name_limiter.go`, `pkg/beyla/config.go` (`Attributes`), `OBI/pkg/export/attributes/attr_defs.go` |
| `security.md` | `OBI/pkg/obi/os.go`, `OBI/pkg/ebpf/common/common.go` (lockdown, CAP_SYS_ADMIN probing), `charts/beyla/values.yaml` |
| `distributed-traces.md` | `OBI/pkg/config/ebpf_tracer.go` (`context_propagation`), `OBI/pkg/internal/ebpf/tpinjector/`, `OBI/pkg/ebpf/common/common.go` |
| `cilium-compatibility.md` | `OBI/pkg/ebpf/tcmanager/cilium_support.go`, `OBI/pkg/config/tcbackend.go`, `pkg/beyla/config.go` (`Validate`, `willUseTC`) |
| `requesttime.md` | `OBI/pkg/config/ebpf_tracer.go`, `OBI/pkg/export/attributes/` |
| `obi.md` | `go.mod`, `.gitmodules`, `pkg/beyla/config_obi.go` (what Beyla changes from OBI) |
| `beyla-dashboard.md` | Metric names: `OBI/pkg/export/attributes/metric.go`; dashboards aren't in this repo's source tree to verify beyond names |

### `configure/` reference pages

| Page | Primary source files |
|---|---|
| `options.md` | `pkg/beyla/config.go` (`Config`), `OBI/pkg/obi/config.go`, `cmd/beyla/main.go` |
| `example.md`, `resources/instrumenter-config.yml` | Check every key with the YAML-example method in `example-validation.md` |
| `service-discovery.md` | `pkg/services/criteria.go`, `OBI/pkg/appolly/services/criteria.go`, `attr_glob.go`, `attr_regex.go`, `OBI/pkg/appolly/discover/` |
| `export-data.md` | `OBI/pkg/export/otel/otelcfg/`, `OBI/pkg/export/prom/prom.go`, `OBI/pkg/export/feature.go`, `pkg/export/otel/grafana.go`, `pkg/beyla/config.go` (`normalizeConfig`) |
| `export-modes.md` | `OBI/pkg/appolly/services/export.go` (`exports`), `pkg/export/alloy/`, `resources/alloy-config.river` (Alloy, not Beyla, syntax) |
| `controlling-instrumentation.md` | `OBI/pkg/config/ebpf_tracer.go`, `payload_extraction.go`, `log_enricher.go`, `OBI/pkg/obi/config.go` |
| `tune-performance.md` | `OBI/pkg/config/ebpf_tracer.go`, `tcbackend.go`, `OBI/pkg/obi/config.go` (`DefaultConfig`) |
| `routes-decorator.md` | `OBI/pkg/transform/routes.go`, `OBI/pkg/appolly/services/custom_routes.go`, `pkg/beyla/config.go` (`DefaultConfig` routes override, `Validate` wildcard check) |
| `metrics-traces-attributes.md` | `OBI/pkg/export/attributes/attr_defs.go`, `attr_select.go`, `attr_selector.go`, `names/attrs.go`, `pkg/export/extraattributes/attr_defs.go`, `OBI/pkg/transform/k8s.go`, `pkg/beyla/config.go` (`Attributes`) |
| `filter-metrics-traces.md` | `OBI/pkg/filter/attribute.go`, `matcher.go` |
| `metrics-histograms.md` | `OBI/pkg/export/bucket.go`, `otelcfg/config_metrics.go`, `prom/prom.go` |
| `sample-traces.md` | `OBI/pkg/appolly/services/samplerconfig.go`, `otelcfg/config_traces.go` |
| `name-resolver.md` | `OBI/pkg/transform/name_resolver.go`, `pkg/beyla/config.go` (`DefaultConfig` sources override) |
| `internal-metrics-reporter.md` | `OBI/pkg/export/imetrics/`, `OBI/pkg/export/attributes/metric_internal.go`, `pkg/beyla/config.go` (`Validate` internal-metrics checks) |
| `language-agents.md` | `OBI/pkg/obi/config.go` (`NodeJSConfig`, `JavaConfig`), `OBI/pkg/internal/java/`, `OBI/pkg/internal/nodejs/` |
| `_index.md` | Navigation only; check links to config files only |

### `network/` pages

`network/config.md` -> `OBI/pkg/obi/network_cfg.go`, `OBI/pkg/export/feature.go`,
`OBI/pkg/filter/attribute.go` (`filter.network`), `pkg/beyla/config.go`
(`Validate` network exporter checks). Flow printer and agent behavior:
`OBI/pkg/internal/netolly/export/printer.go`, `OBI/pkg/netolly/agent/`.
Metric names: `pkg/beyla/config_obi.go` (`beyla.network.*`). `network/quickstart.md`,
`inter-az.md`, `asserts.md`: configs also check against `charts/beyla/values.yaml`
and `charts/beyla/templates/`. Stats (`stats.*`): `OBI/pkg/obi/stats_cfg.go`,
`OBI/pkg/internal/statsolly/`.

### `quickstart/` pages

Language pages check against `examples/quickstart/<language>/` (sample app
source only; the `docker run` / Beyla commands the pages print aren't stored
there, so verify them with the shell-command method in `example-validation.md`)
plus the config keys and env vars they print. `quickstart/kubernetes.md`
also checks against `charts/beyla/`, `examples/k8s/`, and `deployments/`.
Language-support statements: `OBI/pkg/internal/goexec/gofile.go`,
`OBI/pkg/internal/ebpf/` and the language-agent packages.

### `setup/` pages

| Page | Primary source |
|---|---|
| `standalone.md` | `cmd/beyla/main.go`, `contrib/beyla.service`, `contrib/beyla.env`, `contrib/beyla.yaml` |
| `docker.md` | `Dockerfile` (`FROM scratch`, `ENTRYPOINT ["/beyla"]`), `javaagent.Dockerfile`, `examples/` compose files |
| `kubernetes.md` | `charts/beyla/templates/` (daemon-set, configmap, cluster-role), `examples/k8s/`, `deployments/`, `cmd/k8s-cache/`, `k8scache.Dockerfile` |
| `kubernetes-helm.md`, `kubernetes-helm-appolly.md`, `kubernetes-helm-k8s-monitoring.md` | `charts/beyla/values.yaml`, `charts/beyla/templates/`, `charts/beyla/Chart.yaml`; the k8s-monitoring chart is a different repository |
| `helm-alloy.md` | Alloy's Helm chart and Alloy's `beyla.ebpf` component, neither in this repo. Beyla-side hooks only: `pkg/export/alloy/`, `Config.TracesReceiver`. Record anything else as an open question |

Chart and image defaults aren't binary defaults. The chart's `config.data`
(`attributes.kubernetes.enable: true`, `prometheus_export.port: 9090`,
`discovery.instrument: k8s_namespace "*"` for the `application` preset,
`contextPropagation.enabled`, `k8sCache.replicas: 0`) is rendered by
`charts/beyla/templates/configmap.yaml` and `daemon-set.yaml`; `contrib/beyla.yaml`
sets `ebpf.wakeup_len: 100` while the binary default is 500. `charts/beyla/README.md`
is generated from `values.yaml`; verify against `values.yaml`. Chart
`appVersion` is in `charts/beyla/Chart.yaml`.

### Other binaries

- `cmd/k8s-cache/` (Kubernetes metadata cache): config in
  `cmd/k8s-cache/cfg/config.go`; env vars use `BEYLA_K8S_CACHE_*`. The chart
  wires it through `k8sCache` and sets `BEYLA_KUBE_META_CACHE_ADDRESS` on the
  Beyla pod (`charts/beyla/templates/daemon-set.yaml`).
- `cmd/beyla-schema/` generates `docs/config-schema.json`.

### Experimental and undocumented

`pkg/webhook/` and `Config.Injector` (SDK injection) are marked experimental
and undocumented in `pkg/beyla/config.go`. Don't require documentation for
them; if a page does document them, verify as usual.

## OBI dependency and source availability

`go.mod` can replace `go.opentelemetry.io/obi` with `./.obi-src`. Inspect
`go.mod` and `git submodule status` to establish the version and whether that
submodule is checked out. If the replacement source is absent, check whether
the exact dependency source is available locally through the repository's
vendor or module setup. Do not fetch or substitute the latest upstream source
as if it were the version used by this checkout.

When the implementation needed to verify a claim isn't available locally,
record the claim as an open question and name the exact source or behavior that
must be inspected. Do not report a discrepancy or gap based only on a
different OBI version.

State of this checkout as observed on 2026-10-20 (re-check each time; it
changes with every OBI bump):

- `go.mod` requires `go.opentelemetry.io/obi v0.15.2` and replaces it with
  `./.obi-src`; `vendor/modules.txt` records the same replacement.
- `.obi-src` is a git submodule (`.gitmodules`) pinned to a commit but is
  **not checked out** (the directory is empty), so the pinned OBI source,
  including OBI's eBPF C code under `bpf/`, isn't available.
- `vendor/go.opentelemetry.io/obi/` is present and is what the checkout
  compiles against (`go build -mod vendor` in the `Makefile`). It contains Go
  source only (no `.c`/`.h` files), refreshed by `make vendor-obi`. Whether it
  matches the pinned submodule commit is **unverified**.
- Cite OBI behavior as `vendor/go.opentelemetry.io/obi/...` and say the claim
  depends on the vendored copy. When the claim is only about probe internals
  (what an eBPF program does in C), the vendored Go can show the Go-side
  setup and generated object names but not the C logic; record that as an open
  question naming OBI's `bpf/` directory at the pinned commit.
- OBI defaults in the vendor tree can be overridden at runtime by Beyla
  (`DefaultConfig` and `OverrideOBIGlobalConfig`, for example the `obi` vendor
  prefix becomes `beyla`). Never report a vendored default or name until you
  have checked those two functions.

## Runtime behavior and supported capabilities

- Follow configuration values into their consumers in `pkg/`, `internal/`,
  and the vendored OBI source, as applicable. Beyla's own pipeline code is in
  `pkg/internal/` and `pkg/export/`; OBI's is in
  `vendor/go.opentelemetry.io/obi/pkg/internal/` and `.../pkg/appolly/`.
- Kernel-facing behavior spans Go code and eBPF C code. Beyla's own `bpf/`
  directory holds only `survey_watcher` (plus compile flags); the probe C code lives in OBI (not
  checked out here). Check the Go-side gating (`OBI/pkg/obi/os.go`,
  `OBI/pkg/ebpf/common/common.go`) and state what you could not see.
- Use validation logic and tests to confirm accepted values, errors, and edge
  cases. Read the implementation under test before drawing broader conclusions.
- For deployment-specific defaults and behavior, inspect the relevant files
  under `charts/`, `deployments/`, and Dockerfiles. Separate a chart or image
  default from the binary's own default.
- For metrics and traces, trace the configured exporter through the
  implementation that constructs or emits the data. Confirm names, attributes,
  and semantics in source rather than assuming that a nearby documentation
  table or upstream OpenTelemetry convention describes Beyla's behavior.

## Evidence discipline

- Cite documentation lines for claims being reviewed and source lines for
  behavior that confirms or contradicts them.
- Open each cited source file and check context before including a citation.
- Prefer the effective runtime path over comments or struct tags alone when
  they disagree or when defaults are assembled across packages.
- Treat comments, tests, generated code, and deployment manifests as evidence
  for their specific scope; don't imply they establish more than they do.

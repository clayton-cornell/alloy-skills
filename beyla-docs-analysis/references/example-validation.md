# Example validation

Validate every example on the page the person will copy: YAML config, shell
commands, environment variables, and sample output. Findings follow the same
rule as everywhere else: cite the doc `file:line` of the example and the source
or tool output, and propose the corrected example text. `<skill>` is the
`beyla-docs-analysis` skill directory and `<beyla>` is the Beyla checkout.
`OBI/` means `vendor/go.opentelemetry.io/obi/` (write full paths in findings).

This skill is read-only. It never builds Beyla (`make`, `go build`, `docker
build`), never pulls images, and never starts containers on its own.

## A. YAML configuration examples

Why it matters: Beyla decodes YAML non-strictly (`yaml.Unmarshal` in `LoadConfig`,
`pkg/beyla/config.go`), so a misspelled or removed key doesn't fail; it is
silently ignored. A copied example can run "fine" and do nothing.

### Run the checker

```sh
python3 <skill>/scripts/check_yaml_examples.py <page.md> [<page2.md> ...] \
  --schema <beyla>/docs/config-schema.json [--json]
```

- Positional arguments: one or more Markdown files.
- `--schema PATH`: the generated JSON Schema (`docs/config-schema.json`,
  produced by `cmd/beyla-schema`).
- `--json`: machine-readable output instead of text.
- Exit code `0` means no problems, `1` means problems were found, `2` means a
  usage or tool error (bad path, unreadable schema). Treat `2` as a skipped
  check, not as "clean".
- For each fenced YAML block it prints the unknown keys and type problems. Run
  `--help` to confirm the exact options; if the script is absent, use the manual
  fallback below and list the script as a skipped check.

### What it can and can't catch

- It catches: YAML syntax errors, keys not present in the schema (the silent
  failure above), and values of the wrong type or enum where the schema says so
  (for example `traffic_control_backend`, `network.source`).
- Unknown-key detection is done by the checker, not by the schema. The schema's
  root and `$defs` have no `additionalProperties: false`, so schema validation
  alone would accept any key. The schema may also not cover every key (it is
  generated from Go types and can lag the code, and some maps accept free-form
  keys such as attribute selection or `extra_group_attributes`).
- Treat a checker hit as a lead, not a finding. Open the source, confirm the key
  is absent from the struct tags (`grep -rn 'yaml:"<key>"' pkg vendor/go.opentelemetry.io/obi/pkg`),
  then report it.
- Things it can't judge: whether the combination makes sense (for example an
  exporter is still required, see `Validate` in `pkg/beyla/config.go`), whether a
  documented default is right, deprecated-but-valid keys (check those against
  `accuracy-checklist.md` 1.4), and fragments. A block showing only a nested
  section (for example just `wakeup_len: 100` under a heading about `ebpf`) will
  be reported as an unknown top-level key; judge from context whether the page
  makes the nesting clear, and say so instead of reporting a false error.

### What isn't Beyla config

The checker skips, or you must treat separately:

- **Helm `values.yaml` snippets** (keys such as `image`, `preset`, `config.data`,
  `k8sCache`, `env`). Validate against `charts/beyla/values.yaml` and how
  `charts/beyla/templates/` uses them. Whatever sits under `config.data` is
  Beyla config; extract it and check it as Beyla config.
- **Kubernetes manifests** (`apiVersion`, `kind`). Check fields against
  `charts/beyla/templates/` and `examples/k8s/`; the Beyla config embedded in a
  ConfigMap `data:` string is Beyla config.
- **Docker Compose files.** Check against the `Dockerfile` entrypoint and the
  env var/config rules; Compose syntax itself is out of scope.
- **Alloy / River blocks** (` ```alloy `, `resources/alloy-config.river`). These
  are Alloy configuration, not Beyla. Verify only Beyla-side claims
  (`pkg/export/alloy/`); record Alloy component attributes as an open question
  naming the Alloy docs unless an Alloy checkout is supplied.
- **Other tools' configs** (Prometheus scrape config, OpenTelemetry Collector
  config): out of scope unless the page makes Beyla-specific claims in them.

### Manual fallback

When the checker isn't available:

1. Extract each ` ```yaml ` / ` ```yml ` block (the docs use both fences).
2. Syntax: `python3 -c 'import sys,yaml; list(yaml.safe_load_all(sys.stdin))' < block.yaml`
   (if PyYAML isn't installed, say so under Skipped checks and check indentation
   by eye).
3. Keys: for every key, resolve it with `jq` against the schema (for example
   `jq '."$defs".EBPFTracer.properties | has("wakeup_len")' docs/config-schema.json`)
   or against the struct tag. Walk nested keys one level at a time from the
   top-level properties (`jq -r '.properties | keys[]' docs/config-schema.json`).
4. Values: check the type, the enum, and the unit (durations as `5s`).
5. Selector keys under `discovery.instrument` (`open_ports`, `exe_path`,
   `languages`, `k8s_namespace`, ...): confirm against
   `OBI/pkg/appolly/services/attr_glob.go` (`GlobAttributes`) and
   `AllowedAttributeNames` in `OBI/pkg/appolly/services/criteria.go`.

Also check, for each example, that it doesn't use deprecated keys without a
note (`discovery.services`, `executable_name`, `otel_metrics_export.features`,
`prometheus_export.features`, `application_span`), and that `${VAR}` syntax
matches `pkg/config/env_replacer.go`.

## B. Shell commands and environment variables

- [ ] Every `BEYLA_*`, `OTEL_*` and `GRAFANA_CLOUD_*` variable: look up the tag
      (`accuracy-checklist.md` 1.2). An unknown variable is silently ignored.
- [ ] Beyla's only flag is `-config` (`cmd/beyla/main.go`); `BEYLA_CONFIG_PATH`
      overrides it. Any other flag is wrong.
- [ ] `docker run` flags: privileges and namespaces against the capability
      tables in `accuracy-checklist.md` section 4 and `charts/beyla/templates/daemon-set.yaml`
      (host PID, host network, privileged or capabilities). The image has no
      shell (`Dockerfile`, final stage `FROM scratch`, `ENTRYPOINT ["/beyla"]`).
- [ ] `helm` commands: every `--set` path must exist in
      `charts/beyla/values.yaml`; check the chart name and repo from
      `charts/beyla/Chart.yaml`; check that `--set` of a Beyla option goes under
      `config.data.` and not at the chart root.
- [ ] systemd and file paths: `contrib/beyla.service`, `contrib/beyla.env`,
      `contrib/beyla.yaml`.
- [ ] Image names, tags and URLs: record as "not verified" unless a file in the
      repo states them. Don't pull or query a registry.
- [ ] Never run the commands. Judge them against source; commands that need
      root, a cluster or a registry are out of scope for this check.

## C. Sample output blocks

Compare the field set and order, not the values. A sample generated by an older
version is wrong if the printer has since added, removed or reordered fields.

| Output | Printer | What to compare |
|---|---|---|
| `trace_printer: text` line | `printSpan` in `OBI/pkg/export/debug/debug.go` | Timestamp, duration pair, `type`/`subType`, status, method, path, route in parentheses, `peer as ...`, `host as ...`, `contentLen`, `responseLen`, `svc=[...]`, `traceparent=[...]` |
| `trace_printer: json` / `json_indent` | `serializeSpansJSON` in the same file | Field names come from the span struct's JSON encoding (`Span` in `OBI/pkg/appolly/app/request/span.go`); a doc sample with fields the struct doesn't have is stale |
| `trace_printer: counter` | `counterPrinter` | `Processed N requests` |
| Network flow lines (`network.print_flows`) | `printFlow` in `OBI/pkg/internal/netolly/export/printer.go` | `network_flow:` prefix, `transport=`, `<prefix>.ip=` (prefix is `beyla` at runtime, see `OverrideOBIGlobalConfig`), `iface=`, `iface_direction=`, `src.address`, `dst.address`, `src.name`, `dst.name`, `src.port`, `dst.port`, then metadata |
| Stats output (`stats.print_stats`) | `OBI/pkg/internal/statsolly/export/printer.go` | Same method |
| Log lines (`level=... msg=...`) | The `slog` call | Message literal, level, key names; Beyla's startup lines are in `cmd/beyla/main.go` |
| Metric exposition samples (`# TYPE ...`) | Metric definitions | Name, unit suffix, labels; `accuracy-checklist.md` section 3 |

Steps: locate the printer, read the format string or struct fields, list the
fields of the sample, diff both ways, and propose a corrected sample built from
the printer's actual fields. If you can't produce a faithful value (for
example a trace ID), mark it as a placeholder in your proposal and say it's
illustrative.

## D. Optional runtime verification

Only if the person supplies a Beyla binary or container image built from this
checkout. This skill never builds Beyla and never pulls images on its own. The
person must also agree to running it: eBPF needs privileges (`CAP_BPF`,
`CAP_PERFMON`, and the others listed in `OBI/pkg/obi/os.go`), BTF and kernel
5.8 or newer (4.18 on RHEL-based), and in containers `--privileged` or the
equivalent capabilities, `--pid=host`. The development machine this skill was
written for runs Linux with BTF and Docker, so runtime checks are feasible when
a build is provided.

When a build is supplied, useful read-only checks are:

- Run it with the page's example config and confirm it loads (`configuration
  loaded` line) and, with `log_config: yaml`, inspect the effective config it
  prints (`BEYLA_LOG_CONFIG`; implemented in `logConfig`, `cmd/beyla/main.go`)
  to confirm a default or a key is picked up.
- Set `trace_printer: text` or `network.print_flows` to capture real sample
  output and compare it with the doc.

State exactly which binary or image (version and revision from the `Grafana
Beyla` startup line) the result is from, and report what you ran.

If none is supplied, list this under **Skipped checks**, in the report's
dedicated section and not under Open questions:

> Runtime verification skipped: no Beyla binary/image from this checkout provided.

Also list, when they apply: `check_yaml_examples.py` not found or exited with
`2`; PyYAML missing for the manual YAML syntax check; `jq` missing; Alloy or
Kubernetes-Monitoring chart claims not checkable because those repositories
weren't supplied.

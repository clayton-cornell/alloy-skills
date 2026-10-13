# Alloy component docs audit: possible code issues

Compiled: 2026-10-13
Repo: [grafana/alloy]
Companion to: [overview.md](overview.md) (the audit catalog) and [closed-items.md](closed-items.md) (fixed and closed items).

Possible source bugs the docs audit surfaced, written up for discussion with the dev team. Each entry states the problem, where to look and a possible fix. It is not a full analysis: the developer who picks it up will do the deep dive.

Item numbers match [overview.md](overview.md). An item gets an entry here only after it has been checked against the source and judged to be a real issue. "Not run" means the behaviour was read from the code, not reproduced by running Alloy.

## Index

| Item | Component | Issue | Severity | Reproduced |
|---|---|---|---|---|
| [1](#item-1-prometheusexporterkafka-instance-ignored-with-one-uri-kafka_uris-not-validated) | `prometheus.exporter.kafka` | `instance` is ignored when there is one URI; `kafka_uris` is required but tagged optional | Low | Not run |
| [2](#item-2-prometheusexportermongodb-enable_profile-has-no-effect) | `prometheus.exporter.mongodb` | `enable_profile = true` does not produce profile metrics | Medium | Not run; upstream condition unconfirmed |
| [3](#item-3-prometheusexportermssql-connection_name-never-becomes-a-metric-label) | `prometheus.exporter.mssql` | `connection_name` enables the `up` and scrape-duration metrics but never becomes a label | Low | Not run; pinned library commit unconfirmed |
| [4](#item-4-prometheusexportercloudwatch-static-block-accepts-period-length-and-delay-but-ignores-them) | `prometheus.exporter.cloudwatch` | `static` block accepts `period`, `length` and `delay` but ignores them | Low | Not run; pinned YACE version unconfirmed |
| [8](#item-8-prometheusexporterconsul-server-without-a-scheme-gives-instance-the-value-unknown) | `prometheus.exporter.consul` | A `server` address without a scheme sets `instance` to `unknown` | Medium | Not run; Go parsing behaviour from documentation |
| [9](#item-9-prometheusexportergithub-github_rate_limit-has-no-alloy-default-so-github-app-re-auth-never-triggers) | `prometheus.exporter.github` | `github_rate_limit` defaults to `0` instead of `15000`, so GitHub App re-authentication never triggers | Medium | Not run; upstream code path not read |
| [10](#item-10-prometheusexportergithub-a-partial-github-app-configuration-is-silently-ignored) | `prometheus.exporter.github` | Setting only some of the three GitHub App arguments is silently ignored | Low | Not run |
| [12](#item-12-prometheusecho-an-unknown-format-is-accepted-and-falls-back-to-text) | `prometheus.echo` | An unknown `format` is accepted and falls back to `text` | Low | Not run |

---

## Items

### Item 1: `prometheus.exporter.kafka`: `instance` ignored with one URI; `kafka_uris` not validated

**A. `instance` is silently ignored when `kafka_uris` has exactly one entry**
- **What happens:** the `instance` label is always the first URI, whatever `instance` is set to. With two or more URIs, `instance` is required and is used.
- **Why:** both `Config.InstanceKey()` and `customizeTarget` return `KafkaURIs[0]` for a single URI without looking at `Instance`.
- **Where:** `internal/static/integrations/kafka_exporter/kafka_exporter.go:155-163`; `internal/component/prometheus/exporter/kafka/kafka.go:94-103`.
- **Repro (not run):** `kafka_uris = ["broker:9092"]` and `instance = "my-kafka"`. Expected label `my-kafka`; from the code it will be `broker:9092`.
- **Open question for the devs:** is this intended ("one URI means automatic instance") or a bug? The reference doc calls the first URI the *default* `instance`, which suggests an override should work.
- **Possible fix:** use `Instance` when it is set, for any number of URIs. Or keep the behaviour and say in the docs that `instance` has no effect with one URI.

**B. `kafka_uris` is required in practice but tagged `optional`**
- **What happens:** omitting it is not caught at config decode or in `Validate()`. The component fails when it is built, with `empty kafka_uris provided`. It does not crash.
- **Where:** tag at `kafka.go:35`; the check is in `kafka_exporter.go:177-179`.
- **Possible fix:** drop `optional` from the tag, or add a length check to `Validate()`. Configs that omit it already fail, so this is not a breaking change. Optionally also guard the `[0]` index in `customizeTarget`.
- **Severity:** cosmetic. The error message is clear, it just surfaces late.

**Docs:** the reference doc already marks `kafka_uris` as required, which matches actual behaviour. No change needed for B. A is unaddressed in the docs.

**Checked:** by reading the code, on `grafana/alloy` branch `docs/component-export-receiver` (commit `b7a1698`), not on `main`. Not run. The kafka source was not diffed against `main`.

**Related:** [#7335] (docs part 06).

---

### Item 2: `prometheus.exporter.mongodb`: `enable_profile` has no effect

- **What happens:** setting `enable_profile = true` should add profile metrics. From the code it does not, and there is no warning.
- **Why (high level):** the upstream exporter only collects profile metrics when its `ProfileTimeTS` option is non-zero. Alloy never sets that option, so it stays `0`.
- **Where:** Alloy builds the exporter options in `internal/static/integrations/mongodb_exporter/mongodb_exporter.go:96-118`. It passes `EnableProfile` (`:114`) and no `ProfileTimeTS`. The component argument is at `internal/component/prometheus/exporter/mongodb/mongodb.go:48`.
- **Upstream:** `github.com/percona/mongodb_exporter` v0.47.2 (pinned in `go.mod`). `ProfileTimeTS int` exists in its `Opts`, and its CLI flag `collector.profile-time-ts` sets it (default 30 in an upstream PR diff; version not confirmed).
- **Not confirmed:** the exact condition in upstream `exporter/exporter.go` (around line 227) that requires `ProfileTimeTS != 0`. That file was not read, so the dev should confirm it first. If the condition differs, the cause above may be incomplete.
- **Repro (not run):** run with `enable_profile = true` against a MongoDB that has profiling enabled, and check for profile metrics. None are expected.
- **Possible fix:** expose a `profile_time_ts` argument, or set a non-zero default when building the options. The upstream CLI default (30) is the obvious value, once confirmed.
- **Docs:** the reference doc says "Enables collecting profile metrics." It is left as is on purpose and becomes accurate once this is fixed.
- **Checked:** Alloy side by reading the code, on the current `alloy` checkout. Not run.

**Related:** [#7335] (docs part 06).

---

### Item 3: `prometheus.exporter.mssql`: `connection_name` never becomes a metric label

- **What happens:** the reference doc says `connection_name` is "used as a label in uptime metrics". From the code, a non-empty name makes the exporter emit the synthetic `up` and `scrape_duration_seconds` metrics (they are skipped when the name is empty, which is the default) and adds the name to log messages. It does not add a label.
- **Why (high level):** Alloy passes the name plus an empty but non-nil `prometheus.Labels{}` to `sql_exporter.NewTarget`. The library only builds the target label from the name when that map is `nil`, so with a non-nil map no label is created.
- **Where:** Alloy: `internal/static/integrations/mssql/sql_exporter.go:129-137` (name at `:131`, label map at `:137`). Library: `NewTarget` and `Collect` in `github.com/burningalchemist/sql_exporter` `target.go`.
- **If fixed:** the library passes the same constant labels to the synthetic metrics and to `NewCollector`, so the label would probably appear on all of the exporter's metrics, not only the uptime ones. The collector code was not read.
- **Likely also needed (unconfirmed):** passing `nil` may not be enough on its own. The label name comes from `config.TargetLabel`, which the library uses but whose default and assignment were not read. If it is empty, the label name would be empty and invalid. Worth checking when fixing.
- **Not confirmed:** the library was read from its public `master` on 2026-10-13, not from the commit Alloy pins (`e19ac2aef3d7`, dated 2026-09-28, which could not be retrieved). The `master` file includes a mutex change merged 2026-04-10, so it is at least from the same period.
- **Repro (not run):** set `connection_name` and scrape the mssql exporter. `up` and `scrape_duration_seconds` should appear with no label for the name. With `connection_name` unset, neither metric should appear.
- **Possible fix:** pass `nil` (or a map that already contains the label), and make sure the label name is set. Alternatively, drop or redefine the argument.
- **Impact:** low. The `instance` label is the host from the connection string (`sql_exporter.go:78-85`), so connections to different hosts can still be told apart. Different connection strings to the same host cannot.
- **Docs:** the doc at HEAD describes a label and does not mention that the argument is what enables `up` and `scrape_duration_seconds`. If the source is fixed, the doc should describe the label. The part-06 branch was not checked.
- **Checked:** by reading the Alloy source and the upstream `target.go`. Not run.

**Related:** [#7335] (docs part 06).

---

### Item 4: `prometheus.exporter.cloudwatch`: `static` block accepts `period`, `length` and `delay` but ignores them

- **What happens:** a `static` block accepts `period`, `length` and `delay` without an error or warning, and they have no effect. The same three attributes do work on `discovery` and `custom_namespace` blocks. `period` and `length` set inside a `metric` block still work.
- **Why (high level):** the conversion for static jobs never reads the job-level values. It calls `toYACEMetrics(sj.Metrics, 0, 0)`, while the discovery and custom-namespace conversions pass their job values through. The YACE `Static` type has no job-level fields to carry them, at least at the version checked.
- **Where:** `internal/component/prometheus/exporter/cloudwatch/config.go`: attributes at `:86-88`; `toYACEStaticJob` at `:302-332`, with the zero values at `:330`; discovery and custom-namespace pass job values at `:355` and `:381`.
- **Precedent in the code:** `nil_to_zero` on the same block had the same problem and is patched inside `toYACEStaticJob` (`:311-321`). The comment at `:89-93` says such fields should either be removed from Alloy in a major release or contributed to YACE.
- **Not confirmed:** the YACE types were read at upstream `v0.60.0`, where `Static` has no job-level metric fields and `validateStaticJob` does not inherit them. Alloy pins a fork of YACE based on v0.64.x (`replace` in `go.mod`), which was not read.
- **Repro (not run):** a unit test on `toYACEStaticJob` with `Period` set on the job and a metric with no period. The metric's `Period` should come out as `0`, so YACE applies its default.
- **Possible fix:** for `period` and `length`, pass `sj.Period` and `sj.Length` to `toYACEMetrics`, which already applies them to metrics that do not set their own. `delay` cannot be applied that way, because YACE ignores delay for static jobs at the version checked. Remove or deprecate it, or log a warning when it is set. Or leave the behaviour and document it.
- **Impact:** low. A configuration that sets them is accepted and silently uses YACE defaults.
- **Docs:** the `static` table at HEAD does not list these attributes. The part-04 PR description says that branch documents the current behaviour in two places: a no-effect note in the `static` section and an inheritance sentence in the `metric` section. That text was not read (the commit that adds it could not be retrieved). If the source is fixed, revert both.
- **Checked:** by reading `config.go` in the `alloy` checkout and the YACE `v0.60.0` config types. Not run.

**Related:** [#7281] (docs part 04).

---

### Item 8: `prometheus.exporter.consul`: `server` without a scheme gives `instance` the value `unknown`

- **What happens:** with `server = "localhost:8500"` (no `http://`), every target from the component gets `instance="unknown"`. The exporter still connects, so metrics flow, but the label is wrong. The reference doc uses `localhost:8500` as an example address, and the default is `"http://localhost:8500"`.
- **Why (high level):** the instance label comes from `url.Parse(server).Host`. Go parses `host:port` without a scheme as scheme `host` and opaque `port`, so `Host` is empty. The empty key then hits the generic fallback that substitutes `unknown`.
- **Where:** `internal/static/integrations/consul_exporter/consul_exporter.go:60-65` (`InstanceKey`); the fallback at `internal/component/prometheus/exporter/exporter.go:93-94`. The consul component uses the plain `exporter.New` builder (`internal/component/prometheus/exporter/consul/consul.go:20`), so nothing overrides the label.
- **Upstream behaviour:** the upstream consul exporter accepts scheme-less addresses (its README example is `--consul.server=172.17.0.1:8500`), and an older upstream revision prepends `http://` when `://` is missing. So the connection works and only the instance key is wrong.
- **Likely related (unverified):** an IP address with a port, such as `10.0.0.5:8500`, should fail to parse in Go because a scheme must start with a letter. That would make the component fail to build with `could not parse url`, rather than label wrongly. Worth including when testing.
- **Not confirmed:** Go's parsing result is taken from Go's own closed issue (golang/go#12585) and library documentation, not from running it here; Go is not installed where this was checked. Earlier notes record a scratch Go program (2026-10-01) that confirmed the `unknown` label for `consul.example.com:8500`, `localhost:8500` and a bare hostname; that was not re-run. The exact code of upstream `consul_exporter` v0.8.0 (the version Alloy pins) was not read, only an older revision.
- **Repro (not run):** set `server = "localhost:8500"` and look at the `instance` label on the exported targets. `unknown` is expected. With `"http://localhost:8500"` it should be `localhost:8500`.
- **Possible fix:** normalise the address before deriving the instance key, as the upstream exporter does: if it does not contain `://`, prepend `http://`. Requiring a scheme in the docs would only work around it, since the exporter itself accepts the address.
- **Impact:** medium. A documented form of the address produces a meaningless `instance` label, which breaks per-server grouping and alerting and makes several consul exporters indistinguishable by `instance`.
- **Docs:** the doc at HEAD (`main`) shows `localhost:8500` as an example address. On the unmerged part-04 branch (head `c5dc82d`) the consul topic says to set `server` to an address that includes a scheme, for example `https://consul.example.com:8500` (commit `4a0e35c`). That wording is a workaround for this issue and should be revisited if the source is fixed. Whether part-04 still shows `localhost:8500` in the arguments table was not checked.
- **Checked:** by reading the Alloy source. Not run.

**Related:** [#7281] (docs part 04).

---

### Item 9: `prometheus.exporter.github`: `github_rate_limit` has no Alloy default, so GitHub App re-auth never triggers

- **What happens:** when `github_rate_limit` is not set, Alloy passes `0`, not the intended default of `15000`. This threshold is what makes the exporter fetch a new GitHub App token when the remaining rate limit gets low. With `0` that condition can never be met, so the token is not refreshed unless the user sets the argument explicitly.
- **Why (high level):** the component's `DefaultArguments` only sets `api_url`. The static-mode config gets `15000` from `DefaultConfig` through `UnmarshalYAML`. The Alloy component path does not, so the field keeps its zero value.
- **Where:** component `internal/component/prometheus/exporter/github/github.go:32-34` (`DefaultArguments`, only `APIURL`) and `:65` (value passed through). Integration `internal/static/integrations/github_exporter/github_exporter.go:18-21` (`DefaultConfig` with `GitHubRateLimit: 15000`), `:57-58` (`*c = DefaultConfig`), and `:116` (`SetGitHubRateLimit`).
- **Upstream:** the `githubexporter/github-exporter` README documents a default of 15,000 and says a new token is generated when the value is below the threshold. Earlier notes trace the check in `github-exporter@v1.3.1`, `exporter/prometheus.go`: `Collect()` calls `isTokenExpired()`, which tests `limit < e.Config.GitHubRateLimit()`. With `0` that is never true, so `SetAPITokenFromGitHubApp()` never runs. That trace was not re-read here.
- **Repro (not run):** decode an Alloy config without `github_rate_limit` and check `GitHubRateLimit`. It should be `15000` and is expected to be `0`. A long-running exporter using GitHub App auth is the end-to-end check.
- **Possible fix:** add `GitHubRateLimit: github_exporter.DefaultConfig.GitHubRateLimit` to `DefaultArguments`.
- **Impact:** medium. The failure is silent and only shows on long-running exporters.
- **Docs:** the reference doc already says the default is `15000`, which is the intended value. Leave it as is, because documenting `0` would describe the bug as intended behaviour.
- **Checked:** by reading the Alloy source. Not run.

**Related:** [#7284] (docs part 05).

---

### Item 10: `prometheus.exporter.github`: a partial GitHub App configuration is silently ignored

- **What happens:** GitHub App authentication only turns on when all three of `github_app_id`, `github_app_installation_id` and `github_app_key_path` are set. If only one or two are set, there is no error and no log message:
  - with no token, the exporter starts unauthenticated and gets GitHub's low unauthenticated rate limit;
  - with a token, the token is used and the App arguments are ignored. The doc says token and App authentication cannot be combined, but this case is not rejected.
- **Why (high level):** the code builds a single boolean from all three values being non-zero. A partial set makes it false, and the authentication chain has no final branch for "unauthenticated", so nothing is reported. No `Validate()` exists on the component or the integration.
- **Where:** `internal/static/integrations/github_exporter/github_exporter.go`: the guard at `:101-102`, the mutual-exclusion check at `:104-107`, the App branch at `:110`, and the token branches at `:122-131`. The component (`internal/component/prometheus/exporter/github/github.go`) defines no `Validate()`.
- **Repro (not run):** set only `github_app_id` (or two of the three) with no token. The component should start without error and, with debug logging, without an authentication-method line.
- **Possible fix:** add a `Validate()` that returns an error when some but not all of the three App arguments are set, and ideally when App arguments are combined with a token. Or at minimum log a warning.
- **Impact:** low. It only affects a misconfigured or half-finished block, but the result looks accepted and silently degrades.
- **Docs:** the doc tells users to set all three arguments for App authentication and does not mention the partial case. The existing health section covers invalid configuration in general, so a doc note is optional.
- **Checked:** by reading the Alloy source. Not run.

**Related:** [#7284] (docs part 05).

---

### Item 12: `prometheus.echo`: an unknown `format` is accepted and falls back to `text`

- **What happens:** `format` accepts any string. Anything other than `text`, `openmetrics` or empty is accepted without an error, the component stays healthy, and each time metrics are committed it logs `unknown format, using text` and writes text output.
- **Why (high level):** nothing validates the value. `Update()` stores the arguments and always returns `nil`, `New()` only fails if `Update()` fails, and the component has no `Validate()`. The output code has an explicit `default` branch that warns and uses text.
- **Where:** `internal/component/prometheus/echo/echo.go`: `Update()` at `:83-89`, `New()` at `:65-71`, the format `switch` at `:234-242`.
- **Open question for the devs:** is the lenient fall-through intended? The explicit `default` branch with a warning suggests it may be deliberate, but the reference doc says `format` "Must be `text` or `openmetrics`".
- **Repro (not run):** set `format = "json"`. The component should build and report healthy, and the log should show the warning on each commit. No test in `echo_test.go` covers an unknown value.
- **Possible fix:** validate the value in a `Validate()` method (rejected at config load) or in `Update()` (returns an error, so the component is unhealthy). Or keep the behaviour and make the doc say that an unknown value falls back to `text`.
- **Impact:** low. A misspelled value gives text output and a repeated warning, with no health signal. `prometheus.echo` is a debugging component.
- **Docs:** the reference doc now describes the current behaviour (working tree, uncommitted): an unrecognised `format` logs a warning and uses `text`, and does not make the component unhealthy. If validation is added, revisit the note under `format` and the Component health wording. A wrong-typed argument already makes the component unhealthy through the normal evaluation path, so only the unrecognised-value case is affected.
- **Checked:** by reading the source and tests. Not run.

**Related:** [#7270] (docs part 03).

---

[grafana/alloy]: https://github.com/grafana/alloy
[#7270]: https://github.com/grafana/alloy/pull/7270
[#7281]: https://github.com/grafana/alloy/pull/7281
[#7284]: https://github.com/grafana/alloy/pull/7284
[#7335]: https://github.com/grafana/alloy/pull/7335

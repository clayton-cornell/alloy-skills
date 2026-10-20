<!-- Condensed from writers-toolkit/docs/sources/write/style-guide/word-list/index.md, via the alloy-docs-analysis copy. -->

# Grafana word list

The canonical Grafana-wide "which term to use" reference. Most entries already have a dedicated Vale rule, so the `make vale` run (`references/style-consistency-vale.md`) catches them. The gap this file fills is the few entries with no dedicated rule, which need a manual check.

To decide whether a term is Vale-covered, check `WordList.yml`'s substitution table (second table below), not only for a standalone rule file named after the term. Its coverage is broader than a rule-file scan suggests.

| Term | Guidance | Vale rule |
|---|---|---|
| agentless | Don't use. Use "no-collector" for deployments without a collector. | `Agentless.yml` — Vale-covered |
| alert rule vs. alerting rule | "Alert rule" is the Grafana Alerting feature (Grafana-managed or data-source-managed). "Alerting rule" is the Prometheus/Mimir/Loki concept. Don't confuse them. | None — check manually |
| Best practices | Use as the title for conceptual topics covering best-practice guidance. | None |
| CHANGELOG | All caps when naming the file or making a general reference. Match the file's actual capitalization when citing a specific file. | `CHANGELOG.yml` — Vale-covered |
| data source (not datasource) | "Data source" is two words. Use "data source plugin," not "data-source plugin." | `WordList.yml` (`"data-?source": "data source"`) |
| dataset | "Dataset," not "data set." | `WordList.yml` |
| dialog box | "Dialog box," not "modal" or "dialog." | `DialogBox.yml` — Vale-covered |
| drop-down | A modifier only ("drop-down menu"), never a standalone noun; never "dropdown." | `DropDown.yml` — Vale-covered |
| easy / simple | Try eliminating. What's simple to the writer may not be simple to the reader. | `Simple.yml` — Vale-covered |
| end-to-end | "End-to-end," not "e2e" or "E2E." | `EndToEnd.yml` — Vale-covered |
| hover over | "Hover over," not "hold the pointer over" or "point to." | None — check manually |
| kebab case | "Kebab case" (dashes between lowercase words), not "dash case." | None — check manually |
| menu icon | "Menu icon," not "hamburger menu" or "kebab menu." | `WordList.yml` |
| meta-monitoring | Hyphenated, not "metamonitoring" or "meta monitoring." | `MetaMonitoring.yml` — Vale-covered |
| no-collector | Use for collector-less deployments instead of "agentless." | `Agentless.yml` — Vale-covered |
| Node Exporter vs. `node_exporter` | "Node Exporter" for the product, code-formatted `node_exporter` for the binary. | `PrometheusExporters.yml` — Vale-covered |
| OK, okay | Avoid in technical docs except when quoting a UI or an HTTP status. | `OK.yml` — Vale-covered |
| quickstart | No hyphen, as noun or adjective. | `Quickstart.yml` — Vale-covered |
| React | "React," not "React.js" or "ReactJS." | `React.yml` — Vale-covered |
| README | All caps for the file or a general reference. | `README.yml` — Vale-covered |
| self-managed | "Self-managed," not "self-hosted," "on-prem," or "on-premise," for Grafana deployment methods. | `SelfManaged.yml` — Vale-covered |
| single pane of glass | Marketing-only. In technical docs use "single interface" or "unified interface." | None — check manually |
| SQL | "A SQL Server analysis" (pronounced "sequel," Microsoft SQL Server) vs. "an SQL error" (any other context). | `SQL.yml` — Vale-covered |
| time series vs. timeseries | "Time series" as a noun, "time-series" as an adjective, never "timeseries." | `WordList.yml` |

**No dedicated Vale rule** (confirmed against rule files and the `WordList.yml` table when this file was written): `alert rule` vs. `alerting rule`, `Best practices`, `hover over`, `kebab case`, `single pane of glass`. Check just these five manually. A Beyla page is unlikely to use most of them. Verify with a text search, and paste the result, before reporting an absence.

## `WordList.yml` general substitution table

`WordList.yml` (`writers-toolkit/vale/Grafana/styles/Grafana/WordList.yml`, `level: warning`) is a general preferred-spelling rule with over 100 entries. Those most likely to matter in Beyla docs:

| Wrong | Right |
|---|---|
| `otel` | `OTel` (see the OpenTelemetry note below) |
| `otlp` | `OTLP` |
| `grafana` | `Grafana` |
| `loki`, `prometheus` (except after `kube-`), `promtail` (except after `lambda-`) | `Loki`, `Prometheus`, `Promtail` |
| `the Grafana Agent` | `Grafana Agent` (no leading article) |
| `regexp?` / `regex[ep]?s` | `regular expression(s)` |
| `url` / `urls` | `URL` / `URLs` |
| `blacklist` / `whitelist` | `blocklist` / `allowlist` |
| `data-?source(s)` | `data source(s)` |
| `timeseries` | `time series` / `time-series` |
| `open-source` | `open source` (no hyphen as a noun) |
| `in order to` | `to` |

See the source file for the full list.

**Scope caveat.** The rule applies to prose, not code. Don't flag a configuration key or flag such as `exe_path_regexp` or an environment variable as if it were the prose word "regex." Vale respects code fences and inline code through its own settings. Apply the same judgment when checking manually.

**OpenTelemetry note.** The `otel` → `OTel` substitution only fires on the lowercase token. The org style prefers the full "OpenTelemetry" in prose, and "OTel" is not preferred. When a finding involves this term, propose "OpenTelemetry" and not "OTel." See `references/style-consistency-terminology.md`.

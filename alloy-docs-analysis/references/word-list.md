<!-- Condensed from writers-toolkit/docs/sources/write/style-guide/word-list/index.md. -->

# Grafana word list

The canonical Grafana-wide "which term to use" reference — same role as
`frontmatter-schema.md` and `shortcode-schema.md` play for their subjects.
Most entries already have a dedicated Vale rule (so `make vale`/Step 5 item 1
already catches them) — the real gap this file fills is the handful of
entries below with no dedicated rule, which need manual checking against
this file specifically. **When determining whether a term is Vale-covered,
check `WordList.yml`'s own substitution table directly** (see that table
below), not just for a standalone rule file named after the term — its
coverage is broader than a rule-file scan alone would suggest.

| Term | Guidance | Vale rule |
|---|---|---|
| agentless | Don't use — Alloy replaced Grafana Agent, so avoid agent-based terminology. Use "no-collector" instead. | `Agentless.yml` — already Vale-covered |
| alert rule vs. alerting rule | "Alert rule" = the Grafana Alerting feature (Grafana-managed or data-source-managed). "Alerting rule" = the Prometheus/Mimir/Loki concept. Don't confuse the two. | No dedicated rule — check manually |
| Best practices | Use as the title for conceptual topics covering best-practice guidance. | No dedicated rule |
| CHANGELOG | All caps when naming a file or making a general reference; match the actual file's capitalization when referencing a specific file. | `CHANGELOG.yml` — already Vale-covered |
| data source vs. datasource | Use "data source" (two words) for the noun, not "datasource." Use "data source plugin," not "data-source plugin" (no hyphen, unlike most compound adjectives). | **Covered — `WordList.yml`'s substitution table** (`"data-?source": "data source"`) |
| dataset | Use "dataset," not "data set." | **Covered — `WordList.yml`** (`"data[- ]?sets": "datasets"`) |
| dialog box | Use "dialog box," not "modal" or "dialog." | `DialogBox.yml` — already Vale-covered |
| drop-down | Use "drop-down" (not "dropdown"/"drop down") as a modifier only (e.g. "drop-down menu"), not as a standalone noun. | `DropDown.yml` — already Vale-covered |
| easy / simple | Try eliminating — what's simple to the writer may not be simple to the reader. | `Simple.yml` — already Vale-covered |
| end-to-end | Use "end-to-end," not "e2e"/"E2E." | `EndToEnd.yml` — already Vale-covered |
| hover over | Use "hover over," not "hold the pointer over" or "point to." | No dedicated rule — check manually |
| kebab case | Use "kebab case" (the naming convention with dashes between lowercase words), not "dash case." | No dedicated rule — check manually |
| menu icon | Use "menu icon," not "hamburger menu" or "kebab menu." | **Covered — `WordList.yml`** (`"(?:hamburger menu|kebab menu)": "menu icon"`) |
| meta-monitoring | Use "meta-monitoring," not "metamonitoring"/"meta monitoring." | `MetaMonitoring.yml` — already Vale-covered |
| no-collector | Use for collector-less deployments, instead of "agentless." | `Agentless.yml` — already Vale-covered (same rule family as "agentless") |
| Node Exporter vs. `node_exporter` | Capitalize both words ("Node Exporter") when referring to the product; use the literal code-formatted `node_exporter` when referring to the tool/binary. | `PrometheusExporters.yml` — already Vale-covered |
| OK, okay | Avoid in technical docs (too informal) except when quoting a UI or an HTTP status/code. | `OK.yml` — already Vale-covered |
| quickstart | No hyphen, whether used as noun ("a quickstart") or adjective ("quickstart guide"). | `Quickstart.yml` — already Vale-covered |
| React | Use "React," not "React.js"/"ReactJS." | `React.yml` — already Vale-covered |
| README | All caps when naming a file or making a general reference; match the actual file's capitalization when referencing a specific file. | `README.yml` — already Vale-covered |
| self-managed | Use "self-managed," not "self-hosted"/"on-prem"/"on-premise," for Grafana deployment methods. | `SelfManaged.yml` — already Vale-covered |
| single pane of glass | Marketing-only term. In technical docs use "single interface" or "unified interface" instead. | No dedicated rule — check manually |
| SQL | Article depends on pronunciation: "a SQL Server analysis" (pronounced "sequel," Microsoft SQL Server specifically) vs. "an SQL error" (pronounced "ess-cue-el," any other context). | `SQL.yml` — already Vale-covered |
| time series vs. timeseries | Use "time series" (two words) as a noun, "time-series" (hyphenated) as an adjective — never "timeseries" as one word. | **Covered — `WordList.yml`** (`"timeseries": "time series\|time-series"`) |

**Genuinely no dedicated Vale rule, confirmed against both standalone rule
files and `WordList.yml`'s full substitution table** — these five are the
real, narrower gap: `alert rule` vs. `alerting rule`, `Best practices`,
`hover over`, `kebab case`, `single pane of glass`.

## `WordList.yml`'s general substitution table (not previously in this file)

Beyond the word-list *page*'s prose entries above, `WordList.yml` itself
(`writers-toolkit/vale/Grafana/styles/Grafana/WordList.yml`) is a much larger,
general term-substitution rule (`level: warning`) — dozens of preferred
spellings/capitalizations, most generic, but several directly relevant to
Alloy given how much it discusses OTel/Prometheus/Loki:

| Wrong | Right |
|---|---|
| `otel` | `OTel` |
| `otlp` | `OTLP` |
| `grafana` | `Grafana` |
| `loki` | `Loki` |
| `prometheus` (except after `kube-`) | `Prometheus` |
| `promtail` (except after `lambda-`) | `Promtail` |
| `the Grafana Agent` | `Grafana Agent` (no leading article) — relevant to any migration-guide prose comparing Alloy to its predecessor |
| `regexp?`/`regex[ep]?s` | `regular expression`/`regular expressions` |
| `url`/`urls` | `URL`/`URLs` |
| `blacklist`/`whitelist` (and inflections) | `blocklist`/`allowlist` |
| `data-?source(s)` | `data source(s)` |
| `data[- ]?set(s)` | `dataset(s)` |
| `timeseries` | `time series` / `time-series` |
| `(?:hamburger menu\|kebab menu)` | `menu icon` |
| `open-source` | `open source` (no hyphen as a noun) |
| `in order to` | `to` |

This is not the full table — see the source file directly for the complete
list (over 100 entries). **Critical scoping caveat**: this substitution rule
applies to *prose*, not code-formatted content — don't flag a legitimate
Alloy config attribute or CLI flag literally named `regex` (e.g.
`discovery.relabel`'s `regex` argument) as if it were the prose word
"regex" needing expansion to "regular expression." Vale itself already
respects code-fence/inline-code boundaries via `.vale.ini`'s `TokenIgnores`
setting; apply the same judgment manually if running this check without
Vale.

## Alloy-specific note (not in the original source file)

**The "agentless" → "no-collector" rule is directly about Alloy's own product
history** — Alloy is Grafana Agent's replacement, so any lingering
agent-based terminology in Alloy docs ("agentless deployment," "agent-based
collection," etc.) is exactly the pattern this rule exists to catch. This one
already has a dedicated Vale rule, so `make vale` should catch it — but it's
worth knowing the *reason* the rule exists when explaining a finding, since
it's Alloy-specific context a generic Vale message wouldn't supply.

"Data source" (not "datasource") is the term most likely to actually appear
in Alloy docs among this file's entries, given how often Alloy components
interact with Grafana data sources (Prometheus, Loki, and so on) in
cross-references and integration guides — and it's Vale-automated via
`WordList.yml`'s substitution table.

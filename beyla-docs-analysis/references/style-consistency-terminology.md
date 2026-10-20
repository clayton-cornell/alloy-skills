<!-- Written for Beyla. Replaces the Alloy skill's cascade-variable checks: the Beyla docs use no `{{< param >}}`. -->

# Style consistency: terminology, version strings, and sibling comparison

The Beyla docs use no `{{< param >}}` shortcode, no `cascade` variables, and no shared partials. Product names and versions are written literally in prose, so consistency has to be checked by reading. Beyla has no term or dictionary file of its own. Vale and the Grafana word list are the only sources (`references/word-list.md`).

## Product and brand naming

Check the page against these rules, and cite the Vale rule when one exists:

- **Grafana Beyla, then Beyla.** Use the long name "Grafana Beyla" in the page overview or first mention, and "Beyla" in the body. Flag a page that never uses the long name in its opening, or one that repeats "Grafana Beyla" throughout.
- **Grafana Alloy, then Alloy.** Same pattern. Say "Grafana Alloy" on first mention and "Alloy" afterwards. Don't use "the Grafana Alloy agent," "Agent," or "Grafana Agent" for Alloy.
- **OpenTelemetry, not "OTel" or "OTEL."** Prose uses "OpenTelemetry." Env var names (`OTEL_EXPORTER_OTLP_ENDPOINT`), YAML keys, and code stay as written. Observed in prose in the baseline: "Grafana Alloy as your OTEL collector" (`configure/sample-traces.md:26`), "Grafana Cloud OTEL endpoint" (`configure/export-data.md:24`), the heading "Exclude otel instrumented services" (`configure/service-discovery.md:429`), and an "OTEL Metric" table header (`configure/metrics-traces-attributes.md:346`). Propose "OpenTelemetry" in each. The Vale word list substitutes `otel` → `OTel`, but the org style prefers "OpenTelemetry" in prose, so propose the full name.
- **Kubernetes, not "K8s."** Prose uses "Kubernetes." `k8s.*` attribute names, `kubernetes.io` and `*.k8s.io` URLs, and `k8s_*` option names are code and stay. Capitalize Kubernetes object types (Pod, DaemonSet, Deployment) (`Grafana.Kubernetes`).
- **Grafana Cloud in full.** Never "Cloud" on its own for the product.
- **OpenTelemetry eBPF Instrumentation (OBI).** Spell out "OpenTelemetry eBPF Instrumentation" on first use in a page, with "(OBI)" immediately after, and use "OBI" afterwards. `obi.md` defines the topic. Check that other pages that mention OBI (for example `configure/options.md`) use the same name, and flag a bare "OBI" with no definition on a page that never introduces it. Don't flag "Beyla" vs. "OBI" in `obi.md` as inconsistent, because that page compares them on purpose.
- **eBPF capitalization.** "eBPF" with a lowercase `e` and uppercase `BPF`, even at the start of a sentence (rewrite the sentence rather than capitalize it). `ebpf` as a YAML key is code and stays. Flag "EBPF," "Ebpf," and "ebPF" in prose. Whether a Vale rule enforces this is unverified.
- **Signal order: metrics, logs, traces, profiles.** When a sentence lists signals, use this order (`references/style-guide.md`). Don't reorder a list where order carries meaning, or an option's accepted values.
- **Other products** follow the word list and Vale vendor rules (`Prometheus`, `Loki`, `Tempo`, `Mimir`, `Pyroscope`, `Grafana Cloud Application Observability`). Use a name exactly as the product's own docs spell it.

If a term has several spellings across the page, report the page's most common spelling as the likely intended form and say how many instances deviate.

## Hardcoded version strings

Beyla docs hard-code versions in prose and examples: for example, kernel claims such as "Linux 6.6 adds support for TCX" (`configure/tune-performance.md`), and Go, Beyla, or image versions in commands. There's no mechanism to substitute them. Flag a hardcoded version that will rot:

- a Beyla, OpenTelemetry, Go, Helm chart, or container image version;
- a minimum kernel or distribution version;
- a "current," "latest," or "new in" claim that depends on a release.

For each one, say what could go stale, and **mark the value as needing source verification** (see the SKILL accuracy step: check the code, `go.mod`, the release notes, or the Helm chart). Don't propose a replacement value from memory. Propose either the verified value, or wording that avoids the version (for example, "a recent Linux kernel" only when the source supports it). Don't flag a version that is a fixed historical fact, or a version inside sample command output (for example, a dated log line).

Timestamps and IP addresses in sample output aren't version strings.

## Cross-topic sibling comparison (judgment, manual)

Pick siblings and compare. **Siblings must come from the same subdirectory as the page**: `configure/`, `quickstart/`, `setup/`, `network/`, or top-level pages. A `quickstart/` page isn't a sibling of a `configure/` page. Each directory has its own conventions, so a difference between families is expected and not a finding.

Rules:

- **Need at least two real siblings** that do the same thing before calling it a convention. One sibling is an anecdote. A corpus-wide count isn't by itself a convention, and the repo's developer documentation outranks a tally of pages when they disagree.
- Read the siblings in full. Don't compare against titles or a snippet.
- Compare: heading order and naming for equivalent sections; admonition placement; example formatting; the option table header and cell conventions (`references/style-consistency-manual-checklist.md`); terminology for the same concept; voice and tense.
- Name the siblings you compared against, so the finding is checkable. Report cross-topic findings as a separate subsection from Vale output, because they're judgment calls.
- Propose which convention should win (usually the more common one across siblings, unless the minority version is clearly better) and the exact corrected text, heading, or order. Don't just say "these are inconsistent."
- A within-family inconsistency (one `quickstart/` page lacking a section its siblings share) is a real finding. Don't build a rigid template across families.

**Reading siblings.** Read siblings from the working tree by default. If the human says documentation work is split across open branches, ask which branch owns the siblings and read them from there (`git show <branch>:docs/sources/<path>.md`, read-only). A stale working-tree sibling can manufacture a false "that isn't a convention" finding. If you can't establish which copy is current, say the comparison is unverified. Don't infer merge state from branch ancestry.

## Spelling and the dictionary

Beyla has no dictionary file. For `Grafana.Spelling` hits on legitimate terms (for example `instrumentable`, `qdisc`, `CIDRs`, or any product term that is genuinely correct, as can happen with `eBPF`, `Beyla`, `OBI`, or `cgroup` if a run flags them), propose a `writers-toolkit` dictionary entry instead of a doc edit. The method and entry formats are in `references/style-consistency-vale.md`.

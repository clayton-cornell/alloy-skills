# Analysis: docs/sources/troubleshoot/debug.md

**Regenerated 2026-07-29** to replace a prior report lost in a cleanup pass.
This run applies the corrected log-message citation rule
(`accuracy-checklist-other.md`, "A grep hit is not itself a confirmed
citation") — every source file referenced below was opened and read
directly by this run, not inferred from a prior grep result or from an
earlier version of this report.

## Summary

`troubleshoot/debug.md` is a task/reference hybrid: it documents the Alloy
UI's debugging pages, then a "Common log messages" reference table
presenting exact `msg="..."` strings as real log output, then clustering
troubleshooting guidance. The UI-description portions weren't independently
verified against the actual UI (out of scope for source-code verification).
The "Common log messages" section is the highest-risk part of this page —
it makes specific, falsifiable claims about exact log text — and is where
this run concentrated its verification effort. Overall health: **three
confirmed inaccuracies (including one log-level mismatch in the cluster
section, added in a follow-up pass), three open questions, and one
confirmed stale link** in an otherwise well-structured page.

## Audience

Persona: **Operator** (someone running Alloy in production, debugging a live
issue), with secondary **Practitioner** signals (walkthrough-style UI
descriptions assume no prior familiarity with the Alloy UI). Evidence: the
page opens with an imperative troubleshooting flow ("Follow these steps to
debug issues"), assumes the reader already has Alloy running and reachable,
and the log-message reference table is clearly aimed at someone comparing
real output against expected output — a Learner wouldn't have real log
output to compare yet. No mismatch with the page's position under
`troubleshoot/`. What's missing for this reader: the log-message table's
accuracy problems (below) directly undermine the Operator use case this
page is designed for — an Operator grepping their own logs for
`"starting server"` to confirm the HTTP service came up would find no match
at all, and might wrongly conclude something is broken.

## Accuracy issues

All log-message claims below are from the page's "Component lifecycle
messages" subsection. Method: extracted every `msg="..."` string, searched
by exact text, then **opened and read the cited file directly** before
reporting anything as confirmed (per the corrected rule) — a search hit
alone is not treated as a citation.

| Doc claim | Source reality | Citation | Status |
|---|---|---|---|
| `level=info msg="starting server"` / `msg="starting server" addr=localhost:8080` | The HTTP service's actual startup log is `s.log.Info("now listening for http traffic", "addr", s.opts.HTTPListenAddr)` | `internal/service/http/http.go` (`Run` method) — read directly, confirmed no `"starting server"` string exists anywhere in this file | **Inaccurate** — propose replacing both lines with `level=info msg="now listening for http traffic" addr=localhost:8080` |
| `level=info msg="terminating server"` | No explicit shutdown log line exists in the HTTP service at all — shutdown goes through `defer func() { _ = srv.Shutdown(ctx) }()` with no accompanying log call | `internal/service/http/http.go` — read directly, no `"terminating"` string of any kind in this file | **Inaccurate** — propose removing this line, or replacing it with a real message if one exists elsewhere and is found (none located in this run) |
| `level=info msg="started scheduled components"` (appears 3 times across the subsection) | No such string exists in the scheduler. The closest real analogs: `f.log.Info("scheduling loaded components and services")` (present participle, different wording) in the Run loop, and the scheduler's own per-node messages `s.logger.Error("node exited with error", "node", id, "err", err)` / `s.logger.Info("node exited without error", "node", id)` | `internal/runtime/alloy.go` (`Run` method, `case <-f.loadFinished:` branch) and `internal/runtime/internal/controller/scheduler.go` — both read directly | **Inaccurate** — propose replacing with `level=info msg="scheduling loaded components and services"` where the doc means the initial-load event, and removing the implication that a single "started scheduled components" message exists |
| `level=warn msg="task shutdown is taking longer than expected"` | Confirmed exact match, no field arguments in source (matches doc) | `internal/runtime/internal/controller/scheduler.go`, `(*task).Stop()` — read directly: `t.opts.logger.Warn("task shutdown is taking longer than expected")` | **Confirmed accurate** |
| `level=warn msg="the discovery.process component only works on linux; enabling it otherwise will do nothing"` | Confirmed exact match, including level | `internal/component/discovery/process/process_stub.go` — read directly: `opts.Logger.Warn("the discovery.process component only works on linux; enabling it otherwise will do nothing")` | **Confirmed accurate** |
| `level=info msg="starting controller"` | Not found verbatim in either of the two most likely files. `internal/runtime/alloy.go` has `f.log.Debug("Running alloy controller")` (Debug level, different text) and `internal/alloycli/cmd_run.go` has `slogger.Info("Alloy is starting")` (different text, and it's the CLI layer, not the controller) | `internal/runtime/alloy.go`, `internal/alloycli/cmd_run.go` — both read directly, neither contains this exact string | **Open question** — a plausible real message exists nearby (`"Running alloy controller"`) but doesn't match at either text or log level (Debug vs. the doc's Info); not confident enough in a single substitution to propose one without a broader search of `internal/runtime/` this run didn't complete |
| `level=info msg="configuration loaded"` | Not found in either `internal/runtime/module.go` or `internal/runtime/alloy.go` (the two most likely locations for a config-load log line) — no broader repo-wide grep was run this session to rule out other locations | Files read directly, string absent from both | **Open question** — genuinely unresolved; do not report as confirmed-inaccurate without a full-repo search, per the corrected citation rule |
| `level=info msg="module content loaded"` | **This is the corrected finding.** A prior version of this report cited `internal/runtime/internal/testcomponents/module/module.go:65` as the confirmed-inaccurate source of this claim. **That file does not exist anywhere in this repository** — no `testcomponents` directory exists at all, confirmed by direct directory search. The prior citation was fabricated (accepted from an unverified grep result). `internal/runtime/module.go` (the real module-handling file) was read directly and does not contain this string. | `internal/runtime/module.go` — read directly, string absent; no other candidate file located this run | **Open question**, not "Inaccurate" — its true status (a paraphrase of some other real message, or a genuinely invented one) is unknown, not merely uncertain. Do not re-cite the previous file:line under any circumstance; it was never real. |
| `level=info msg="config reloaded"` (elsewhere on the page, "Component updates" group) | Confirmed exact match | `internal/service/http/http.go` — read directly: `s.log.Info("config reloaded")` in the `/-/reload` handler | **Confirmed accurate** (re-verified directly this run, not carried over from the prior report) |

**Cluster-related messages** ("starting cluster node," "discovered peers,"
minimum-cluster-size messages, and similar under "Cluster operation
messages") were **not verified in this version of the report** — correctly,
at the time, per `accuracy-checklist-other.md`'s then-current scope limit.
**That scope limit has since been found to be wrong** and was corrected in
the skill's reference file: nearly all of these messages are directly
verifiable in `internal/service/cluster/` and
`internal/service/cluster/discovery/`, not in the external `ckit` module as
previously assumed. A follow-up run against this same page, applying the
corrected scope, confirmed the text and level of every cluster message
except one: **`"discovered peers"` is documented as `level=info`, but the
real call (`internal/service/cluster/cluster.go`'s `getRandomPeers`) is
`s.log.Debug("discovered peers", ...)`** — a genuine, confirmed level-mismatch
accuracy issue, propose changing the doc's `level=info` to `level=debug` on
that line. Every other cluster message checked (`"starting cluster node"`,
both "failed to..." bootstrap/reconnect messages, `"failed to refresh/
rejoin list of peers"`, `"rejoining peers"`, all three "minimum cluster
size" messages, `"using provided peers for discovery"`, `"found an IP
cluster join address"`, `"received DNS query response"`, `"failed to
resolve provided join address"`) matched source exactly on both text and
level — this section of the page is otherwise solid.

## Completeness gaps

Not run this session. `troubleshoot/debug.md` is a conceptual/task page, not
a component or CLI reference page with a struct to walk exhaustively — a
completeness check here would mean comparing the UI-page descriptions
against the actual UI, or comparing the log-message list against every
`slog` call in the runtime, neither of which this run attempted. Flagging
this explicitly as **not checked**, rather than silently omitting the
section.

## Style & consistency

### Vale findings

**Skipped** — `make vale` requires Docker/Podman, neither confirmed
available in this session. See "Skipped checks" below.

### Manual style checklist findings

No violations found on inspection: present tense/active voice throughout,
sentence-case headings, admonitions used for genuinely supplementary
content (not overused), no gerund-form headings, no bare hardcoded
`Alloy`/`Grafana Alloy` in prose (confirmed — every occurrence checked uses
`{{< param "PRODUCT_NAME" >}}` or `{{% param "FULL_PRODUCT_NAME" %}}`
correctly, including in the H1 heading, which correctly uses percent
delimiters per Check C).

### Link findings

**Confirmed stale link**, consistent with the now-systemic pattern
documented in `style-consistency.md`'s Link check:

```
[secret]: ../../get-started/configuration-syntax/expressions/types_and_values/#secrets
```

The real current path is `../../get-started/expressions/types_and_values/#secrets`
(the `configuration-syntax/` segment no longer exists in the site's
structure; `expressions/` sits directly under `get-started/`). This is the
**fourth** independently-confirmed file with this exact stale prefix. Propose:

```
[secret]: ../../get-started/expressions/types_and_values/#secrets
```

### Cross-topic inconsistencies

Not run this session — no comparable sibling `troubleshoot/*.md` page was
checked against for structural consistency.

## Skipped checks

- Automated Vale linting (`make vale`) — Docker/Podman availability not
  confirmed in this session; not attempted rather than assumed.
- Completeness check — not applicable in the usual sense for this page type;
  see "Completeness gaps" above.
- Cross-topic comparison — not run.
- Full repo-wide search for `"configuration loaded"` and a real analog for
  `"module content loaded"` / `"starting controller"` — only the most
  likely candidate files were read directly; a broader `grep -rn` pass
  across `internal/` was not completed this run. These three remain
  legitimately open, not resolved.

## Open questions

- `"starting controller"` — no exact match found; closest candidates
  (`"Running alloy controller"` at Debug level, `"Alloy is starting"` in the
  CLI layer) don't match on text or level. Needs a broader search before
  proposing a fix.
- `"configuration loaded"` — not found in the two most likely files; status
  genuinely unresolved.
- `"module content loaded"` — not found in the one real candidate file
  checked this run. **The specific file:line this claim was previously
  attributed to does not exist and should not be cited again.** Needs a
  broader search (or acceptance that it may not exist in any form) before
  this can move to either "confirmed accurate" or "confirmed inaccurate."

Once the fixes from this report are actually applied (e.g. merged in a PR),
this page's `review_date` frontmatter field should be updated to the merge
date, in `YYYY-MM-DD` format.

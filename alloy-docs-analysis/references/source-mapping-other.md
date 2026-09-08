# Mapping doc topics to source: everything else

## Non-CLI, non-component, non-syntax, non-packaging pages

Truly generic conceptual pages (e.g. `introduction/why-alloy.md`) with no
dedicated source subsystem of their own. Verify individual claims against
whichever of `source-mapping-components.md`, `source-mapping-cli.md`,
`source-mapping-syntax.md`, or `source-mapping-packaging.md` actually applies
rather than treating everything here as unverifiable — most "generic" pages
still make component, CLI, syntax, or packaging claims in passing and should
be checked against the matching file, not waved through as prose.

## Log message text (troubleshoot/debug.md and similar)

Genuinely scattered — no single package owns all log output. Likely
locations by subsystem, confirmed by direct inspection rather than guessed:
HTTP server events → `internal/service/http/http.go`; component
start/stop/scheduling events →
`internal/runtime/internal/controller/scheduler.go`; component-specific
warnings → the relevant `internal/component/.../*.go` file (e.g.
`discovery.process`'s Linux-only warning lives in
`internal/component/discovery/process/process_stub.go`); clustering messages
→ likely the external `github.com/grafana/ckit` module (imported in
`cmd_run.go`), not this repo. See
`references/accuracy-checklist-other.md`'s "Log-message-text checks" section
for the verification method — confirmed both accurate matches and confirmed
mismatches on a first pass, so this is worth real, not perfunctory, checking.

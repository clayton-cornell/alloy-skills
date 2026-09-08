# Accuracy checklist: CLI reference pages (reference/cli/*.md)

See `references/source-mapping-cli.md` for where each fact lives in
`internal/alloycli/cmd_<name>.go`. Checklist:

- [ ] Flag name in the doc matches the string literal passed as the second
      argument to its `pflag` registration call (`StringVar`/`BoolVar`/
      `IntVar`/`DurationVar`/`StringSliceVar`/`Var`) exactly.
- [ ] Default value stated in the doc matches the corresponding field's value
      in the `new<Name>()` constructor's struct literal — not just the zero
      value assumption from the type.
- [ ] Allowed-value enums for flags backed by a custom type (e.g.
      `--stability.level`) match that type's own source (e.g.
      `featuregate.AllowedValues()`), mapped by meaning per the same
      hyphenation caveat as component stability badges.
- [ ] **Every flag registered via a deprecation helper (e.g.
      `addDeprecatedFlags()`) is listed in the doc's "Deprecated flags"
      section.** Read the helper's full list, not just the doc's existing
      list — a helper deprecating N flags with only N-1 documented is a real,
      already-confirmed failure mode (see `references/source-mapping-cli.md`).
      This is the single highest-value CLI check; don't skip it even under
      time pressure.
- [ ] Windows-only or platform-gated flags (e.g. `--windows.priority`, gated
      by `runtime.GOOS == "windows"` in source) are documented as
      platform-specific in the doc, not presented as universally available.

## What NOT to attempt without more source access

`reference/cli/otel.md`'s flags come from the external
`go.opentelemetry.io/collector/otelcol` module, not this repo's own `pflag`
registrations (see `references/source-mapping-cli.md`'s special case). If the
external module's source isn't inspectable, say so in "Open questions" rather
than fabricating a verification. Same caution for the non-Alloy-specific
environment variables in `environment-variables.md` (`GODEBUG`, `GOGC`,
`GOMAXPROCS`, `GOTRACEBACK`) — verify those against Go's own documentation,
not by searching this repo for source that isn't there.

## Grepping flag registrations: watch for multi-line calls

Confirmed real in `cmd_run.go`: several `pflag` registrations are split
across two lines, e.g.

```go
fset.
	StringVar(&r.clusterTLSCAPath, "cluster.tls-ca-path", r.clusterTLSCAPath, "...")
```

with `fset.` on its own line and the actual `StringVar(...)` call (and the
flag's string-literal name) on the next line. A single-line grep pattern
like `fset\..*Var` won't match these — the method call and its arguments
never appear on the same line, so the flag name inside is invisible to a
line-based search. Confirmed real consequence: this is exactly the pattern
behind several `--cluster.tls-*` flags, which a naive grep can silently skip
without any error — it just returns fewer matches than there are real
registrations, which looks like a clean result rather than a gap. Don't
trust a `grep fset.*Var` (or similar) count as complete without checking for
this. Use `grep -A 1 'fset\.$'` to also capture the line immediately after a
bare `fset.` line, or just read `mountRunFlags` (or the equivalent function
in another `cmd_<name>.go`) directly rather than relying on a single-line
pattern match when confirming the full set of registered flags.

## Changelog drift

For CLI flags with recent changes, use
`references/accuracy-checklist-components.md`'s "Changelog drift checks"
section — the method and overlap warning are identical, just scoped by flag
name instead of component name; not duplicated here.

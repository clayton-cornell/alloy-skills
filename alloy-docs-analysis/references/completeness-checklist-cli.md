# Completeness checklist: CLI reference pages (reference/cli/*.md)

Different method, since there's no `Arguments` struct — see
`references/source-mapping-cli.md`.

1. Open the relevant `internal/alloycli/cmd_<name>.go` and read the full
   `mount*Flags`-style function top to bottom.
2. List every flag registered there, including ones registered through a
   separate deprecation helper (e.g. `addDeprecatedFlags()`) — don't stop at
   the main flag-mounting function if a helper adds more.
3. Confirm each appears in the doc's flag list. **Flags added via a
   deprecation helper must appear specifically in the doc's "Deprecated
   flags" section, not just anywhere** — a flag that's deprecated in source
   but undocumented, or documented as if it were a normal active flag, is a
   completeness gap either way. Confirmed real instance:
   `cluster.use-discovery-v1` is deprecated via `cmd_run.go`'s
   `addDeprecatedFlags()` but doesn't appear anywhere in `run.md`.
4. Platform-gated flags (wrapped in a `runtime.GOOS == "..."` check) still
   need documenting — confirm they're present, not skipped because they're
   conditional.

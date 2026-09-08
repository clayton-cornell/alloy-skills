# Mapping doc topics to source: component reference pages

Path pattern in docs: `docs/sources/reference/components/<namespace>/<component.name>.md`
Path pattern in source: `internal/component/<namespace>/<...>/<last-segment>/<last-segment>.go`

Verified example:
- Doc: `docs/sources/reference/components/otelcol/otelcol.processor.transform.md`
- Source: `internal/component/otelcol/processor/transform/transform.go`

General rule: drop the leading namespace repeated in the component name
(`otelcol.processor.transform` → `otelcol/processor/transform`), and the final
segment names both the directory and the primary `.go` file. This holds across
`discovery.*`, `loki.*`, `prometheus.*`, `otelcol.*`, `pyroscope.*`, `local.*`,
`remote.*`, `faro.*`, `database_observability.*`. If a component wraps an
upstream OTel Collector component (common under `otelcol.exporter.*` and
`otelcol.receiver.*`), there will also be an import of the matching
`opentelemetry-collector-contrib/...` package — check that import for the
*actual* default values and validation logic, since the Alloy wrapper often just
maps config through via `mapstructure`.

Some directories nest further (e.g., `internal/component/otelcol/processor/resourcedetection/internal/<provider>/config.go`
for `otelcol.processor.resourcedetection`'s per-provider blocks) — if the flat
mapping doesn't resolve, use `Filesystem:search_files` with the component's last
name segment as the pattern before giving up.

## Where the facts actually live in a component's `.go` file

- **Component name, stability level**: the `component.Register(component.Registration{...})`
  call — `Name` and `Stability` fields. `Stability` is the source of truth for
  whether a doc's experimental/beta/GA badge is current.
- **Arguments (attributes and blocks)**: the `Arguments` struct. Each field's
  `alloy:"..."` tag gives the exact documented name, whether it's `attr` or
  `block`, and whether it's `optional`. No `optional` in the tag means required.
- **Defaults**: the `DefaultArguments` var and/or `SetToDefault()` method. If
  absent, the default comes from the wrapped upstream OTel component's
  `CreateDefaultConfig()` — trace the import.
- **Exported fields**: the `Exports` type referenced in `component.Registration`
  (often a shared type like `otelcol.ConsumerExports`, not redefined per
  component — check the shared type once, not per topic).
- **Enum/allowed values**: custom types with an `UnmarshalText` method (like
  `ContextID` above) — the `switch` statement inside is the exhaustive list.

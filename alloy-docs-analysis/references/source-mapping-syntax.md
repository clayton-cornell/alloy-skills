# Mapping doc topics to source: core syntax/language pages

Covers `get-started/syntax.md`, `get-started/expressions/*.md`, and
`reference/stdlib/*.md`. Different subsystem from components/CLI entirely:
the grammar and standard library live in the top-level `syntax/` directory,
which is its own separate Go module (has its own `go.mod`/`go.sum`), not
under `internal/`.

## Where each claim type lives

| Doc page / claim | Source |
|---|---|
| Identifier rules ("letters, digits, underscores," "can't start with a digit," Unicode support) | `syntax/scanner/identifier.go` + `syntax/scanner/scanner.go` (`isLetter`/`isDigit`/`scanIdentifier`) |
| Comment syntax (`//`, `/* */`) | `syntax/scanner/scanner.go` (`scanComment`) |
| String quoting rules (double-quote required, single-quote rejected, backtick raw strings) | `syntax/scanner/scanner.go`'s `Scan()` — the `'\''` case explicitly errors "illegal single-quoted string; use double quotes" |
| Terminator/newline-insertion rules | `syntax/scanner/scanner.go`'s `insertTerm` logic (genuinely intricate — the doc's simplified summary is an appropriate abstraction, not something to expand into full lexer-state detail) |
| Block/attribute/label parsing rules | `syntax/parser/parser.go` and `syntax/parser/internal.go`; `syntax/parser/testdata/*.alloy` (including files literally named `attribute_names.alloy`, `block_names.alloy`, `commas.alloy`) are executable ground-truth fixtures for valid/invalid syntax — treat these as authoritative examples, not just source to read |
| `alloy fmt` formatting behavior | `syntax/printer/printer.go`; `syntax/printer/testdata/*.in`/`*.expect` pairs are exact before/after fixtures |
| Expression evaluation, types, operators | `syntax/internal/value/`, `syntax/typecheck/`, `syntax/vm/` |
| Secret type behavior (referenced from `troubleshoot/debug.md`'s "secret" note and `types_and_values.md`) | `syntax/alloytypes/secret.go` |
| Standard library functions (`reference/stdlib/<namespace>.md`) | `syntax/internal/stdlib/stdlib.go` — clean 1:1 mapping confirmed: `array.md` ↔ the `array` map, `sys.md` ↔ the `sys` map, `encoding.md` ↔ the `encoding` map, `string.md` ↔ the `str` map, `convert.md` ↔ the `convert` map, `file.md` ↔ the `file` map; `coalesce.md`/`constants.md`/`json_path.md` ↔ individual top-level identifiers |

## Stdlib deprecation and experimental status — same pattern as CLI flags

`stdlib.go` defines two maps that are the stdlib equivalent of the CLI's
`addDeprecatedFlags()` pattern (see `references/source-mapping-cli.md`) —
check both the same way:

- **`ExperimentalIdentifiers`**: currently `array.combine_maps` and
  `array.group_by`. Confirmed both are correctly marked with the
  `{{< docs/shared lookup="stability/experimental_feature.md" ...>}}`
  shortcode in `array.md` as of this check — clean, no bug found here, but
  re-verify on every run since this map can grow.
- **`DeprecatedIdentifiers`**: bare `env`, `nonsensitive`, `concat`,
  `json_decode`, `yaml_decode`, `base64_decode`, `format`, `join`, `replace`,
  `split`, `to_lower`, `to_upper`, `trim`, `trim_prefix`, `trim_suffix`,
  `trim_space` — deprecated in favor of their namespaced equivalents
  (`sys.env`, `convert.nonsensitive`, `array.concat`, `encoding.from_json`,
  etc.). Check that the docs don't present a deprecated bare name as the
  primary/only way to call a function, and that a namespaced replacement page
  exists and is what's actually documented (confirmed correct for `concat` →
  `array.concat`, which has an `aliases` entry redirecting from the old
  `./concat/` path).

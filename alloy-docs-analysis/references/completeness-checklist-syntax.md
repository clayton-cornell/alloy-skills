# Completeness checklist: syntax/language and stdlib pages (get-started/syntax.md, expressions/*, reference/stdlib/*.md)

1. For stdlib specifically: open `syntax/internal/stdlib/stdlib.go` and list
   every key across all the namespace maps (`array`, `sys`, `encoding`,
   `str`, `convert`, `file`) plus top-level `Identifiers` entries
   (`constants`, `coalesce`, `json_path`, `groupBy` etc.).
2. Confirm each has a corresponding doc entry in `reference/stdlib/<namespace>.md`.
3. Cross-check `ExperimentalIdentifiers` and `DeprecatedIdentifiers` — same
   principle as the CLI deprecated-flags check: a function present in one of
   these maps but not correctly reflected in its doc page (missing
   experimental marker, or documented under a deprecated bare name instead of
   its namespaced replacement) is a completeness/accuracy gap, not a nit.
4. For the parser/scanner/printer (no equivalent "list of identifiers" to
   diff against) — completeness here means: does `get-started/syntax.md`
   cover every top-level EBNF production documented in
   `syntax/scanner/scanner.go`'s own EBNF comment block? That comment is
   itself a complete grammar summary written by the source's own maintainers
   — a good checklist to diff the doc against directly.

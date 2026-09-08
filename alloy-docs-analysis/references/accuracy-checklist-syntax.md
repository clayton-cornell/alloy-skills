# Accuracy checklist: syntax/language and stdlib pages (get-started/syntax.md, expressions/*, reference/stdlib/*.md)

See `references/source-mapping-syntax.md` for where each claim type lives in
the `syntax/` module.

- [ ] Identifier/comment/string-quoting/terminator claims match
      `syntax/scanner/scanner.go` and `identifier.go` — these are
      well-isolated, pure functions (`isLetter`, `isDigit`,
      `scanIdentifier`), cheap to actually verify rather than assume.
- [ ] Block/attribute/label parsing claims match `syntax/parser/`. Prefer
      cross-checking against the executable fixtures in
      `syntax/parser/testdata/*.alloy` and `syntax/printer/testdata/*.in`/
      `*.expect` over just reading the parser source — they're exact,
      already-agreed-upon ground truth.
- [ ] Every stdlib function documented in `reference/stdlib/<namespace>.md`
      exists in the matching map in `syntax/internal/stdlib/stdlib.go`, with
      matching argument count/order/behavior.
- [ ] **Every identifier in `stdlib.go`'s `ExperimentalIdentifiers` map is
      marked experimental in its doc page** (the `{{< docs/shared
      lookup="stability/experimental_feature.md" ...>}}` shortcode, per the
      pattern confirmed correct for `array.combine_maps`/`array.group_by`).
      Same class of check as the CLI deprecated-flags one — don't skip it
      just because it happened to be clean the first time it was checked.
- [ ] Deprecated bare stdlib names (`stdlib.go`'s `DeprecatedIdentifiers` map)
      aren't presented as the primary way to call a function in current docs
      — the namespaced replacement should be what's actually documented.

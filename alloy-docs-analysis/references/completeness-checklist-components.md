# Completeness checklist: component reference pages

Goal: find things in source that a reader would need but the doc doesn't
mention. Starting list — expand as patterns emerge.

## Method

1. Open the `Arguments` struct (and any nested block structs) in full.
2. List every field with an `alloy:"..."` tag.
3. For each, confirm it appears somewhere in the doc's arguments/blocks tables.
4. Anything present in source but absent from the doc is a gap — note the field
   name, type, whether required/optional, and where it should logically go in
   the doc's existing structure (don't just say "add it somewhere").
5. **When a `block`-tagged field's type isn't defined in the same file as
   `Arguments`, follow it into its own package before concluding anything.**
   A `grep` scoped to the primary `args.go`-equivalent file, or a search for
   `<TypeName>.Arguments` in that same file, will miss this — the type
   itself lives elsewhere and needs a separate lookup (`find`/`grep` for the
   type's own package, then read that file directly). **Confirmed real,
   high-value case**: `pyroscope.ebpf`'s `Arguments` struct has
   `DebugInfoArguments debuginfo.Arguments \`alloy:"debug_info,block,optional"\``
   — a real, user-facing block whose type is defined in a completely separate
   package, `internal/component/pyroscope/write/debuginfo` (`common.go`),
   not anywhere in the `ebpf` package itself. `pyroscope.ebpf.md` was found
   to be missing this block entirely, while its own "Blocks" section
   actively (and incorrectly) states "`pyroscope.ebpf` doesn't support any
   blocks." This is the same general cross-package-tracing principle as the
   wrapped-upstream-OTel-defaults case elsewhere in this skill, just within
   the same repo instead of across a vendored module boundary — the extra
   hop to find the real struct is a search step, never a reason to skip the
   check or assume a block doesn't exist because it isn't in the obvious
   file. This pattern generalizes: any block argument type that isn't a
   plain nested struct defined inline (common naming pattern: `<pkg>.Arguments`,
   `otelcolCfg.DebugMetricsArguments`, and similar) needs this treatment.

## Specific things to check

- [ ] Every `attr`-tagged field in `Arguments` appears in the arguments table.
- [ ] Every `block`-tagged field appears as a documented block, including
      nested blocks inside blocks.
- [ ] New enum values added to a type's `UnmarshalText` switch since the doc was
      last touched (compare against what the doc lists).
- [ ] Fields with a `// Deprecated:` comment in source — confirm the doc marks
      them deprecated too, with guidance on the replacement.
- [ ] Exported fields on the `Exports` type not mentioned in an "Exported
      fields" section, if the doc has one.
- [ ] Component-level capabilities implied by interfaces the component
      implements (e.g., implementing a livedebugging or clustering interface)
      that aren't mentioned anywhere in the doc.

## What NOT to flag

- Unexported (lowercase) struct fields — not user-facing, not a doc gap.
- Fields with no `alloy:"..."` tag at all — these aren't part of the
  user-facing config surface.
- Internal helper types used only for `Convert()`/`convertImpl()` plumbing.

If you're unsure whether something is user-facing, say so in the report's "Open
questions" section rather than guessing either way.

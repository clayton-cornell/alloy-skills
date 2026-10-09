# Completeness checklist: component reference pages

Goal: find things in source that a reader would need but the doc doesn't
mention. Starting list — expand as patterns emerge.

## Required section presence (structural completeness)

Source of truth: `docs/developer/writing-component-documentation.md`'s "Page
structure" section (read directly, not copied — it's in-repo). Every
component reference page must contain all nine of these `##`-level
sections (Title is the `#` page heading), in this order, regardless of
whether the component has real content for a given one:

1. Title
2. Usage
3. Arguments
4. Blocks
5. Exported fields
6. Component health
7. Debug information
8. Debug metrics
9. Examples (`## Example` if there's exactly one)

**A section that doesn't apply to the component must still be present**,
with the documented boilerplate sentence stating it doesn't apply (e.g.
"`COMPONENT_NAME` doesn't expose any component-specific debug
information.") — omitting the section entirely reads as "undocumented,"
not "not applicable," so a missing heading is always a real gap, never a
valid way to handle an inapplicable section.

**What to flag as a completeness gap**:
- A required section heading missing entirely from the page — propose the
  exact heading, and, if the component genuinely has nothing to document
  there, the exact boilerplate sentence from
  `writing-component-documentation.md` with the real component name
  substituted in.
- A required section present as a heading but empty, or missing the
  boilerplate "doesn't expose/support..." sentence when the component has
  nothing to document there.
- **Presence of the heading and a disclaimer sentence isn't proof the claim
  inside it is true — cross-check the content against source.** Confirmed
  real precedent for this exact failure mode: `pyroscope.ebpf.md`'s `##
  Blocks` section states "`pyroscope.ebpf` doesn't support any blocks,"
  which is false (see the `debug_info` block gap in the Method section
  below) — the section isn't missing, but what it claims is wrong. Don't
  stop at "the heading exists" for this check; read what it actually says.

**Don't flag**: extra sections beyond the required nine — a page can have
more, never fewer. This includes the documented exceptions in
`writing-component-documentation.md`'s own "Exceptions" section (e.g.
`loki.source.podlogs`'s CRD section, `otelcol.processor.transform`'s OTTL
Contexts section) — those are sanctioned additions, not deviations.

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
- [ ] **The `instance` label sentence, on every `prometheus.exporter.*`
      page.** Settled convention: the Arguments section ends (after any
      explanatory prose, before `## Blocks`) with "The component sets the
      `instance` label on its exported targets to X."

### Deriving X for the instance label sentence

**Read `InstanceKey()` in source — don't copy a sibling page's phrasing.**
The wording depends on what the function actually returns, and the two cases
mean different things:

| `InstanceKey()` returns | Correct wording |
|---|---|
| a plain field (`return c.SomeAddress`) | "the value of `<arg>`" |
| `url.Parse(...).Host` | "the host and port from `<arg>`" |

Copying "the value of" onto a parsed case is wrong: the label is
`localhost:9200`, not `http://localhost:9200`.

**`url.Parse(...).Host` has edge cases that break the simple phrasing.**
Confirmed by running the stdlib function directly (see
`references/technical-verification.md`):

- It **excludes** userinfo, so credentials don't leak into the label.
- It includes the port only when one is present — a scheme with no port
  yields a bare host.
- For a comma-separated multi-host URI it returns the **whole list**.
- Scheme-less input behaves inconsistently across schemes: some error, some
  parse as `Scheme` + `Opaque` with an empty `Host`, which downstream
  becomes `instance="unknown"`.

So "the host and port from `<arg>`" is wrong for any argument that accepts a
scheme-less or multi-host value. Prefer "the host portion of `<arg>`" there,
and if the empty-`Host` path is reachable, that's a source defect — see
`references/source-defects.md`.

## What NOT to flag

- Unexported (lowercase) struct fields — not user-facing, not a doc gap.
- Fields with no `alloy:"..."` tag at all — these aren't part of the
  user-facing config surface.
- Internal helper types used only for `Convert()`/`convertImpl()` plumbing.

If you're unsure whether something is user-facing, say so in the report's "Open
questions" section rather than guessing either way.

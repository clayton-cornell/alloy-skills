<!-- Extracted from style-consistency.md. -->

# Style consistency: link check and shortcode validity check

## Link check

This was previously too thin ("verify internal links resolve") to catch a
real bug that was sitting in production docs. **Confirmed systemic, not a
single-page accident** — the exact same stale prefix,
`get-started/configuration-syntax/`, has now been directly confirmed (each
read and checked individually, not inferred from one instance) in three
separate files across different sections of the docs tree:
- `tutorials/first-components-and-stdlib.md` (two links: `../../get-started/configuration-syntax/` and `.../configuration-syntax/components/`)
- `collect/prometheus-metrics.md` (`[Objects]: ../../get-started/configuration-syntax/expressions/types_and_values/#objects`)
- `troubleshoot/debug.md` (`[secret]: ../../get-started/configuration-syntax/expressions/types_and_values/#secrets`)

The real current paths (confirmed against the live published site's own
navigation): `get-started/configuration-syntax/` → `get-started/syntax/`;
`get-started/configuration-syntax/components/` →
`get-started/components/configure-components/`;
`get-started/configuration-syntax/expressions/...` →
`get-started/expressions/...` (drop the `configuration-syntax/` segment
entirely — `expressions/` now sits directly under `get-started/`, not
nested under it). **Given three independent confirmations, treat any
`get-started/configuration-syntax/` fragment found in a link as already-known-stale
on sight** — apply the substitution above directly rather than re-deriving
it from scratch each time, though still confirm the specific target section
(`#anchor` or sub-path) still exists at the corrected location before
proposing the final link text. All three only "work" via each target's
`aliases:` redirect, which is exactly why this was missed before: a redirect
makes a stale link *functional* but not *correct*.

### Method

1. **Extract every internal link, both forms** — reference-style definitions
   (`[label]: path`, usually collected at the bottom of the file) and inline
   links (`[text](path)`). Reference-style is the dominant convention across
   every file sampled in this repo; don't only check inline links.
2. **Resolve each path relative to the file's own location.** Empirically
   confirmed pattern: for a file one directory below `docs/sources/` (e.g.
   `tutorials/*.md`, `configure/*.md`, `set-up/*.md`), `../../` reaches back
   to `docs/sources/` and into another top-level section (Hugo treats the
   page itself as an extra pseudo-directory level) — verified against
   multiple already-correct links in the same tutorial file
   (`../../reference/stdlib/`, `../../get-started/components/`). Don't assume
   a different relative-path convention without checking sibling examples
   first.
3. **Check whether the target exists directly** — not just whether it
   resolves via some target page's `aliases:` list. If path X only works
   because the page at Y has `aliases: [X]`, that's a stale link: propose the
   direct path to Y, don't accept the alias chain as "resolved." This is
   exactly the class of bug that a naive "does it 404" check would miss,
   since Hugo aliases mean the link doesn't 404 — it just isn't pointing at
   the real location anymore.
4. **Propose the exact corrected link text**, not just "this link is stale."
   For the confirmed case above: change
   `[configuration syntax]: ../../get-started/configuration-syntax/` to
   `[configuration syntax]: ../../get-started/syntax/`, and change
   `[Components configuration language]: ../../get-started/configuration-syntax/components/`
   to `[Components configuration language]: ../../get-started/components/configure-components/`.

### Link style consistency (separate from resolution)

Separately from whether a link resolves, check whether the topic's link
*style* is internally consistent: reference-style (`[label]: path`) vs.
inline (`[text](path)`), relative path vs. full absolute URL
(`https://grafana.com/docs/...`) for internal Alloy content, and trailing
slash presence. Per `references/style-guide.md`'s copied rule, internal links
should be relative and end in `/`, not `.md`, and a full absolute URL to an
Alloy page (rather than a relative link) is itself a finding, not just a
style preference — it breaks version-relative resolution the way relative
links are designed to support. Flag a page that mixes styles for the same
kind of link (e.g. some internal cross-references as relative paths, others
as hardcoded `https://grafana.com/docs/alloy/latest/...` URLs) as a
cross-topic or within-page consistency issue, and propose the relative form.

Also check that obvious cross-links to related components or concepts exist
where a reader would expect them (e.g., a component wrapping an upstream OTel
processor should link to that upstream processor's docs, as
`otelcol.processor.transform` already does).

Separately, check link **text** quality (not just resolution/style covered
above) — see the "Link text quality" item in
`references/style-consistency-manual-checklist.md`, added from a direct
`writers-toolkit` cross-check: no generic link text ("refer to [this
file]", "click here"), and prefer the linked page's actual title as the
link text.

## Shortcode validity check

General shortcode correctness — separate from Checks A/B/C (which are
`param`-specific — see `references/style-consistency-cascade-vars.md`) and
the sub-feature stability check (which is
`docs/shared`-for-stability-partials-specific — see
`references/style-consistency-stability-callouts.md`). This is a
validation step against a documented schema, the same pattern as the
Frontmatter check: read `references/shortcode-schema.md` and check the
topic's actual shortcode usage against it.

### Method

1. Extract every shortcode invocation in the topic, both delimiter forms
   (`{{< name ... >}}` and `{{% name ... %}}`).
2. Look each one up in `references/shortcode-schema.md`. If the name doesn't
   match any documented shortcode, that's a real finding (likely a typo or a
   made-up name) — propose the closest real match if one's obvious, or flag
   it plainly if not.
3. For shortcodes with required parameters, confirm all of them are present.
   **`docs/shared` is Alloy's single most-used shortcode and has three
   required parameters (`lookup`, `source`, `version`)** — a missing one
   here is a common, high-value thing to actually check, not a formality.
4. **Cross-check against the schema's "Confirmed NOT part of Alloy's
   convention" list**: `docs/public-preview`, `docs/private-preview`,
   `docs/experimental`, `docs/experimental-deployment`,
   `docs/openapi/info`/`docs/openapi/path`, `pyro-flamegraph`, `grot guides`.
   If any of these turn up in an Alloy file, that's the finding itself (a
   generic or other-product shortcode where Alloy has its own convention) —
   propose the Alloy-specific equivalent where one exists (e.g.
   `docs/public-preview` → the correct `stability/*.md` partial per
   `references/style-consistency-stability-callouts.md`'s table), and just
   flag plainly where no Alloy equivalent exists at all.
5. **`docs/reference` is deprecated per the source doc's own warning**
   ("prefer `ref` URIs instead"). If found, propose `ref` URIs or a direct
   relative link instead, depending on whether the multi-destination
   behavior it provides is actually needed.
6. Don't re-report `param`-specific findings here that Checks A/B/C already
   cover (hardcoded product names, version-substitution mechanism, heading
   delimiter) — this check's job is confirming the shortcode *itself* is
   real and its parameters are complete, not re-deriving those three checks'
   more specific findings.

### What NOT to flag

Shortcodes listed in `shortcode-schema.md`'s "not yet confirmed either way"
list (`badge`, `button`, `tabs`, `mermaid`, `image-map`, `fixed-table`,
`term`, video embeds, `card-grid` beyond the site root) aren't unused by
default — don't assume a topic misusing one of these is wrong just because
it hasn't come up in a previously sampled file. Check the actual topic's
usage against the schema like any other shortcode; the "not yet confirmed"
note is about this reference file's own coverage gaps, not a signal that
Alloy avoids them.

# Completeness checklist: self-referential completeness (collect/*.md, monitor/*.md)

Stated component lists vs. actual examples. This one doesn't compare the doc
against Go source at all — it compares the doc against **itself**.
Multi-component task/scenario pages often state which components they use,
then show `alloy` code blocks that should match. This comes in two different
conventions — check for both, don't assume one:

- **Whole-page list**: a "Components used in this topic" (or similarly named)
  bullet list near the top, meant to cover every component used anywhere on
  the page. Confirmed real gap: `collect/opentelemetry-data.md` lists 5
  components (`otelcol.auth.basic`, `otelcol.exporter.otlp`,
  `otelcol.exporter.otlphttp`, `otelcol.processor.batch`,
  `otelcol.receiver.otlp`) but its own "Configure batching" example also uses
  `otelcol.processor.memory_limiter`, which isn't in the list.
- **Per-section count**: a sentence like "requires four components" followed
  by a bulleted list, scoped to just that section rather than the whole page
  (seen in `monitor/*.md` scenario pages, e.g. `monitor-linux.md`'s "Configure
  metrics"/"Configure logging" sections). Checked this pattern directly:
  `monitor-linux.md`'s two per-section counts (four components each) both
  matched their section's actual component blocks exactly — confirmed clean,
  not a bug, but validates the method is worth running even when it doesn't
  find anything.

## Method

1. Identify the scope of any stated component list on the page: whole-page
   ("Components used in this topic") or section-scoped ("requires N
   components," tied to a specific `###`/`##` heading).
2. Extract every distinct component **type** actually invoked in `alloy` code
   fences within that scope (pattern: `namespace.name "label" {` at the start
   of a line). Count by type, not by instance — two `discovery.relabel`
   blocks with different labels still count as one entry in a components-used
   list, not two (confirmed correct in `monitor-linux.md`).
3. Diff both ways:
   - **Used but not listed** — a completeness gap. Propose adding the missing
     entry to the stated list, in the same style/order as existing entries.
   - **Listed but not actually used** — likely a stale list left over after an
     example was edited; propose removing the entry (or flag as "Open
     questions" if the component might be used further down the page outside
     the assumed scope — don't guess at scope boundaries when they're
     ambiguous).
4. If a page has no stated component list or count at all, don't invent one
   as a requirement — this check only applies where the page makes the claim
   itself. Absence of the list isn't a gap in itself unless the page's own
   conventions (compare 2–3 siblings) suggest one is expected.

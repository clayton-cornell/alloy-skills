# Batch modes (multiple topics in one run)

Both modes below are deliberate exceptions to "one topic, fully analyzed, is
the unit of work" — use either only on explicit ask, never as a default
expansion of a single-topic request.

## Batch stability-badge sweep mode

Use this mode only when the person explicitly asks for a stability-badge
audit *across* components ("check every component's stability badge," "are
any stability badges stale," or similar) — not for general-purpose batch
review (see "Batch documentation review mode" below for that).

**Why this is worth a distinct mode rather than just "run Step 3 N times":**
Step 3 (`accuracy-checklist-components.md`'s Component-level checks) already
validates one component's badge against `component.Registration.Stability`
per-topic. This mode is the same check swept across the whole
`reference/components/` tree in one pass, producing one consolidated table
instead of dozens of separate reports — mirroring the same sweep pattern
already used for `--stability.level=experimental` claims repo-wide in
`alloy-scenarios`, just applied to doc badges instead of CLI flags.

**Done when**: every component doc page in scope has a row in the
consolidated table (component | doc `labels.stage` | source `Stability` |
match/mismatch) — no page silently skipped.

### Method

1. **Enumerate every component doc page.** There's no generated master list
   to read from — `reference/components/_index.md` only contains a
   `{{< section >}}` shortcode that renders a listing at Hugo build time, not
   a static list this skill can parse. Walk the actual directory tree
   (`docs/sources/reference/components/**/*.md`, excluding `_index.md`
   files) directly.
2. **Confirm scope with the person before running the full sweep** if the
   ask is ambiguous — "every component" could mean literally all of them
   (100+) or just one namespace (e.g. "check all `otelcol.*` badges"). This
   is exactly the kind of scope confirmation SKILL.md's intro already calls
   for before doing more than one file; don't assume "everything" by default.
3. For each page: extract `labels.stage`, map to Go source per
   `references/source-mapping-components.md`, extract
   `component.Registration.Stability`, and compare by meaning (not string
   equality — same GA-string caveat as the per-topic check).
4. **Produce one consolidated table**, not N separate per-topic reports:
   component name | doc `labels.stage` | source `Stability` | match/mismatch.
   This is the one place in this skill where combining multiple topics into
   a single report is correct, precisely because the whole point of the
   mode is the aggregate view — don't fall back to separate reports here.
5. Given the volume, this will take many tool calls. Say so up front so the
   person knows what to expect, and consider proposing a smaller scoped
   sweep (one namespace, or a sample) if the full tree seems more than the
   person actually wanted.

## Batch documentation review mode (general findings across many topics)

Generalizes the pattern above beyond stability badges: use this when the
person wants a systematic sweep of a directory, component family, or doc
section for general improvement opportunities and gaps (accuracy,
completeness, style) — not just one narrow check.

**For scoping which pages to include, consider the companion
`alloy-docs-freshness` skill first** — a much cheaper, frontmatter-only sweep
that flags pages missing a `review_date` or older than roughly 6–7 months.
Its output ("here's what's missing or stale") is a natural, evidence-based
way to pick a batch scope, rather than picking a directory arbitrarily.
They're deliberately separate skills: that one only checks one date field
and is fast enough to run broadly; this one does deep, expensive analysis
and needs a deliberately bounded scope, per the cost note below.

**The honest cost, stated up front, not discovered partway through**: unlike
the stability-badge sweep (one cheap, narrow comparison per page), this mode
runs the **full** Steps 0–5 per topic — reading Go source, running Vale,
cross-checking multiple reference files. That's the same depth as a single
standalone analysis, multiplied by however many pages are in scope. A
full-tree sweep of `reference/components/` (100+ pages) at this depth is not
a realistic single-pass operation.

**Done when**: every file in the confirmed scope has had the full Steps
0–5 run against it, the consolidated summary is triaged by severity (not
one report per page), and any recurring cross-topic pattern is called out
once rather than repeated per page.

### Method

1. **Confirm scope before starting** — this matters more here than
   anywhere else in the skill, given the cost above. Don't default to "all
   of Alloy's docs." Propose a bounded starting scope (one subdirectory,
   one component namespace like `otelcol.exporter.*`, one doc family like
   `reference/cli/*`, or a fixed sample size) and confirm it before running
   anything, even if the person's original ask sounded broad ("scan the
   Alloy docs" → propose starting with a specific, sized-down slice and
   expanding from there once they've seen what a batch report looks like).
2. **Enumerate the actual files in scope** by walking the real directory
   tree, the same way the stability-badge sweep does — don't rely on a
   generated index page as a file list (confirmed unreliable: Hugo
   `{{< section >}}` shortcodes don't statically list anything this skill
   can parse).
3. **Run the full Steps 0–5 per topic**, exactly as in standalone mode —
   no shortcuts, no skipped checks, same rigor as a single-topic request.
   This is the expensive part and there's no way to responsibly cut corners
   on it without producing shallow, unreliable findings across the batch.
4. **Checkpoint rather than silently power through a large batch.** Process
   a manageable sub-batch (roughly 5–10 topics, depending on how deep each
   one's findings turn out to be), report interim results, and confirm
   whether to continue before starting the next sub-batch — both so the
   person can redirect early (e.g. "skip the low-priority style stuff, just
   keep going on accuracy") and so a very long run doesn't produce one
   enormous, hard-to-review wall of output at the end.
5. **Output is a consolidated, triaged summary, not N full per-topic
   reports.** A full Output Format report per page, multiplied across a
   batch, would be too voluminous to actually use for prioritization — the
   point of a batch scan is triage, not exhaustive documentation of every
   page. Structure the summary as:
   - One row/entry per topic with its most significant findings only
     (severity-ranked: confirmed accuracy issues and completeness gaps
     first, then style/consistency), not everything the full analysis
     turned up.
   - Findings that recur across multiple topics in the batch (e.g. the same
     stale link pattern, the same missing frontmatter field) called out
     once as a systemic/cross-topic finding rather than repeated per page —
     same principle as SKILL.md's one-off-vs-systemic distinction, applied
     across a whole batch instead of within one page.
   - An explicit offer to produce the full, detailed standalone-mode report
     for any specific topic in the batch on request — the full analysis was
     still done internally for each page; the summary is a presentation
     choice, not a shortcut that lost information.
6. If a topic in the batch turns out to need something the batch summary
   format can't represent well (e.g. a confirmed real bug worth fixing
   immediately), surface it prominently in the summary rather than letting
   it get buried at the same weight as a minor style nit.
7. **Include the `review_date` reminder** (see SKILL.md's Output format)
   once per topic that had real findings, not just once for the whole batch
   — each page gets fixed and merged independently, so each needs its own
   reminder tied to its own eventual merge date.

# Triage mode (multi-topic overview)

Use this mode when the user asks for an overview across many pages instead of a
detailed report on one. It replaces the Step 4 report format in `SKILL.md` and
keeps the same evidence rules: verify against the checked-out source, don't
guess, and never edit files.

## Depth

Steps 1-3 still apply, but verify the highest-risk claims first and stop early
on clean pages:

- Config keys, env vars, defaults, accepted values, ports, paths, commands,
  metric names, version/kernel requirements, and examples.
- Skip pure narrative and marketing prose unless it makes a checkable claim.
- If every checked claim is accurate, report the page as Accurate and move on.

## Per-topic result

Return one row per page:

| Field | Meaning |
|---|---|
| Page | Path relative to `docs/sources/` |
| Verdict | `Accurate`, `Minor`, `Major`, or `Unverified` |
| Deviations | Approximate count of confirmed doc-vs-source discrepancies |
| Gaps | Approximate count of confirmed user-facing source behavior the page should cover but doesn't |
| Notes | One line: the most important deviation or gap, with a `file:line` for the doc and source side |

Verdict rules:

- **Accurate**: no confirmed deviations. Gaps may exist.
- **Minor**: deviations that don't change what a user would configure or expect
  (stale wording, an imprecise default, a missing allowed value).
- **Major**: deviations that would make a user's configuration fail, silently
  behave differently, or rely on an unsupported feature. Any wrong key, env var,
  default with behavioral impact, removed option, or unsupported claim.
- **Unverified**: the page's claims can't be checked against the available
  source. Say what is missing.

Counts are approximate; prefix with `~` when you didn't enumerate every item.
Only count confirmed findings. Put unconfirmed items in a short "Open" note,
not the counts.

## Topic-level gap pass

After the per-page rows, do one pass for source behavior that no page covers.
Per-page gap counts only measure missing detail inside existing pages.

1. List the top-level YAML sections and env-var groups in `pkg/beyla/config.go`
   and the nested OBI config types, plus separate binaries and charts under
   `cmd/` and `charts/`.
2. For each, search `docs/sources/` for its key, env var, and plain-language
   name. Report anything with no coverage as a missing topic, with its source
   location and a suggested home.
3. Report features that are only mentioned in passing as "thinly covered".
4. Exclude behavior the source marks as experimental, undocumented, or
   development-only. List these under "Not counted" so the omission is visible.

This is a keyword-coverage survey, not a page review. Say so in the report.

## Evidence discipline

A search hit isn't evidence. Open each file you cite and confirm the context
before recording a note. Don't pad Notes for Accurate pages.

# Delta/PR review mode (partial doc changes)

Use this mode when the person gives a PR link or number, a git diff/patch, or
asks to review "just the changes" or "what changed in this PR" for the Beyla
docs (`docs/sources/**`), rather than whole pages.

**The honest limit to state up front**: accuracy, completeness, audience, and
style checks need full-page context to be accurate. You can't validate front
matter from a fragment that lacks it, can't tell whether a page omits a
supported option without the whole page, and can't assess audience fit from a
few changed paragraphs. **So always read the full current file for context,
even in delta mode.** What is scoped to the diff is the *output*, not the
analysis input.

**Done when**: every finding is tagged in or out of the changed-line ranges,
the Summary states the scope explicitly, and the out-of-diff finding count is
reported even when the detail is withheld.

## Read-only commands only

Use only read-only commands: `gh pr view`, `gh pr diff`, `git diff`,
`git show`, `git log`. Don't use `gh pr checkout` or `git checkout`, because
they change the working tree. Never post to GitHub, push, comment, or edit
files. See the GenAI note at the end.

## Method

1. **Get the diff.**
   - PR on `grafana/beyla`: `gh pr view <number> --repo grafana/beyla --json title,files,headRefOid,baseRefName`
     and `gh pr diff <number> --repo grafana/beyla`. `gh pr diff` takes no
     path filter, so keep only the `docs/sources/` hunks yourself, and note
     which other files (code) the PR changes.
   - Local branches or commits: `git diff <base>..<head> -- docs/sources`.
   - A raw patch given directly: use it as-is.
2. **Identify changed line ranges per file.** For each doc file touched, note
   which lines were added or modified, not only that the file changed.
3. **Read the full current version of each changed file** and run the normal
   procedure from `SKILL.md`. Don't skip a step because it's delta mode. For a
   PR, "current" means the PR's head version of the file: use
   `git show <headRefOid>:docs/sources/<path>` or `gh pr diff` context. If the
   head commit isn't present locally, say so and review from the diff plus the
   checked-out version, flagging the limitation.
4. **Choose the source to verify against.**
   - If the PR also changes code (outside `docs/`), verify claims in the diff
     against the PR's **head** source, using `gh pr diff` or
     `git show <sha>:<path>`. Cite the head SHA with each source reference.
   - Otherwise verify against the **current checkout**, the same as a
     standalone review. Remember the OBI vendoring caveat in `SKILL.md`: if the
     `.obi-src` submodule isn't present, don't substitute another version.
5. **Tag every finding** as in or out of the changed lines, using the ranges
   from step 2.
6. **Default output**: report only findings in the changed lines, and state how
   many additional pre-existing findings exist outside the diff (count only,
   listed separately in an "Outside the diff" note). If the person says they
   want the whole page reviewed anyway, report everything and use the tags to
   highlight what's new.
7. **Multiple files in one PR**: run the method per file and keep separate
   reports. Don't merge findings from different pages into one report. A short
   rollup listing each page's in-diff finding count is fine.

## A moved or reformatted line is not in scope

**Check whether the content changed, not whether the line changed.** A PR that
reorders table rows, rewraps a paragraph, or restyles a link touches lines
without changing what they say. Treating them as "in the diff" and correcting
their content is out-of-scope editing in disguise.

- **Link and line-break conventions are checked on changed text only.** The
  reference-style link preference, the rule that an admonition holds its own
  link definitions, and one sentence per line apply to lines the PR added or
  changed. Don't flag or count pre-existing inline links or hard-wrapped
  paragraphs on untouched lines. Report their page-level counts once, as a
  follow-up, from `scripts/check_source_format.py`.
- A pre-existing problem on a reformatted line is **reported as a follow-up**,
  never counted as an in-diff finding.
- When a PR fixes one instance of a problem and leaves an identical sibling
  untouched, report the asymmetry as a finding. Don't treat it as a gap to
  close.
- Pre-existing blank or placeholder cells on rows the PR didn't change
  semantically stay as they are.

## What can't be delta-scoped

If you're given only a pasted fragment with no way to locate or read the full
file (no path, no repo access), say which checks can't run reliably
(front matter, completeness, cross-page comparison, audience assessment)
instead of running them against the fragment with false confidence.

## Output

Use the same output format as standalone mode (see `SKILL.md`). The Summary
states the scope, for example: "Scope: PR #1234 delta only
(`configure/export-data.md` lines 40-72, head `<sha>`); N additional
pre-existing findings exist outside this diff." Tag findings in or out of the
diff.

## GenAI policy note

The person writes the PR description and any review comments. This mode
produces a **local report only**. It never posts to GitHub, never drafts text
for the person to paste into a review thread, and never edits the files under
review.

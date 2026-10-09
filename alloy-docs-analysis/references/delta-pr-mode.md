# Delta/PR review mode (partial doc changes)

The standard five steps assume a full-page analysis. Use this mode instead
when the person gives a PR link/number, a git diff/patch, or explicitly asks
to review "just the changes"/"what changed in this PR" rather than the whole
page.

**The honest limit to state up front**: most of Steps 1–5 need full-page
context to be accurate at all — you can't validate frontmatter from a
fragment that doesn't include the frontmatter block, can't run the
self-referential completeness check without the whole page's component list
and every example, can't do cross-topic comparison without knowing the
whole page's structure, and can't assess audience fit reliably from a
few changed paragraphs. **So: always read the full current file for context,
even in delta mode** — the thing that's actually scoped to the diff is the
*output*, not the analysis input.

**Done when**: every finding is tagged in/out of the changed-line ranges, the
Summary states scope explicitly (per the Output section below), and the
out-of-diff finding count is reported even when full detail is withheld.

## Method

1. **Get the diff.** Use `git diff <base>..<head> -- <path>` for a local
   branch comparison, or `gh pr diff <number> -- <path>` if reviewing a
   GitHub PR by number/URL (both assume `git`/`gh` are available via the
   Bash tool in Claude Code, the same assumption already made for
   `grep`/`rg` elsewhere in this skill). If given a raw patch/diff directly,
   use that instead of re-deriving it.
2. **Identify changed line ranges per file.** For each doc file touched,
   note which lines were added or modified (not just "the file changed" —
   the specific ranges matter for scoping output).
3. **Read the full current version of each changed file** and run Steps
   1–5 exactly as normal — don't skip any step because it's "delta mode."
   The full read is what makes every check's findings accurate; skipping it
   to save time produces worse, not faster, analysis.
4. **Tag every finding by whether it falls in a changed line range or not**,
   using the diff from step 2. This is the actual point of delta mode: the
   analysis is full-page, the *presentation* is split.
5. **Default output**: report only findings tagged "in changed lines,"
   with a one-line summary noting how many additional pre-existing findings
   exist outside the diff (count only, not full detail) so the person knows
   there's more if they want a full review too. If the person's request
   already made clear they want the full page reviewed regardless of scope
   (e.g. "review this whole page, focusing on what changed in the PR"),
   report everything and use the tags to highlight what's new instead of
   filtering.
6. **Multiple files in one PR**: run the full method per file, but keep
   them as separate reports (this skill's existing "one topic, fully
   analyzed, is the unit of work" principle still applies) — don't merge
   findings from different pages into one combined report.

## A moved or reformatted line is not in scope

**Check whether the cell *value* changed, not whether the line changed.** A
PR that reorders table rows, rewraps a paragraph, or restyles a link touches
those lines without changing what they say. Treating them as "in the diff"
and then correcting their content is out-of-scope editing wearing a
delta-mode disguise.

This has gone wrong three times on different PRs, always the same shape: a
row the PR merely *moved* had a pre-existing error, the error was real, and
fixing it inside the delta was still wrong. In one case the PR author had
deliberately fixed one of two identically-broken rows; "finishing the job"
on the second was an unrequested change to a line the PR hadn't semantically
touched.

So:

- A pre-existing problem on a reformatted line is **reported as a follow-up**,
  never corrected in place.
- When a PR fixes one instance of a problem and leaves an identical sibling
  untouched, that asymmetry is a finding to report, not a gap to close.
- Pre-existing blank or placeholder cells on rows the PR didn't semantically
  change stay as they are.

**If you do propose an edit at the edge of delta scope, keep it in its own
isolated change** rather than bundling it into a larger structural edit, so
it can be accepted or rejected on its own.

## What genuinely can't be delta-scoped

If given only a raw text fragment with no way to locate or read the full
file (no path, no repo access, a snippet pasted directly) — rather than a
git diff against a real file — say explicitly which checks can't run
reliably (frontmatter, self-referential completeness, cross-topic
comparison, audience assessment all need full-page context) instead of
running them against the fragment and reporting false confidence. This is a
direct application of SKILL.md's "when you're not sure, say so" principle.

## Output

Use the same Output Format as standalone mode (see SKILL.md), with the
Summary section stating scope explicitly (e.g. "Scope: PR #1234 delta only
(lines X–Y); N additional pre-existing findings exist outside this diff")
and findings tagged per step 4/5 above.

# Handoff: applying fixes after the report

This skill's analysis phase is read-only. After the report, the person often asks the agent to apply some of the fixes in chat. This file defines how, so every change reaches the person as a reviewable edit with Keep and Undo, not as a silent file rewrite.

**This rule outlives the skill run.** It applies for the rest of the conversation after the report, including edits asked for many turns later, when the skill is no longer the thing being "run". It's an instruction to you, not a feature of the host: it works because you follow it, and the Keep/Undo controls depend on the host app (see "What this relies on").

## When editing is allowed

- Only after the person explicitly asks you to apply specific findings or "the fixes" from the report. A report is not a request to edit. When in doubt, ask which findings to apply.
- Only to the page or pages the person names. If the fix needs a second file (for example the sibling that links to a renamed heading), say so and ask first.

## How to edit

1. **Use the editor's in-place file edit tool**, the same kind of tool that lets the person see a diff and press Keep or Undo. For an existing file, make a targeted replacement of the exact lines. Don't recreate or overwrite a whole existing file: that shows as one giant diff that's hard to review. A **new file** (for example a new child topic the person asked for) is created with the file-creation tool, which also shows up for review.
2. **Never change a file through the terminal or a script.** That means no `sed`, `awk`, `perl -i`, `python` or `node` that writes, `tee`, `>` or `>>` redirection, heredocs, `git apply`, `patch`, or running a formatter or linter in write or fix mode (for example `vale` with a fix option, or a Markdown formatter with `--write`). These bypass the review controls. Read-only commands are fine.
3. **Keep edits small and separate.** One finding per edit where you can, in document order, using the corrected text from the report. Don't mix unrelated findings in one change. Apply in this order so the person can keep one group and undo another: accuracy fixes, then completeness additions, then style fixes. Never put a style change in the same change as an accuracy fix.
4. **Change only what the finding says.** Don't reflow paragraphs, re-wrap lines, fix whitespace, rename headings, or "improve" nearby text. Unrelated changes make the diff harder to review.
   - **One exception: text you write.** Any sentence or link you add or replace follows the house conventions (next section), even if the paragraph around it doesn't.
   - **Converting existing text** to those conventions (turning inline links into reference-style links, re-breaking hard-wrapped paragraphs) is its own finding and its own edit. Do it only when the person asks, and say first that it produces a large diff. Offer to do it as a separate pass after the accuracy and gap fixes. Make it one edit per paragraph or per admonition block, so the person can Keep or Undo each one.
5. **Don't accept your own changes.** The person decides with Keep or Undo. Don't describe the edits as final. If the person undoes one, don't re-apply it.

## Conventions for text you write

These apply to every sentence you add or replace, in an edit or in the report's proposed text. Full rules are in `references/style-consistency-links-shortcodes.md` and `references/style-consistency-manual-checklist.md`.

- **Reference-style links.** Write `[text][label]` and define `[label]: destination`. Leave in-page `#anchor` links and images inline. Put the definition block at the end of the page, in order of first use.
- **Inside an admonition, the definitions go inside the block.** A reference link in a `{{< admonition >}}` gets its definition in the same block, after its content and a blank line, even if the label is defined elsewhere on the page. That is a separate hunk from the page-level definitions, so keep it with the text that uses it. If you reuse an existing page-level label in new page text, don't add a duplicate. Page text must never rely on a definition that exists only inside an admonition.
- **One sentence per line.** Break only at sentence ends. Don't wrap at a column width, and don't put two sentences on a line. In a list item, put further sentences on their own lines, indented to the item text.
- **Don't start a sentence with "Because."** Put the main point first and the reason after it. This applies to every sentence you write, and the same rule is in `references/style-consistency-manual-checklist.md`.
- **Adding a link needs two edits:** the sentence, and the definition (inside the admonition block or at the end of the page). Make both, and say which is which, so the person can Keep or Undo them together.
- **Match the page when it differs.** If the page's own links or wrapping are inline or hard-wrapped, still write your new text to the conventions, and mention in the summary that the rest of the page isn't converted.

## Finish with a review_date suggestion

When you've applied **all** the edits the person asked for, and at least one edit to a page is still standing, end your summary with a one-line suggestion to add or update that page's `review_date`:

- The value is today's date as `YYYY-MM-DD` in quotes, like the Writers' Toolkit examples: `review_date: "2026-10-20"`. Take the date from the environment (the current date shown to you). If you can't tell today's date, ask; don't guess.
- Say whether the page already has a `review_date` (suggest updating it) or doesn't (suggest adding it). Beyla pages don't carry one today.
- Suggest once, after the last requested edit, not after each edit. If you edited several pages, list them in one suggestion.
- Don't suggest it if the person undid every edit to a page, or if you applied nothing.
- **Don't add it unprompted.** If the person says yes, apply it as its own in-place edit of just that front matter line, separate from the content edits, so they can Keep or Undo it. Add it as the last front matter key unless sibling pages order their keys differently.
- If the changes merge on a later day, the person may want the merge date instead. Mention that in one short clause, not a paragraph.

This is a suggestion for the person to accept, not a step you perform.

## What not to edit

- This skill's own files (`SKILL.md`, `references/`, `scripts/`, `evals/`, `reports/`). Skill maintenance happens only when the person explicitly asks for it in a separate request, and then with the same in-place edit tool and the same Keep/Undo review. If you notice a way the skill should change while doing a docs run, tell the person in chat; don't change it.
- Source code, Helm charts, `docs/config-schema.json`, workflows, or any file outside `docs/sources/` that the person didn't name.
- Don't commit, push, stage, or open a PR. Don't write the PR description or any review reply (see the GenAI boundary in `SKILL.md`).

## After you edit

Tell the person, briefly:

- which findings you applied, by report number or heading, and which you skipped and why;
- that the changes are pending their review, with Keep or Undo on each;
- anything you couldn't change safely (for example a fix that needs a restructure, or text that changed since the report);
- when every requested edit is done, the `review_date` suggestion (see "Finish with a review_date suggestion").

## If you can't edit in place

If the environment has no in-place edit tool, or you can't tell whether edits will be reviewable, **stop and say so**. Give the proposed text in chat and let the person apply it. Don't fall back to a terminal or script write.

## What this relies on

Keep and Undo come from the host application, not from this skill. In VS Code with the agent, edits made with the editor's file edit tools appear as inline diffs with Keep and Undo; terminal writes don't. I haven't verified that every host or mode behaves this way, so if you don't see review controls on an edit, tell the person.

Because a fresh chat doesn't load this skill, a short always-on instruction in the Beyla repo or in the person's user settings (for example "after a docs review, apply changes only with the in-place edit tool, never through terminal writes") is a useful backup. Suggest that to the person; don't create it unless they ask.

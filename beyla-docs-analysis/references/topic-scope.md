# Topic scope: is this page one topic, or several?

Run this in Step 1, after reading the page and before the accuracy work. A page that tries to be several things at once is hard to keep accurate, hard to scan, and hard to find the right answer on. The goal is to spot when a page should be restructured into focused topics, and say so with evidence.

## Why this isn't a word-count rule

The Writers' Toolkit says that when you write content, you should use one of its topic types: concept, task, reference, tutorial, or scenario (`writers-toolkit/docs/sources/structure/topic-types/_index.md`). Each type answers one question:

| Type | Answers | Notes from the Writers' Toolkit |
|---|---|---|
| Concept | "What is it?" | Doesn't include step-by-step instructions or reference lookup tables or lists of values |
| Task | "How do I?" | Numbered steps toward one outcome |
| Reference | "What details do I need to accomplish this task?" | Lookup information |
| Tutorial | "Can you teach me to…?" | Procedures a user can safely reproduce |
| Scenario | "How should I approach this situation?" | Guidance applied to a real problem |
| Section | Landing page for finding content | Hero, a short overview, and cards that link to child pages |

So judge a page by how many of these jobs it does, not only by how long it is. A long reference page whose job is lookup can be fine. A 160-line page that is a landing page, a concept primer, a decision guide, a requirements checklist, and a getting-started path is doing too much.

## Signals

Count what you can observe, and record each one with line numbers.

1. **Mixed topic types.** Classify each H2 (and big H3) section by the question it answers. More than one type in a page is the main signal. Typical mixes: concept narrative plus numbered procedure; concept plus lookup tables; background plus a decision matrix; prerequisites plus limitations plus next steps.
2. **Page role versus content.** An `_index.md` is a section landing page. If it carries substantial body content beyond a short overview and links to child pages, flag it. Say what it is acting as instead (concept, task, decision guide).
3. **Distinct reader questions.** List the questions the page answers ("what is eBPF?", "should I use this or an SDK?", "will it run on my kernel?", "how do I start?"). Three or more unrelated questions is a signal.
4. **Mixed audiences.** From Step 2, if one page serves a Learner and an Operator or Expert at once, readers have to skip past material that isn't theirs.
5. **Buried answers.** The thing most readers came for sits far down the page, after unrelated material.
6. **Overlap with other pages.** Sections that repeat or approximate content on a sibling or parent page. Search `docs/sources/` before you recommend a new page, so you don't propose a duplicate.
7. **Size, as supporting evidence only.** Measure prose words excluding fenced code, plus H2 and H3 counts. Lines mislead: a page that is mostly code looks long by lines but short by prose.

Starting calibration, measured on the 47 Beyla pages on 2026-10-20: median 143 lines, 594 prose words, 4 H2. `setup/helm-alloy.md` is 619 lines but about 734 prose words, because it is mostly code. `_index.md` is only 164 lines but about 2,100 prose words with 7 H2 and 5 H3, roughly 3.5 times the median prose. **These numbers are a starting point, not thresholds.** As a rough trigger to look closer, use more than about 1,500 prose words or more than about 7 H2. **Size alone never justifies a split recommendation. You need at least two distinct purposes (signal 1 or 3) as well.** Update this calibration when you've seen more runs.

## When not to recommend a split

- **Reference pages that are long because the material is a list of options or values.** Readers look things up; splitting scatters the lookup. Only recommend a split when the page covers clearly separate sub-areas that readers approach separately, and say which.
- **Tasks that belong together.** The Writers' Toolkit says it's reasonable to combine tasks when you document more than one approach to the same user goal, when tasks are likely done around the same time, or when documenting create/read/update/delete operations. It also warns against combining content at random because that can hide information. Don't split a task page that follows those guidelines.
- **A tutorial that tells one story.**
- **A split that would hide information** or force readers to follow several links to complete one job.
- **Size with a single purpose.** A long page with one purpose and a clear structure gets a "long but cohesive" verdict.

If the evidence is thin or the call is borderline, say so and give your best judgment with the reason. Don't force a verdict.

## What to report

Add a `## Scope and structure` section to the report (after Audience) with:

- **Verdict**, one of:
  - `Right-sized`: one purpose, no restructuring suggested.
  - `Long but cohesive`: one purpose; length is inherent. Say what makes it cohesive.
  - `Mixed purpose, consider restructuring`: two or more distinct jobs.
  - `Unclear`: you couldn't decide, and why.
- **Evidence**: a table of section (heading, lines) | topic type it acts as | question it answers | notes, followed by the signals that fired.
- **Proposed structure** (only for `Mixed purpose`): what the parent keeps; proposed child topics with working titles, the topic type of each, and which current sections (by line range) move into each. Use sentence-case titles, nouns for concepts and verbs for tasks. Say where each child belongs (directory, rough `weight`). Name overlap with existing pages, if any, and whether to link to them instead of writing new content.
- **Restructure cost** (small, medium, or large) and what has to be handled when content moves: `aliases` for moved URLs, inbound links across `docs/sources/` (search for them and count), `weight` and `menuTitle`, the parent's `{{< section >}}` listing, and heading anchors that other pages link to.
- **Sequencing**: tag every accuracy, gap, and style finding in the report with the section it belongs to, so findings travel with their content. Recommend doing the split first if the person agrees, then the accuracy pass on the new pages, then the style pass, so fixes aren't applied twice. If they don't want a split, the findings still apply to the current page.

The recommendation is a proposal for a human decision. A restructure changes URLs and navigation, so don't present it as a fix to apply. Content that moves into a child topic is new text for that page, so write any proposed outline or draft to the house link and line-break conventions (`references/handoff-editing.md`); a split is also the cheapest moment to convert it. Outline the child topics only; draft their full content only when the person asks, as a handoff edit (see `references/handoff-editing.md`; a new page is created with the file-creation tool so the person can review it).

## Worked example (illustrative; re-read the page, don't reuse this as a finding)

When this check was designed, `docs/sources/_index.md` had these sections:

| Lines | Section | Acts as |
|---|---|---|
| 25-42 | eBPF application auto-instrumentation | Concept (product intro and feature list) |
| 44-76 | eBPF overview, with three H3 subsections | Concept, plus a long security and performance argument |
| 78-130 | Determine compatibility, with practical guidance | Decision guide with a lookup table |
| 132-143 | Requirements | Reference (prerequisites) |
| 145-153 | Limitations | Concept and reference (capabilities) |
| 155-161 | Get started | Section links |

That's four or more jobs in one landing page. A reviewer following this method would still re-read the page, count the signals, check for overlap with `security.md` and `distributed-traces.md`, and only then propose a structure.

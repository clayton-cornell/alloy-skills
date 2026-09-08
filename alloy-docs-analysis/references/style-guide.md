<!-- Copied from docs-ai/skills/shared/style-guide.md. -->

## Style guide

Always strictly adhere to the documentation style guide:

Product naming (Grafana organization):

- Write for Grafana Labs users, not staff
- Do not document how to develop on the project
- Do not document deployment for Grafana Cloud products
- Use long product names with "Grafana" in article overviews
- Use short product names without "Grafana" in the article body
- Always use "Grafana Cloud," not "Cloud."
- Mention metrics, logs, traces, profiles in this order

Style:

- Follow Every Page is Page One
- Keep articles short and focused
- Use present simple tense, second-person, and active voice
- Use simple words, short sentences, and few adjectives or adverbs
- Prefer contractions
- Use sentence case for titles, headings, and UI
- Bold UI text
- Reference UI text, not element types such as button or tab

Structure:

- Include a short overview after each heading
- Structure most content under h2 headings
- Use h3 for related subsections
- Do not use lists as a substitute for paragraphs
- Use ", for example," for examples
- Use relative links for internal pages
- End links in `/`, not `.md`
- Use "refer to" instead of "see."
- Separate code and output blocks
- Use `>` quotes for Assistant prompt examples
- Use `<VARIABLE_1>` in code and _VARIABLE_1_ in copy for variables

Where necessary, use the following custom Grafana shortcodes for Hugo:

- If a product or feature is in public preview, use `{{< docs/public-preview product="<PRODUCT|FEATURE">}}`
- Use admonitions sparingly: `{{< admonition type="note|caution|warning" >}}<CONTENT>{{< /admonition >}}`

**Alloy-specific note (not in the original source file): `docs/public-preview` is not Alloy's convention — ignore this bullet entirely for Alloy analysis.**
This shortcode belongs to other Grafana products' documentation conventions.
Every real Alloy page checked (`reference/cli/run.md`, `array.md`, and
others) uses `{{< docs/shared lookup="stability/<name>.md" source="alloy"
version="<ALLOY_VERSION>" >}}` instead — see
`references/style-consistency-stability-callouts.md`'s "Sub-feature
stability callout consistency" section for the full method and the exact
partial-selection table. Don't check Alloy docs for `docs/public-preview` usage, don't propose
it as a fix, and don't treat its presence or absence as a finding of any
kind — it's simply not part of Alloy's toolset. If it ever turns up in an
Alloy file, that would itself be the anomaly (wrong product's convention
leaking in), not a case of "either shortcode is fine."

## Templates

Always include introduction after each heading.
Structure most content under h2 headings.
Use h3 for related subsections.
Use lists sparingly - only for actual list content, not as a substitute for paragraphs.

Determine the topic type from the context and generate the article using the corresponding template. Do not deviate from the template structure.

## Concept template

```markdown
---
title: <Concept name>
menuTitle: <Short title>
weight: <number>
aliases:
  - /old-url/
topicType: concept
versionDate: YYYY-MM-DD
---

# <Concept name>

Introduction explaining the concept, its purpose, and when you use it.

## Why this concept matters

Describe the problem it solves and the outcomes it enables.

## How it works

Explain the underlying ideas, models, or flows.

## Related concepts

Link to related articles.

## Related tasks
```

## Task template

```markdown
---
title: <Task name>
menuTitle: <Short title>
weight: <number>
aliases:
  - /old-url/
topicType: task
versionDate: YYYY-MM-DD
---

# <Task name>

Introduction explaining the goal of the task and when you perform it.

## Before you begin

List requirements.

## <ACTION_VERB_HEADING>

Explain task steps in short sentences.

## Result

Explain how to confirm success.

## Next steps

Link to follow-up tasks.
```

## Reference template

```markdown
---
title: <Reference topic>
menuTitle: <Short title>
weight: <number>
aliases:
  - /old-url/
topicType: reference
versionDate: YYYY-MM-DD
---

# <Reference topic>

Introduction explaining what the reference covers and when to use it.

## Definitions

Define terms.

## Parameters

List fields or settings.

## Examples

Provide minimal examples.

## Related resources

Link to tasks or concepts that use this reference.
```

## Scenario template

```markdown
---
title: <Scenario name>
menuTitle: <Short title>
weight: <number>
aliases:
  - /old-url/
topicType: scenario
versionDate: YYYY-MM-DD
---

# <Scenario name>

Introduction describing the scenario.

## How the scenario works

Explain behavior or flow.

## Goal

## Challenge

## Solution

## Outcome

## Next steps

Link to related articles.
```

## Introduction template

```markdown
---
title: <Product or section name>
menuTitle: <Short title>
weight: <number>
aliases:
  - /old-url/
topicType: introduction
versionDate: YYYY-MM-DD
---

# <Product or section name>

Introduction explaining the purpose of the product, feature, or section.

## How it works at a glance

## Your workflow

## Fundamentals

## Next steps

Link to concept, task, scenario, and reference pages.
```

## Index template

Always use this template for section `_index.md` pages except the home page.

```markdown
---
# Same article frontmatter
---

# Section title

Introduction providing overview of goals and content.

{{< section withDescriptions="true" >}}
```

---

## Alloy-specific deviation (not in the original source file)

Alloy's actual frontmatter does **not** follow the generic
`topicType`/`menuTitle`/`versionDate` templates above verbatim. Reference pages
under `reference/components/` use `title`, `description`, `labels.stage`,
`labels.products`, `canonical`, and `aliases` instead.

This is consistent across every reference page checked so far — that's
evidence of an established local convention, not scattered mistakes. Don't
propose rewriting individual pages to match the unused generic template;
instead, propose the fix at the template level: this file (or the equivalent
section of `writers-toolkit`) should document a `reference/components`-specific
frontmatter shape that matches what Alloy (and likely other component-heavy
projects) actually needs, rather than leaving reference pages measured against
a template they were never going to follow. State that proposal explicitly in
the report rather than just noting the deviation exists.

What's still checkable and fixable per-page regardless of which template
Alloy's reference pages follow: field *values* against the documented enums in
`references/frontmatter-schema.md` (`labels.stage`, `labels.products`) and
required-field presence (`title`, `description`). Those are individual
deviations from Alloy's own established practice when they occur — propose
the literal corrected frontmatter block for those, the same as any other
accuracy finding. See `references/style-consistency-frontmatter.md` for
the full check.

## Alloy-specific note on the Task template (not in the original source file)

Alloy's task-style pages (`set-up/install/*.md`, `set-up/run/*.md`,
`configure/*.md`, `collect/*.md`, `monitor/*.md`) don't follow the generic
Task template above either, and — unlike the reference-page frontmatter
case — they don't even follow *one* consistent alternative. Confirmed at
least four distinct family conventions by direct comparison:

- **`install/*.md`**: "Before you begin" → one or more action heading(s) →
  verification, but even verification's *shape* varies within the same
  family — `docker.md` has an explicit `## Verify` heading, `kubernetes.md`
  folds it into a numbered step plus a closing sentence, no dedicated
  heading.
- **`run/*.md`**: no "Before you begin" at all; multiple action-verb H2s
  (Start/Configure to start at boot/Restart/Stop/View logs in
  `run/linux.md`) → "Next steps." No "Result"/"Verify" heading; verification
  is sometimes an inline "Optional:" sentence within an action section.
- **`configure/*.md`**: no "Before you begin," numbered steps directly under
  the H1, capability-specific H2 sub-sections (e.g. `configure/linux.md`'s
  "Pass additional command-line flags," "Expose the UI to other machines").
  No distinct verification section.
- **`collect/*.md`**: adds a "Components used in this topic" list (see
  `references/completeness-checklist.md`'s self-referential check) before
  "Before you begin," then task sub-sections — ends with "For more
  information" references, not a Result/Verify heading.

**Don't build or apply a single rigid template check against this diversity**
— it would misfire constantly given the real variation shown above. Instead,
do this at Step 1 (name which family the page belongs to and its typical
shape) and check actual conformance at Step 5 via cross-topic comparison
against 2–3 siblings **from the same subdirectory**
(`references/style-consistency-cascade-vars.md`'s "Cross-topic comparison"
section) — not the generic
template. A within-family inconsistency (e.g. `docker.md` having a `## Verify`
heading its `kubernetes.md` sibling lacks) is worth flagging as a real,
fixable inconsistency; a difference *between* families (install vs. run) is
expected and shouldn't be flagged at all.

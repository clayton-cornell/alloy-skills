<!-- Copied from writers-toolkit/docs/sources/write/front-matter/index.md. -->

# Front matter

The source files of Grafana documentation use front matter to organize the content, order the project table of contents, and help users identify useful pages when searching or viewing the content in search engines or in social media, such as Twitter.

Use YAML for all front matter.
Unless a front matter field is documented as supporting Markdown, _don't_ include any special Markdown formatting, like italics, in that field.

The following snippet shows example front matter at the beginning of a Markdown file:

```markdown
---
description: Learn more about Grafana Mimir's microservices-based architecture.
labels:
  products:
    - oss
keywords:
  - Mimir
  - microservices
  - architecture
menuTitle: Architecture
title: Grafana Mimir architecture
weight: 100
---
```

## Reference

The following headings describe what each front matter field does and provides guidelines for using it.

### Aliases

Use `aliases` to create redirects from the previous URL to the new URL when a page changes or moves.

When you rename or move files, you must create an alias with a reference to the previous URL path to create a redirect from the previous URL to the new URL.
In some cases, for example when you have deleted content or split a file into multiple topics, it may not be possible to create an alias for the moved content.

Only rename a file in cases where the previous filename in the URL would be confusing for a reader.

#### Guidelines

The correct way to use aliases depends on whether the project is versioned or not.

##### Versioned projects

Aliases must be relative to avoid redirecting latest content to old versions.

Aliases should include a YAML comment explaining the absolute URL path that the relative path redirects.
This helps a reviewer confirm that your alias works correctly.

For example, the following Markdown front matter snippet, in the file `new-url.md`, defines an alias to redirect `/docs/grafana/<GRAFANA_VERSION/original-url/`.

```
---
aliases:
  - ./original-url/ # /docs/grafana/<GRAFANA_VERSION>/original-url/
---
```

##### Unversioned projects

Unversioned projects, such as Grafana Cloud, use absolute paths for aliases because there's no version component in the URL.

Unlike versioned projects:

- Use **absolute paths** starting with `/docs/` rather than relative paths starting with `./` or `../`.
- Don't include a YAML comment to clarify the expanded path.

Additional guidelines:

- Include an `aliases` entry for the current URL path.
- Add an `aliases` entry to make it safer to move content around, as the redirect from old to new page location is already in place.
- When a page is moved, update the `aliases` with the new URL path.

### Banners

Use `banners` to render one or more admonitions at the top of a page's content in the docs layout.
Set `banners` under `cascade` on a section's `_index.md` to apply the same banners to every descendant page.

The value of `banners` is a sequence of mappings, each with:

| Field  | Description                                                            | Required |
| ------ | ---------------------------------------------------------------------- | -------- |
| `type` | The type of admonition. One of `caution`, `note`, `tip`, or `warning`. | yes      |
| `body` | The Markdown content of the admonition.                                | yes      |

### Canonical

The `canonical` front matter sets the preferred URL for duplicate or very similar pages.
Search engines use this information and only index the canonical URL.
The value should be the full URL of the canonical page.
All pages reused via Hugo mounts should have `canonical` set.

### Cascade

Hugo `cascade` front matter passes fields down from a parent (typically a section `_index.md`) to page descendants. Two forms exist: array (with a `_target.path` matcher) and mapping (applies to all descendants unconditionally). Also used to define variables consumed via the `param` shortcode.

### Date

`date` is the initial publish date, in full ISO 8601 timestamp format. Recommended for release note pages (RSS feeds). Also affects menu ordering — more recent dates sort lower.

### Description (required)

Short description of the topic for search engines and social media. Aim for at least 150 characters; include contextual information like the product name since the reader isn't on the Grafana website yet.

### Draft

When `draft: true`, Hugo doesn't render the content unless built with `--buildDrafts`.

### Keywords

Used to generate links in the "Related content" section. Don't affect SEO. Prefer single terms over phrases.

### Labels

Use `labels` to add values that appear before the topic title on the published page. **The website only supports certain label values** — this is the validatable part.

#### `labels.products`

Array of one or more of exactly these three values:

- `cloud` — Grafana Cloud
- `enterprise` — Enterprise
- `oss` — Open source

Use every value that applies. A page with both open-source and Cloud content sets both.

#### `labels.stage`

Exactly one of these four values per page:

- `experimental`
- `private-preview`
- `public-preview`
- `general-availability`

If a page has content at multiple stages, use the appropriate release-lifecycle copy in each section rather than trying to express that in front matter — front matter `stage` applies to the whole page.

#### `labels.tags`

General-purpose labels. Each entry has `text` (required) and an optional `tooltip`.

### MenuTitle

Use `menuTitle` for a different sidebar title than `title` (e.g., an abbreviation). Don't drop the verb from task-topic titles when setting `menuTitle` unless the containing section already implies it.

### Meta image

Sets Open Graph/social media image metadata. Value must be a URL of an image already hosted on the website.

### Refs

For explicit control over multi-destination links, use `ref` URIs paired with `refs` front matter.

### Review date

`review_date` records when a page was last reviewed for correctness, format `YYYY-MM-DD`. Rendered at the foot of the page.

### Slug

Overrides the last URL segment. Ineffective on `_index.md`. Prefer renaming the file over using `slug`.

### Title (required)

Should match the first heading and URL slug. Becomes the HTML `<title>`. Optimize for search: under ~70 characters, has real context, is unique.

### Weight

Controls sidebar ordering (default is alphabetical by `title`). Use increments of 100. Weights are per-directory.

### `_build`

Controls whether Hugo lists (`list`) and/or renders (`render`) a page — used to make private-preview pages reachable by direct URL without appearing in the sidebar table of contents.

## Tutorials-only front matter

Not applicable to `reference/components/` pages. `associated_technologies`, `authors`, `summary`, and `tags` (expertise level: Beginner/Intermediate/Advanced) apply only to tutorial pages under a different section — included here for completeness since this file was copied in full, not because Alloy's component reference pages use them.

## Alloy-specific note (not in the original source file)

**None of the four generic tutorial fields above are actually used by Alloy's own tutorials.** Confirmed across two real files (`tutorials/first-components-and-stdlib.md`, `tutorials/send-logs-to-loki.md`) — neither has `associated_technologies`/`authors`/`summary`/`tags`. Don't flag their absence as a gap on `tutorials/*.md` pages; that's expected here, not a deviation.

**What Alloy tutorials actually use instead: a `killercoda:` field**, not documented anywhere in this file (or, per a prior front-matter audit, anywhere in `writers-toolkit` at all — it's a genuine Grafana-wide documentation gap, not an Alloy-specific mistake). Confirmed real structure in `send-logs-to-loki.md`:

```yaml
killercoda:
  title: <same as page title>
  description: <same as page description>
  preprocessing:
    substitutions:
      - regexp: '<pattern>'
        replacement: <replacement text>
  backend:
    imageid: ubuntu
```

Used alongside `<!-- INTERACTIVE ... -->` HTML comments and the `{{< docs/ignore >}}` shortcode, which mark content that should only appear in the source page vs. only in the Killercoda-transformed interactive sandbox version. Don't flag `killercoda:` as an unknown/invalid field when it appears — it's real and intentional — but don't attempt to validate its internal structure against any documented schema either, since none exists yet. If you want to actually build a schema for it, that's tracked as a separate, larger effort in `.claude/skills/alloy-docs-analysis/references/additional-checks.md`'s "Front matter compliance" section (the "full 8-repo audit integration is blocked" item), not something to invent here.

**A second undocumented field, confirmed independently of the audit above:
`headless: true`.** Present on every `docs/sources/shared/**/*.md` partial
checked (`shared/stability/experimental.md`, `experimental_feature.md`,
`experimental_otel.md`, `public_preview.md`, `community.md`) — a genuinely
real, recurring, undocumented-in-`writers-toolkit` Hugo field, not this
file's oversight. It tells Hugo not to render the page as a standalone
page with its own permalink, appropriate for content that's only ever
consumed via the `docs/shared` shortcode elsewhere, never visited directly.
Don't flag `headless: true` as unknown on pages under `docs/sources/shared/`
— it's expected there. If it turns up on a normal, standalone page instead,
that's worth flagging as suspicious (a page that shouldn't be headless
being marked as such), since that would actually break its own URL.

<!-- Condensed from writers-toolkit/docs/sources/write/front-matter/index.md (the Grafana-wide front matter spec). -->

# Front matter

Grafana documentation uses YAML front matter to organize content, order the table of contents, and help readers find pages in search and social media. Unless a field is documented as supporting Markdown, don't put Markdown formatting (italics and so on) in it.

```yaml
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

## Field reference

### `aliases`

Redirects from a previous URL to this page. When you rename or move a file, add an alias for the previous URL path. Only rename a file when the old filename in the URL would confuse a reader. Where content was deleted or split into several topics, an alias may not be possible.

- **Versioned projects**: aliases must be relative so latest content doesn't redirect to old versions. Add a YAML comment with the absolute path the alias redirects, so a reviewer can confirm it. Example: `- ./original-url/ # /docs/grafana/<GRAFANA_VERSION>/original-url/`.
- **Unversioned projects** (for example, Grafana Cloud): use absolute paths starting with `/docs/`, no comment. Include an alias for the current path so moving the page later is safe. When a page moves, update the aliases.

### `banners`

Renders admonitions at the top of the page. Set under `cascade` on a section `_index.md` to apply to all descendants. Each entry needs `type` (`caution`, `note`, `tip`, or `warning`) and `body` (Markdown).

### `canonical`

Preferred URL for duplicate or near-duplicate pages. Full URL. Pages reused through Hugo mounts should set it.

### `cascade`

Passes fields from a parent (typically `_index.md`) to its descendants. Array form uses a `_target.path` matcher; mapping form applies to every descendant. Also defines variables for the `param` shortcode.

### `date`

Initial publish date, ISO 8601 timestamp. Recommended for release notes. More recent dates sort lower in menus.

### `description` (required)

Short description for search engines and social media. Aim for at least 150 characters and include the product name, because the reader isn't on the Grafana site yet.

### `draft`

`draft: true` means Hugo doesn't render the page unless built with `--buildDrafts`. Hugo front matter keys are case-insensitive. A key spelled `Draft` is treated as `draft`, but the lowercase spelling is conventional.

### `keywords`

Used to build the "Related content" links. Doesn't affect SEO. Prefer single terms over phrases.

### `labels`

Values shown before the page title. The site supports only specific values:

- `labels.products`: one or more of `cloud`, `enterprise`, `oss`. Use every value that applies.
- `labels.stage`: exactly one of `experimental`, `private-preview`, `public-preview`, `general-availability`. Applies to the whole page.
- `labels.tags`: entries with `text` (required) and optional `tooltip`.

### `menuTitle`

Sidebar title when it should differ from `title`. Don't drop the verb from task-topic titles unless the containing section implies it.

### `meta image`

Open Graph/social image. A URL of an image already hosted on the website.

### `refs`

Explicit control over multi-destination links, paired with `ref` URIs in the body.

### `review_date`

`YYYY-MM-DD`, the date the page was last reviewed. Rendered at the page foot. The Writers' Toolkit examples quote the value (`review_date: "2024-09-03"`). **Checking it is out of scope for `beyla-docs-analysis`.** After the person's requested edits are applied, the agent suggests adding or updating it (see `references/handoff-editing.md`).

### `slug`

Overrides the last URL segment. Doesn't work on `_index.md`. Prefer renaming the file.

### `title` (required)

Should match the first heading and the URL slug. Becomes the HTML `<title>`. Keep it under about 70 characters, give it real context, and make it unique.

### `weight`

Sidebar order (default: alphabetical by `title`). Use increments of 100. Weights are per directory.

### `_build`

Controls whether Hugo lists and/or renders a page. Used to make a page reachable by URL without appearing in the sidebar.

## Tutorials-only fields

`associated_technologies`, `authors`, `summary`, and `tags` (expertise level) apply to tutorial pages only. Not relevant to Beyla's current pages.

## Beyla-specific note

All 47 pages under `docs/sources/` use `title`, `menuTitle`, `description`, `weight`, and `keywords`. Not every page uses the other fields:

- `aliases` appears on 17 pages. Every observed entry is absolute: mostly `/docs/grafana-cloud/monitor-applications/beyla/...` (the old Grafana Cloud location, an unversioned project, so absolute is correct there) and four `/docs/beyla/latest/...` entries (`tutorial/...`, `stability/`). The `/docs/beyla/latest/...` form differs from the relative-alias rule for versioned projects above. Raise it as a low-confidence question, not a defect, because whether the Beyla site build needs relative aliases is unverified. Don't propose adding YAML path comments to the existing entries.
- `cascade` appears only on the root `_index.md` (`cascade.labels.products: [oss]`), so every page inherits `oss`. A missing `labels` on an individual page is therefore expected, not a finding.
- No page uses `labels` directly, `review_date`, `canonical`, or `topicType`.
- `setup/standalone.md` sets `Draft: true`.

The field-by-field check is in `references/style-consistency-frontmatter.md`.

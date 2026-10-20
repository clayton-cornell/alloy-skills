<!-- Condensed from writers-toolkit/docs/sources/write/shortcodes/index.md. Rendered examples and prose dropped; this is a validation schema (name, parameters, required/optional). -->

# Shortcode schema

The authoritative "is this a real shortcode, used correctly" reference, in the same role as `frontmatter-schema.md`. A shortcode name that isn't listed here, or a missing required parameter, is a finding. A Hugo shortcode has two delimiter forms: `{{< name >}}` (output inserted as-is) and `{{% name %}}` (inner content processed as Markdown).

## Documented Grafana shortcodes

| Shortcode | Purpose | Required parameters | Notes |
|---|---|---|---|
| `admonition` | Banner/blockquote | `type`: `caution`, `note`, `tip`, `warning` | Closing tag `{{< /admonition >}}`. |
| `anchorize` | Anchor fragment for a heading text | one positional argument | |
| `badge` | Styled badge | `text` | Optional `style` (`stage`, `product-oss`, `product-enterprise`, `product-cloud`, `product-oss-enterprise`, `product-general`, `support`), `tooltip`, `id`. |
| `button` | Link rendered as a button | `link`, `type` (`primary`, `secondary`, `white`, `outline-white`, `outline-gray`, `outline-blue`, `success`, `empty`, `none`) | Optional `size` (`mini`, `small`, `slim`, `large`, `hero`), `target`, `class`. |
| `card-grid` | Grid of cards from a front matter array | `key` (and the front matter items) | Each card needs `title` and `href`. |
| `code` | Multi-language code switcher | none | Optional `annotated="true"`. Supports `@@@PLACEHOLDER@@@` editable placeholders (global across the site, so use project-prefixed names). |
| `docs/alias` | Relative alias between two pages | `from`, `to` | Optional `output` (`table`, `row`, `string`). |
| `docs/copy` | Inject copy from the website repo's data file | `name` | |
| `docs/experimental` | Note for an experimental product/feature | `product`, `featureFlag` | |
| `docs/experimental-deployment` | Fixed note for an experimental deployment pattern | none | |
| `docs/ignore` | Hide content between markers in rendered output | none | Used to transform source into Killercoda tutorials. |
| `docs/learning-journeys` | CTA to a Learning Journey | `title`, `url` | |
| `docs/list` | Restart ordered-list numbering after inserted shared content | none | |
| `docs/openapi/info`, `docs/openapi/path` | OpenAPI spec display | one of `url`/`data` | `path` also takes optional `scope`. |
| `docs/play` | CTA to a Grafana Play dashboard | `title`, `url` | |
| `docs/private-preview` | Note for a private-preview product/feature | `product` | |
| `docs/public-preview` | Note for a public-preview product/feature | `product` | |
| `docs/reference` | Multi-destination link | | **Deprecated** by the source's own warning: prefer `ref` URIs. Flag if found. |
| `docs/shared` | Include content from a repo's `shared` directory | `lookup`, `source`, `version` | |
| `fixed-table` | Wraps a Markdown table so columns break at any character | none | |
| `figure` | Image with caption | `src` | Optional `alt`, `caption`, `link`, `width`, `height`, `lightbox`, and others. Set `alt`. |
| `grot guides` | Interactive in-page guidance | none | |
| `hero-simple` | Hero section | none | Optional `key`, `title`, `image`, `description`, and others. |
| `image-map` | Image with clickable hotspots from front matter `image_maps` | `key` | Each point needs `x_coord`, `y_coord`, `content`. |
| `mermaid` | Mermaid diagram from inner content | none | |
| `param` | Build-time variable from a `cascade` value | one positional argument | Use `{{% param %}}` in headings. |
| `pyro-flamegraph` | Embeds a flamegraph.com graph | `id` | |
| `section` | List of child-page links | none | Optional `menuTitle`, `ordered`, `withDescriptions`, `depth`. Every non-home `_index.md` should use it. |
| `shared` / `shared-snippet` | Reuse a snippet within a page / include it by `path` + `id` | `id` / `path` | Different from `docs/shared`. |
| `table-of-contents` | In-page TOC | none | The toolkit advises avoiding it, because pages already render a TOC. |
| `tabs` / `tab-content` | Tabbed content | `name` on each `tab-content` | |
| `term` | Glossary tooltip | one positional argument | |
| `translate` | i18n string lookup | one positional argument | Site-template use only. |
| `video-embed`, `vimeo`, `youtube` | Video embeds | `src` (an `.mp4`, ≤10 MB), positional ID, `id` | `youtube` also takes optional `start`, `end`, `autoplay`. |

**Version substitution in URLs.** A separate angle-bracket token syntax (`<GRAFANA_VERSION>`, `<PROJECT>_VERSION`) substitutes the version inferred from the page URL anywhere the token appears, including plain-Markdown links. It isn't a shortcode and isn't used in the Beyla docs observed.

## Shortcodes used in Beyla docs

Counts from `docs/sources/` (47 pages) on 2026-10-20:

| Shortcode | Count | Where | Validate |
|---|---|---|---|
| `{{< admonition type="..." >}}` | 8 | `configure/export-data.md`, `metrics.md`, `network/inter-az.md`, `network/config.md`, `setup/kubernetes-helm.md`, `setup/kubernetes-helm-appolly.md` | `type` is one of the four valid values; closing tag present. |
| `{{% admonition type="..." %}}` | 5 | `network/quickstart.md`, `network/config.md`, `setup/kubernetes.md`, `setup/kubernetes-helm.md` | Same as above. Both forms occur, sometimes on the same page. See the consistency note in `references/style-consistency-links-shortcodes.md`. |
| `{{< section ... >}}` | 2 | `_index.md`, `configure/_index.md` | Section landing pages. |
| `{{< fixed-table >}}` | 1 | `_index.md` | Wraps a table; check that it's closed. |
| `{{< youtube id="..." >}}` | 1 | `setup/kubernetes.md` | `id` present. |

Not used anywhere in the Beyla docs: `param`, `docs/shared`, `relref`, `figure`, `tabs`, `code`, `docs/public-preview`, `docs/private-preview`, `docs/experimental`. Those names are valid Grafana shortcodes. If one turns up on a page, validate its parameters against the table above. Absence is never a finding. Images use plain Markdown `![alt](url)` syntax.

`.vale.ini` ignores `{{<...>}}` and `{{%...%}}` tokens (single-line match), so Vale doesn't lint the shortcode text itself. A shortcode with a typo'd name is only found by this check.

<!-- Copied and condensed from writers-toolkit/docs/sources/write/shortcodes/index.md. Rendered example output and illustrative prose have been dropped to keep this a validation schema (name, parameters, required/optional) rather than a tutorial. -->

# Shortcode schema: every documented Grafana Hugo shortcode

Use this as the authoritative "is this a real shortcode, used correctly"
reference — the same role `frontmatter-schema.md` plays for front matter
fields. A shortcode name not in this list, or a required parameter missing,
is a real finding, not a style nit.

## Badge

Renders a styled badge.

| Parameter | Required |
|---|---|
| `text` | yes |
| `style` | no — one of `stage`, `product-oss`, `product-enterprise`, `product-cloud`, `product-oss-enterprise`, `product-general`, `support` |
| `tooltip` | no |
| `id` | no |

## Button

Renders a styled link as a button (use instead of raw `<a>` tags).

| Parameter | Required |
|---|---|
| `link` | yes |
| `type` | yes — one of `primary`, `secondary`, `white`, `outline-white`, `outline-gray`, `outline-blue`, `success`, `empty`, `none` |
| `size` | no — one of `mini`, `small`, `slim`, `large`, `hero` |
| `target` | no |
| `class` | no |

## Anchorize

Inserts the anchor fragment for its single positional argument (a heading text string).

## Admonition

Renders a blockquote/banner. `{{< admonition type="..." >}}<content>{{< /admonition >}}`.

| Parameter | Required |
|---|---|
| `type` | yes — one of `caution`, `note`, `tip`, `warning` |

## Card grid

Renders a responsive grid of cards, sourced from a front matter array.

| Parameter | Required |
|---|---|
| `key` | yes — front matter key holding the card array |
| `items` | yes (via front matter) |
| `type` | no — only `simple` currently |
| `min` | no — `xs`/`sm`/`md`/`lg` |
| `wrapper_class`, `grid_class`, `card_class` | no |

Card object fields (under the front matter array): `title`, `href` (required), `description`, `logo`, `width`, `height`.

## Code

Multi-language code block switcher.

| Parameter | Required |
|---|---|
| `annotated` | no — `"true"` for two-column annotated layout (single language only) |

Supports the `@@@PLACEHOLDER@@@` editable-placeholder syntax (global store across the whole site — use project-prefixed names to avoid collisions, e.g. `@@@ALLOY_CONFIG_PATH@@@`).

## Docs/alias

Determines the relative alias between two pages; renders as table/row/string.

| Parameter | Required |
|---|---|
| `from` | yes |
| `to` | yes |
| `output` | no — `"table"` (default), `"row"`, `"string"` |

## Docs/alloy-config

Renders an interactive, collapsible configuration tree from a Markdown table. No shortcode-level parameters — takes a Markdown table (`Block \| Description \| Required`) as its inner content. **Used on nearly every Alloy component reference page** — this is Alloy's own primary use of the shortcode system, not a generic one.

## Docs/copy

Injects copy from the website repo's `data/docs/copy.yaml`.

| Parameter | Required |
|---|---|
| `name` | yes — key in the data YAML file |

## Docs/experimental-deployment

No parameters. Produces a fixed note about an experimental deployment pattern. **Not the same as Alloy's own `shared/stability/*.md` partials** — don't conflate; this is a different, generic Grafana-wide shortcode for deployment patterns specifically, and hasn't been confirmed in use anywhere in Alloy docs sampled so far.

## Docs/experimental

Produces a note admonition for an experimental product/feature.

| Parameter | Required |
|---|---|
| `product` | yes |
| `featureFlag` | yes |

**Not confirmed in use in Alloy** — Alloy's own convention for this is `{{< docs/shared lookup="stability/experimental.md" or "stability/experimental_feature.md" ...>}}` (see `style-consistency-stability-callouts.md`'s sub-feature stability check). Don't propose this generic shortcode as a fix for Alloy pages; propose the Alloy-specific partial instead.

## Docs/ignore

Ignores content between start/end markers in rendered output (used to transform source into Killercoda tutorials). No parameters. **Confirmed in active use** in Alloy tutorials (e.g. `tutorials/send-logs-to-loki.md`) alongside `<!-- INTERACTIVE ... -->` HTML comments — see `frontmatter-schema.md`'s "Alloy-specific note" on the `killercoda:` field for the related convention.

## Docs/learning-journeys

CTA linking to a Grafana Learning Journey.

| Parameter | Required |
|---|---|
| `title` | yes |
| `url` | yes |

## Docs/list

Restarts ordered-list numbering after shared content is inserted mid-list. No parameters (wraps other shortcodes/content).

## Docs/openapi/info, Docs/openapi/path

Display OpenAPI spec info/paths.

| Parameter | Required |
|---|---|
| `url` | no (one of `url`/`data` required) |
| `data` | no (one of `url`/`data` required) — filename under website `data/docs/openapi/` |
| `title` (info only) | no |
| `scope` (path only) | no — filter by OpenAPI tag |

**Not confirmed relevant to Alloy** — Alloy has no REST API of this kind documented today.

## Docs/play

CTA linking to a Grafana Play dashboard.

| Parameter | Required |
|---|---|
| `title` | yes |
| `url` | yes |

## Docs/private-preview

Note admonition for private-preview product/feature.

| Parameter | Required |
|---|---|
| `product` | yes |

**Alloy doesn't use the `private-preview` stability level at all** (see `internal/featuregate/featuregate.go` — Alloy explicitly has only experimental/public-preview/GA, per `style-consistency-frontmatter.md`'s frontmatter check item 2). This shortcode's presence in an Alloy file would itself be a red flag worth investigating, same principle as `docs/public-preview` below.

## Docs/public-preview

**Not Alloy's convention — see `references/style-guide.md`'s "Alloy-specific note" on this exact shortcode.** Never propose it for Alloy; the Alloy-specific mechanism is `{{< docs/shared lookup="stability/public_preview.md" ...>}}`.

## Docs/reference

**Deprecated per the source's own warning** ("prefer `ref` URIs instead — don't use it when creating new or updating existing documentation"). If found in an Alloy file, that's worth flagging as using a discouraged mechanism, proposing `ref` URIs or a direct relative link instead, depending on whether the multi-destination behavior is actually needed.

## Docs/shared

Includes shared/headless content from a source repo's `shared` directory.

| Parameter | Required |
|---|---|
| `lookup` | yes — path relative to the shared directory root |
| `source` | yes — e.g. `"alloy"` |
| `version` | yes — supports version-substitution syntax like `<ALLOY_VERSION>` |
| `leveloffset` | no |

**This is Alloy's single most-used shortcode** — every `output-block.md`/`otelcol-debug-metrics-block.md`/`stability/*.md` inclusion goes through this. Confirm all three required parameters are present on every call; a missing `version` or `source` is a real, reportable error, not a nit.

## Fixed-table

Prevents column overflow by breaking at any character. No parameters; wraps a Markdown table.

## Figure

Renders an image with a caption via `<figure>`.

| Parameter | Required |
|---|---|
| `src` | yes |
| `alt` | no |
| `caption` | no |
| `caption-align`, `class`, `link-class`, `lazy`, `lightbox`, `link`, `height`, `width`, `max-width`, `show-caption`, `animated-gif` | no |

**Confirmed in active use** throughout troubleshoot/tutorial pages (e.g. `{{< figure src="/media/docs/alloy/ui_home_page.png" alt="..." >}}`). Existence/currency of the referenced image file isn't checked by this skill — deliberately out of scope, matching `docs-ai`'s dedicated `screenshot-check` skill (which needs Playwright MCP) rather than duplicating that work here.

## Grot guides

Interactive in-page guidance. No parameters directly (references the separate Grot guides system). **Not confirmed in use in Alloy docs sampled so far.**

## Hero (simple)

Renders a hero section (title/description/image) from front matter or direct args.

| Parameter | Required |
|---|---|
| `key` | no — front matter key holding hero fields, default `hero` |
| `title`, `level`, `image`, `width`, `height`, `description`, and class overrides | no |

**Confirmed in use** on `docs/sources/_index.md` (the site root hero).

## Image-map

Interactive image with clickable hotspots, sourced from a front matter `image_maps` array.

| Parameter | Required |
|---|---|
| `key` | yes — matches an entry in the front matter `image_maps` array |

Front matter point fields: `x_coord`, `y_coord`, `content` all required per point; `src`, `alt` required at the map level.

## Mermaid

Renders a Mermaid diagram from the shortcode's inner content. No parameters.

## Param

The `param` shortcode provides build-time variable substitution from a `cascade` variable.

**Delimiter differs by context** — angle-bracket `{{< param "X" >}}` in body prose, percent `{{% param "X" %}}` inside a Markdown heading. This is Alloy's Check C (`style-consistency-cascade-vars.md`) — see there for the full method and confirmed evidence.

## Pyroscope flame graph

Embeds a flamegraph.com flame graph.

| Parameter | Required |
|---|---|
| `id` | yes — the path segment after `/share/` in the flamegraph.com URL |

**Not confirmed relevant to Alloy's own docs** (Alloy produces profiles but this shortcode embeds a specific hosted flamegraph, not something Alloy's docs currently do).

## Section

Renders a list of links to child pages, typically on `_index.md` section pages.

| Parameter | Required |
|---|---|
| `menuTitle`, `ordered`, `withDescriptions`, `depth` | no, all boolean/numeric flags |

Per `frontmatter-schema.md`'s copied "Index template," every non-home `_index.md` should use this shortcode (`{{< section withDescriptions="true" >}}` is the specific convention observed on `docs/sources/_index.md`'s "Explore" section via `card-grid`, not `section` directly — verify which of `section`/`card-grid` a given `_index.md` actually needs rather than assuming).

## Shared / Shared snippet

`shared` wraps a snippet (with an `id`) for reuse within the *same page*; `shared-snippet` (percent-delimited, since it returns Markdown) includes it elsewhere by `path` + matching `id`. Different from `docs/shared`, which pulls from a separate repo's `shared/` directory — don't confuse the two mechanisms.

## Table of contents

`{{< table-of-contents >}}`, no parameters. Writers-toolkit's own guidance: avoid using this, since every page already renders a table of contents automatically.

## Tabs

Generic tabbed content via nested `tab-content` shortcodes (`name` parameter required on each `tab-content`). **Confirmed in use** (e.g. `set-up/install/docker.md`'s Docker-command-per-OS presentation was prose-based, not tabs, but the mechanism exists in this repo's tooling for cases that need it).

## Term

Tooltip-on-hover for glossary terms, positional argument = glossary lookup key.

## Translate

Looks up an i18n string by key (positional argument). Site-template use only — not something topic authors typically add themselves.

## Video-embed / Vimeo / YouTube

Embed video content.

| Shortcode | Required parameter(s) |
|---|---|
| `video-embed` | `src` (path to an `.mp4`, ≤10MB) |
| `vimeo` | positional video ID |
| `youtube` | `id` (required), `start`/`end`/`autoplay` (optional) |

## Param (version substitution mechanism)

The `param` shortcode is one mechanism; a *separate* angle-bracket
version-substitution syntax (`<GRAFANA_VERSION>`, `<ALLOY_VERSION>`, etc., no
`param` wrapper) substitutes the version inferred from the page's URL,
overridable via a matching front matter key. The convention is the target
project's name, all upper-case (`alloy` → `ALLOY_VERSION`).

**This is a site-wide substitution, not limited to shortcode attributes** —
it applies wherever the literal token appears, including inside a plain
Markdown link URL in ordinary prose. Confirmed real, working example:
`otelcol.receiver.otlp.md`'s "Enable authentication" section links to
`https://grafana.com/docs/alloy/<ALLOY_VERSION>/reference/components/otelcol/`
as raw prose (not inside any shortcode), and the published page resolves
this correctly (e.g. to `.../latest/...`). Don't treat a bare
`<ALLOY_VERSION>`/`<OTEL_VERSION>` token in a raw URL as a hardcoded-string
violation needing a `{{< param >}}` fix
(that would be the failure mode `style-consistency-cascade-vars.md`'s Check B
explicitly warns against getting backward) — it's already using the correct mechanism,
just in a location worth calling out explicitly. **This is the
mechanism behind every `version="<ALLOY_VERSION>"` in Alloy's `docs/shared`
calls**, and also behind any correctly-placed bare occurrence elsewhere on
the page — see `style-consistency-cascade-vars.md`'s Check B for the full distinction
from the `param` cascade mechanism, which is a different thing despite the
similar-looking angle brackets.

---

## Alloy-specific note (not in the original source file)

**Confirmed in active use in Alloy**, based on files sampled this
conversation: `docs/shared` (pervasive), `docs/alloy-config` (pervasive on
component reference pages), `docs/ignore` (tutorials), `param` (pervasive),
`admonition`, `figure`, `hero-simple` (site root only), `docs/learning-journeys`
(`set-up/install/kubernetes.md`).

**Confirmed NOT part of Alloy's convention, even though documented
Grafana-wide**: `docs/public-preview`, `docs/private-preview` (Alloy has no
private-preview stage at all), `docs/experimental` (Alloy uses its own
`shared/stability/*.md` partials instead), `docs/experimental-deployment`,
`docs/openapi/info`/`docs/openapi/path` (no OpenAPI spec), `pyro-flamegraph`,
`grot guides`. Don't propose any of these as fixes for Alloy pages — if one
turns up in a real file, that itself is the anomaly worth flagging (a
generic/other-product shortcode where Alloy's own convention should be),
not evidence that either option is acceptable.

Not yet confirmed either way (not ruled in or out by direct observation this
session): `badge`, `button`, `card-grid` beyond the site root, `code`
(annotated or placeholder variants), `tabs`, `mermaid`, `image-map`,
`fixed-table`, `term`, video embeds. Don't assume these are unused just
because they haven't come up in a sampled file — check the actual topic
before ruling a shortcode in or out.

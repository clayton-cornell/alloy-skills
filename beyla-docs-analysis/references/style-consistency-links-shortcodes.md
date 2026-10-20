<!-- Adapted from the Alloy analysis skill's link and shortcode checks, rewritten for Beyla. -->

# Style consistency: link check and shortcode validity check

## Link check

### Beyla conventions (baseline, 47 pages, 2026-10-20)

- **Inline links only.** No page uses reference-style definitions (`[label]: path`). Don't propose converting inline links to reference style.
- **Relative links ending in `/` are dominant** (about 95), for example `../service-discovery/`. No `{{< relref >}}` is used anywhere. Don't propose it.
- **Deviations from the generic style rule** ("relative links, end in `/`, not `.md`"):
  - Relative links to `.md` files (3): for example `./requesttime.md` in `_index.md` and `./configure/service-discovery.md#survey-mode` in `obi.md`. Propose the trailing-slash form.
  - Root-relative links that pin `latest`: `/docs/beyla/latest/configure/options/` in `cilium-compatibility.md`, `configure/export-data.md` (four lines), and `network/asserts.md`. Propose the relative form, which tracks the version of the page the reader is on.
  - Absolute `https://grafana.com/docs/...` links (10): in `obi.md`, `setup/kubernetes-helm-appolly.md`, and `setup/kubernetes-helm-k8s-monitoring.md`. Every one observed targets a **different** project (`grafana-cloud/...`, `alloy/latest/...`), not a Beyla page. Treat these as a lower-confidence finding: propose a relative path or `ref` only if it's verified to resolve in the shared Hugo site. Otherwise flag it as a question and leave the URL. An absolute link to a **Beyla** page is a clear finding.

### Relative-path resolution

Hugo renders `x.md` at `/x/` and `_index.md` at its directory's URL. So:

- From a non-index page (for example `configure/options.md` at `/configure/options/`), `../` is the **section** (`/configure/`) and `../../` is the site root.
- From a top-level non-index page (for example `metrics.md` at `/metrics/`), `../configure/...` reaches `/configure/...`. This is the pattern `metrics.md` already uses.
- From an `_index.md`, `./` is the section itself and `../` is its parent (for example `quickstart/_index.md` uses `../setup/`). The root `_index.md` uses `./distributed-traces/`.

Check sibling links in the same page before assuming a different convention. A top-level non-index page that uses `./configure/...` resolves to `/obi/configure/...`, which is wrong. Confirm, then propose the `../` form.

### Method

0. **Never assert that a page has no inline links, or no problem links, without running the check.** Run this and paste the output; an empty result is evidence, "I didn't notice any" isn't:

   ```bash
   F=docs/sources/<path>.md
   grep -noE '\[[^]]+\]\([^)]+\)' "$F"
   grep -nE '\]\([^)]*(\.md|https://grafana\.com/docs|/docs/beyla/latest)' "$F"
   ```

1. **Extract every internal link** (`[text](path)`) and image reference.
2. **Resolve each path from the file's own URL** (above) to a real target under `docs/sources/`: the directory's `_index.md` or `<name>.md`. A trailing-slash link `../service-discovery/` maps to `configure/service-discovery.md`.
3. **Check the real location, not just the alias.** A link that only works because the target page lists the path in `aliases:` is stale. Hugo doesn't 404 on it, but it no longer points at the real location. Propose the direct path. Check the target's front matter `aliases:` and, if unsure, `git log --follow --name-status` for a rename (read-only). Old Cloud-location URLs such as `/docs/grafana-cloud/monitor-applications/beyla/...` are aliases, so a link to one is stale.
4. **Check anchors.** Hugo slugifies headings (lowercase, hyphens). Confirm the `#fragment` matches a real heading in the target. Observed defect: `metrics.md:42` links `../configure/export-data/#metrics-export-features/`, with a trailing `/` after the fragment. The heading "Metrics export features" exists on `configure/export-data.md`, so the fix is `../configure/export-data/#metrics-export-features`. Also check that a renamed heading hasn't orphaned in-page `(#anchor)` links.
5. **Propose the exact corrected link**, never just "this link is stale."

### Link text and images

- Link text quality (no "click here"; prefer the target page's title): see `references/style-consistency-manual-checklist.md`.
- Cross-references use "refer to," not "see" or "consult" (`references/style-guide.md`).
- **Image alt text.** Every `![alt](src)` needs meaningful alt text describing the image (not "image" or the file name). The baseline has no empty-alt images. Flag a new one, or one with a useless alt, and propose text.
- Don't check that the image file exists or is current. That's out of scope.
- Check that expected cross-links exist where a reader would look for them (for example, a configure page referencing the options it builds on), only when a sibling does the same.

### Don't flag (link check)

- Link-definition ordering (Beyla has no reference-style links anyway).
- External third-party URLs that pin a branch or a line anchor (`references/dont-flag.md`).
- Anything inside a range suppressed on purpose, or generated content.

## Shortcode validity check

Validate shortcode use against `references/shortcode-schema.md`.

### Method

1. Extract every shortcode in the page, both delimiter forms (`{{< name ... >}}` and `{{% name ... %}}`). A bash check:

   ```bash
   grep -nE '\{\{[<%]' docs/sources/<path>.md
   ```

2. Look each name up in the schema. A name that isn't listed is a finding (a typo or a made-up name). Propose the closest real match, or flag it plainly.
3. Confirm required parameters are present (for example, `admonition` needs `type` with one of `caution`, `note`, `tip`, `warning`; `youtube` needs `id`).
4. Confirm every opening shortcode has a matching closing tag (`{{< /admonition >}}`, `{{< /fixed-table >}}`, `{{% /admonition %}}`).
5. **Delimiter consistency.** Beyla uses both `{{< admonition type="..." >}}` (8 uses) and `{{% admonition type="..." %}}` (5 uses). Sometimes both forms appear on the same page (`network/config.md`, `setup/kubernetes-helm.md`). Recommend **one** form consistently. The generic style guide and the shortcode reference use `{{< admonition >}}`, which is also the majority form here, so propose that and give the exact corrected lines. Don't call either form invalid. If a page uses `{{% %}}` because its inner content needs Markdown processing (a link or list inside the note), check that it really does before proposing the change, and say so.
6. **Deprecated or other-product shortcodes.** `docs/reference` is deprecated (prefer `ref` URIs or a direct relative link). If `docs/public-preview`, `docs/private-preview`, `docs/experimental`, `docs/shared`, or `param` shows up, nothing in Beyla's current docs uses them. Validate their parameters, then ask whether it's intended instead of assuming it's an error.
7. **Admonition content.** Use admonitions sparingly. Flag a page that stacks several, or one that wraps ordinary prose. Not an error: a note holding a real caveat.
8. `.vale.ini` ignores shortcode tokens, so Vale never reports a bad shortcode name. This check is the only coverage. (A `Grafana.Shortcodes` Vale rule appears in the baseline with 10 hits. Cite it when it applies, and still validate the shortcode yourself.)

### Don't flag

The schema lists shortcodes Beyla doesn't currently use. Their absence is never a finding, and their presence isn't wrong by default.

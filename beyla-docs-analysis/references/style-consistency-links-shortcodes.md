<!-- Adapted from the Alloy analysis skill's link and shortcode checks, rewritten for Beyla. -->

# Style consistency: link check and shortcode validity check

## Link check

### Beyla conventions (baseline, 47 pages, 2026-10-20)

- **Inline links only today.** The 2026-10-20 checkout has 401 inline text links and no reference-style links (counted with `scripts/check_source_format.py`). That's the current state, not the preferred style. The house preference is reference-style links; see "Link style: prefer reference-style links" below. Report the conversion as a style finding, not as an error.
- **Relative links ending in `/` are dominant** (about 95), for example `../service-discovery/`. No `{{< relref >}}` is used anywhere. Don't propose it.
- **Deviations from the generic style rule** ("relative links, end in `/`, not `.md`"):
  - Relative links to `.md` files (3): for example `./requesttime.md` in `_index.md` and `./configure/service-discovery.md#survey-mode` in `obi.md`. Propose the trailing-slash form.
  - Root-relative links that pin `latest`: `/docs/beyla/latest/configure/options/` in `cilium-compatibility.md`, `configure/export-data.md` (four lines), and `network/asserts.md`. Propose the relative form, which tracks the version of the page the reader is on.
  - Absolute `https://grafana.com/docs/...` links (10): in `obi.md`, `setup/kubernetes-helm-appolly.md`, and `setup/kubernetes-helm-k8s-monitoring.md`. Every one observed targets a **different** project (`grafana-cloud/...`, `alloy/latest/...`), not a Beyla page. Treat these as a lower-confidence finding: propose a relative path or `ref` only if it's verified to resolve in the shared Hugo site. Otherwise flag it as a question and leave the URL. An absolute link to a **Beyla** page is a clear finding.

### Link style: prefer reference-style links

**The preference.** Write text links in reference style, `[text][label]`, with the destination defined once as `[label]: destination`. Don't write them inline, `[text](destination)`. Reference style keeps sentences readable in the source, lets a destination be defined once and reused, and makes a link change a one-line edit.

**What this rests on.** The Writers' Toolkit Markdown guide describes both forms and doesn't require one. No Vale rule enforces either. So this is a house preference, and this check is the only coverage. Observed in the Alloy docs on 2026-10-20: far more reference-style than inline links (3,205 reference uses against 1,192 inline links, counted by pattern), with the in-page `#anchor` links left inline.

**What converts, and what doesn't.**

- **Convert** inline text links to other pages, to headings on other pages, and to external sites.
- **Leave inline:** in-page anchor links (`[text](#heading)`) and images (`![alt](src)`). This follows what the Alloy docs do, and it avoids churn. Say so in the finding so the person can widen the scope.
- Leave links inside fenced code and inline code alone.

**Labels and definitions.**

- **Label names:** lowercase, hyphenated, and named for the destination, not the link text (`stability-levels`, not `click-here`). Reuse one label for one destination. Never use the same label for two destinations.
- **Placement:** put all definitions in one block at the end of the page, in the order the labels first appear. Separate the block from the text with a blank line. Each definition is on its own line.
- **Proposed destination:** run the resolution method below first. A converted link's definition carries the corrected destination, not the stale one.
- **Links in tables** can be reference-style too.
- **Rewrite the whole sentence when you convert it.** The sentence also follows the line-break convention (one sentence per line). See `references/style-consistency-manual-checklist.md`, "Source line breaks."

**Admonitions: definitions go inside the block.** Every reference-style link used inside an admonition must have its definition **inside that same admonition**, after its content and separated by a blank line. Do this even when the same label is also defined at the end of the page or in another admonition. Duplicate definitions across blocks are intended, not a defect.

```markdown
{{< admonition type="note" >}}
Refer to [Service discovery][service-discovery] for the selection options.

[service-discovery]: ../service-discovery/
{{< /admonition >}}
```

Why: the website's admonition partial renders the block body with its own `RenderString` call (`website/layouts/partials/admonition.html`), so it doesn't see definitions placed elsewhere on the page. Observed in the Alloy docs on 2026-10-20: 55 admonition blocks define their links inside the block, and only a handful rely on page-level definitions. I didn't run a site build to confirm the rendering. The in-block placement is expected to work for both the `{{< admonition >}}` and `{{% admonition %}}` forms, but I haven't verified the `{{% %}}` form. The reverse also holds: page text outside an admonition must not rely on a definition that exists only inside one.

**Detection.** Run the checker and paste its output. An empty result is evidence; "I didn't notice any" isn't.

```bash
python3 <skill>/scripts/check_source_format.py <page.md> --links --lines
```

It reports, per page, the inline link count (each link with its line, tagged when it's inside an admonition), the reference-style uses and definitions, and any admonition reference problem: a reference used in a block with no definition in that block, or a page reference defined only inside a block. Treat the counts as approximate and read the lines you report.

**How to report.**

- Give the page's inline link count and a short list of the cases that need judgment (a link in an admonition, a link that was also stale).
- Show two or three representative conversions as before and after, and the full proposed definition block for the page.
- Say that the rest of the conversion is mechanical, and that doing it is a separate, large edit. Don't paste hundreds of rewrites into the report.
- Report an admonition reference problem as its own finding with the exact corrected block.

**Scope.** In delta mode, apply this only to links on added or changed lines. Pre-existing inline links elsewhere are a follow-up count. See `references/delta-pr-mode.md`.

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
   python3 <skill>/scripts/check_source_format.py "$F" --links
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

- The exact order of the definition block beyond "order of first use" (don't reorder an existing block that's consistent).
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
5. **Delimiter consistency.** Beyla uses both `{{< admonition type="..." >}}` (8 uses) and `{{% admonition type="..." %}}` (5 uses). Sometimes both forms appear on the same page (`network/config.md`, `setup/kubernetes-helm.md`). Recommend **one** form consistently. The generic style guide and the shortcode reference use `{{< admonition >}}`, which is also the majority form here, so propose that and give the exact corrected lines. Don't call either form invalid. If a page uses `{{% %}}` because its inner content needs Markdown processing (a link or list inside the note), check that it really does before proposing the change, and say so. A link in a `{{< admonition >}}` is fine when its definition is inside the block (see "Admonitions: definitions go inside the block" above).
6. **Deprecated or other-product shortcodes.** `docs/reference` is deprecated (prefer `ref` URIs or a direct relative link). If `docs/public-preview`, `docs/private-preview`, `docs/experimental`, `docs/shared`, or `param` shows up, nothing in Beyla's current docs uses them. Validate their parameters, then ask whether it's intended instead of assuming it's an error.
7. **Admonition content.** Use admonitions sparingly. Flag a page that stacks several, or one that wraps ordinary prose. Not an error: a note holding a real caveat.
8. `.vale.ini` ignores shortcode tokens, so Vale never reports a bad shortcode name. This check is the only coverage. (A `Grafana.Shortcodes` Vale rule appears in the baseline with 10 hits. Cite it when it applies, and still validate the shortcode yourself.)

### Don't flag

The schema lists shortcodes Beyla doesn't currently use. Their absence is never a finding, and their presence isn't wrong by default.

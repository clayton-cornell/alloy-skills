<!-- Written for Beyla; modelled on the Alloy analysis skill's front matter check. -->

# Style consistency: front matter check

Validate the page's front matter against `references/frontmatter-schema.md` (the Grafana-wide spec) **and** against what Beyla pages actually do. Every finding proposes the literal corrected front matter, not just "fix the title."

**Out of scope: `review_date`.** The field is valid, but this skill doesn't check whether a page has one or how old it is. A repo-wide absence isn't this page's finding. If a report must mention it, point to the separate documentation-freshness check. Absence of `labels` or `review_date` is **not** a finding (see `references/dont-flag.md`).

## Beyla baseline (all 47 pages, 2026-10-20)

Every page has `title`, `menuTitle`, `description`, `weight`, and `keywords` (a list). `aliases` appears on 17 pages. `cascade` appears only on the root `_index.md` (`cascade.labels.products: [oss]`). No page sets `labels`, `review_date`, `canonical`, or `topicType`. Quickstart pages quote the `title` in YAML, which is fine. Compare unquoted values.

## Checks

1. **Required fields.** `title` and `description` present. If one is missing, propose real text drawn from the page content, not a placeholder. Beyla's established shape also includes `menuTitle`, `weight`, and `keywords`, so flag a page that lacks one of them (propose the value) and say it matches what sibling pages have, not that the generic schema requires it.
2. **`title` equals the H1.** Compare the unquoted `title` with the page's first `# ` heading, ignoring a trailing space. `title` is the HTML `<title>` and should match the first heading and the URL slug. Mismatches observed in the baseline:
   - `configure/language-agents.md`: title "Configure Beyla language specific agents" vs. H1 "Language specific agents"
   - `configure/name-resolver.md`: title "Configure Beyla host name resolution" vs. H1 "Configure Beyla service host and peer name resolution"
   - `setup/kubernetes-helm-appolly.md`: title ends "...for Grafana Cloud", H1 ends "...for Grafana Cloud Knowledge Graph and Application Observability"
   - `setup/kubernetes-helm-k8s-monitoring.md`: H1 has a trailing space
   - `configure/example.md`: no H1 at all (the first heading is `## YAML file example`). Propose adding `# Beyla configuration YAML example` before it.

   Choose which side is right before proposing: prefer the more accurate, search-friendly wording, and under about 70 characters for the title. State which of the two you'd change and why. Don't rewrite both.
3. **`menuTitle` and `weight`.** `menuTitle` is the short sidebar label. Don't drop the verb from a task title's `menuTitle` unless the section implies it. Beyla uses small integer weights (`1`, `2`, `3`, and so on, and larger values such as `100` and `22`) with ties common (all `quickstart/` pages share weight `2`). That isn't the generic "increments of 100" guidance, so don't propose renumbering. Flag only a weight that places the page clearly out of order relative to its siblings, and mark it low confidence.
4. **`description`.** One or two sentences, real content, includes the product name. The generic guidance is at least 150 characters. Beyla descriptions are often shorter (for example, "Example Beyla configuration YAML example." on `configure/example.md`, which also repeats a word). Flag a description that is vague, repetitive, or not a full sentence, and propose a replacement. Don't flag length alone.
5. **`keywords`.** A list of single terms, such as `Beyla` and `eBPF`. Flag a missing or empty list, a string instead of a list, or a list of long phrases.
6. **`aliases` correctness for moved pages.** If the file was renamed or moved, check the history rather than guessing: `git log --follow --name-status -- docs/sources/<path>` (read-only). Confirm the previous URL path is present as an alias, and propose the exact entry when it's missing. Existing entries are absolute: `/docs/grafana-cloud/monitor-applications/beyla/...` (the old Grafana Cloud location) and a few `/docs/beyla/latest/...` entries. The generic spec asks versioned projects to use relative aliases with a path comment. Whether the Beyla site needs that is unverified, so raise it as a low-confidence question at most. Also check that an alias doesn't collide with another page's real URL.
7. **`draft` handling.** `setup/standalone.md` has `Draft: true` (capital D; Hugo front matter keys are case-insensitive, so Hugo reads it as `draft`). A draft page isn't published. Raise it as a **question** ("is this page meant to be unpublished?"), not as an error, and note that the lowercase spelling is conventional. Don't treat the page's content as a published page for audience or navigation findings unless the human confirms.
8. **`labels` and stability.** `labels.products` is inherited from the root `cascade`, so don't flag a missing `labels` on an individual page. If a page does set `labels.products`, the values must come from `cloud`, `enterprise`, `oss`. If it sets `labels.stage`, exactly one of `experimental`, `private-preview`, `public-preview`, `general-availability`. Check the stability claim itself against the source (SKILL accuracy step).
9. **`cascade` and `_build`.** `cascade` belongs on `_index.md` files only. Flag `cascade` or `_build` on a leaf page, unless a human confirms it's intentional.
10. **Field formatting.** No Markdown formatting in fields other than where documented. YAML is valid (a Vale or Hugo failure may hide a front matter parse error). A `title` that starts with a special character or contains a colon is quoted.

## Template-level question

Beyla pages don't use the generic `topicType` and `versionDate` fields (see `references/style-guide.md`'s "Beyla notes"). That's the local shape, shared by every page, so don't propose rewriting a page to add them. If it matters, raise it once as a template-level note, and don't repeat it per page.

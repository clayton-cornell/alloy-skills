# Completeness checklist (Step 4)

Goal: find supported, user-facing behavior in source that the page's scope
should cover but doesn't. Report only what source confirms; cite the source
`file:line` and say where in the page it belongs. Paths are relative to the
Beyla repo; `OBI/` means `vendor/go.opentelemetry.io/obi/` (write full paths in
findings). Apply the same open-before-citing rule as in `accuracy-checklist.md`.

## 1. Decide the page's scope first

Use the routing tables in `source-map.md` to name the source structs for the
page. A page's scope is its title and intro, not everything in the struct. A
`configure/` reference page should cover every user-facing field of its struct
section; a concept or quickstart page covers only what its stated purpose needs.
Write the scope in one sentence before enumerating.

## 2. Enumerate user-facing config for the scope

1. Open the struct(s) in full, following imported types into the vendored OBI
   (see `source-map.md`, "Where a setting is defined"). Nested types count.
2. List each field that has a `yaml:"..."` tag, plus its `env:"..."` tag. For
   OBI-typed fields the documented env var is the `BEYLA_` form of the
   `OTEL_EBPF_` tag (mapping in `pkg/beyla/config_obi.go`; see
   `accuracy-checklist.md`, 1.2). Fast alternative for a subtree, using the
   generated schema (corroborating index only, may lag the code):

   ```sh
   jq -r '."$defs".EBPFTracer.properties | keys[]' docs/config-schema.json
   jq -r '.properties | keys[]' docs/config-schema.json   # top-level keys
   ```

   The schema carries `x-env-var`, `enum` and `deprecated` annotations. It has
   no defaults. Confirm each item against the struct before reporting.
3. **Skip, and list under "Not counted":**
   - Fields with no `yaml` tag, `yaml:"-"`, or env-only test hooks (for example
     `TracesReceiver`, the cached `obi` field, `DisableUprobeMulti`).
   - The block under the comment "the properties below will remain
     undocumented" in `pkg/beyla/config.go` (`channel_buffer_len`,
     `channel_send_timeout`, `channel_send_timeout_panic`, `profile_port`, and
     `internal_metrics`). If the page already presents one as supported user
     configuration, verify it as normal instead of skipping it.
   - Experimental/undocumented: `injector` (SDK injection, `pkg/beyla/config.go`),
     `pkg/webhook/`; `sigil_export` unless a page presents it.
   - Fields documented in source as testing-only (for example
     `disable_black_box_cp`, "Used for testing purposes only") and anything the
     source comments mark development-only. Don't ask docs to cover them.
   - Unexported fields and internal plumbing types.
   - `Deprecated` fields: don't require a full entry, but check that the page
     marks them deprecated with the replacement if it mentions them at all, and
     that no example uses them (see "Deprecated items" below).
4. Look for options hidden outside the obvious struct: per-service blocks
   (`discovery.instrument[].exports|sampler|routes|metrics`,
   `OBI/pkg/appolly/services/attr_glob.go`), enum members of a type
   (`FeatureMapper`, `UnmarshalText` switches, trace printer values, TC
   backends, network sources), and Beyla-only sections (`pkg/services/criteria.go`:
   `survey`, `socket_apps`).

## 3. Compare against the page (coverage lookup recipe)

For each enumerated item, search `docs/sources/` three ways before declaring it
missing:

```sh
grep -rn 'wakeup_len' docs/sources                  # YAML key
grep -rn 'BEYLA_BPF_WAKEUP_LEN' docs/sources        # env var (BEYLA_ form)
grep -rni 'wake up length\|wakeup length' docs/sources   # plain-language name
```

Match semantic coverage, not just text: an option described in prose with a
different name still counts as covered. Record where it appears (page, line,
and whether it appears in a table, an example only, or prose only).

Classify each miss:

| Situation | Classification |
|---|---|
| Item in this page's scope and not mentioned here, but documented on another page | Gap in page: add a cross-reference, or the missing row if the page is the reference for that struct |
| Item in scope and nowhere in `docs/sources/` | Gap in page when the page owns that struct; otherwise a missing topic (record for the topic-level pass) |
| Item outside the page's stated scope | Not a gap on this page; note under Missing topic if nowhere documented |
| Documented but only in an example | Thinly covered: reference table row missing |
| Documented but marked deprecated in source with no deprecation note | Accuracy issue, not a completeness gap |
| Enum member or feature name missing from an otherwise complete list | Gap in page, name the exact member and its source line |

## 4. What a complete reference row needs

For a configuration reference page, each user-facing option should carry, as
the page's own convention requires: YAML key, env var (Beyla spelling), type,
default (the effective default from `accuracy-checklist.md` 1.3), accepted
values for enums, and a deprecation note when applicable. Report a missing
default or missing enum members as a gap; report a wrong one as an accuracy
issue.

Also check behavior a user needs that lives outside the table:

- [ ] Prerequisites and constraints that source enforces: required capability
      for a mode, kernel/BTF floor, `Validate` rules (at least one exporter,
      network and stats need a metrics exporter, only one span-metrics format).
- [ ] Interactions: an option that only takes effect together with another
      (for example a feature requiring an exporter, `network.source: tc`
      needing `CAP_NET_ADMIN`).
- [ ] Per-service vs global applicability.
- [ ] Platform differences (Kubernetes vs standalone vs Docker): chart or
      image values that change the effective default
      (`charts/beyla/values.yaml`, `charts/beyla/templates/`).
- [ ] Deprecated and removed options a user upgrading would still have in a
      config, with the replacement.

## 5. Deprecated items

Mark an item as deprecated when the field comment says `Deprecated:` or the
schema has `deprecated: true`, or `deprecatedFeatures` in
`OBI/pkg/export/feature.go` lists the feature. Report an example or table that
uses one without noting it. Propose the replacement from the source comment.

## 6. Examples and deployment pages

- [ ] An example that omits a setting source requires for it to work (an
      exporter, a capability, a `discovery` section) is a completeness gap.
- [ ] A setup page that mentions a Helm value or manifest field the chart
      doesn't have is an accuracy issue; a chart value that changes behavior
      and isn't mentioned on the page that owns the chart is a gap.

## 7. Topic-level gaps

For source behavior that no page covers, don't look page by page. Run the
topic-level pass defined in `triage-mode.md` ("Topic-level gap pass"): list the
top-level YAML sections and env-var groups from `pkg/beyla/config.go` and the
nested OBI types, plus `cmd/` binaries and `charts/` values, then use the
coverage-lookup recipe above for each against all of `docs/sources/`. Report
unmatched items as missing topics (with the source location and a suggested
home), mention-in-passing items as thinly covered, and list excluded
experimental/dev-only items under Not counted. State that this is a
keyword-coverage survey, not a page review.

In single-page mode, don't run the full topic-level pass. If an item you
enumerated has no coverage anywhere in `docs/sources/`, report it once as a
"missing topic" suggestion with source location, and leave the full survey to
the triage mode.

## 8. What not to flag

- Anything in the Skip list above.
- Generated-reference parity: don't ask a prose page to list every field the
  schema has.
- Internal metrics names and queue/channel tuning unless the page is the
  documented reference for them.
- If you can't tell whether something is user-facing, say so under Open
  questions instead of guessing.

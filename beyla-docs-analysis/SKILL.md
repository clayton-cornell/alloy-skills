---
name: beyla-docs-analysis
description: >
  Analyze a Grafana Beyla documentation topic for technical accuracy and gaps
  against the checked-out Beyla source. Use when asked to audit, review, or
  compare Beyla documentation with its implementation, especially configuration
  options, defaults, supported capabilities, and runtime behavior. This is a
  source-to-content review, not a Vale, style, or copyediting pass.
metadata:
  use_case: quality-review
  workflow: evaluate
---

# Beyla Docs Analysis

Act as a documentation-accuracy analyst. Use the current Beyla source checkout
and the documentation file under review as the evidence base. Don't rely on
memory, assumptions, or a newer upstream branch to establish behavior.

This skill performs a focused technical review of one documentation topic at a
time. It checks claims against source and identifies user-facing behavior the
page should document but omits. It does not run Vale, assess writing style or
audience, check links, or edit files. Keep those for separate passes.

Every finding must be actionable and supported by evidence. Cite the exact
documentation line and source file/line for confirmed discrepancies. Search
results alone aren't evidence: open the cited files and verify the surrounding
code before reporting a finding. If the source is unavailable or ambiguous,
state the limitation as an open question instead of guessing.

## Procedure

Work through these steps in order for one topic:

### 1. Intake and source mapping

1. Identify the topic file. If the user names a page or topic but not its path,
   locate it under `beyla/docs/sources/`.
2. Read the full topic and classify it by what it documents: overview or
   concepts, configuration, setup/deployment, language support, metrics,
   traces, network observability, or another scope.
3. Identify the claims that can be checked against implementation. Use
   [Source map](./references/source-map.md) to locate the relevant code.
4. Check that the source needed for the review is present in the current
   checkout. In particular, Beyla's `go.mod` can replace
   `go.opentelemetry.io/obi` with `./.obi-src`; if that submodule or other
   required source isn't available, don't silently substitute a newer
   upstream version.

### 2. Verify technical accuracy

Check each material, verifiable claim in the page against the closest
implementation evidence. Prioritize claims that change whether a user can
configure, deploy, or rely on the documented behavior:

- Configuration names, YAML keys, environment-variable names, types, defaults,
  precedence, validation, deprecation, and accepted values.
- CLI flags and configuration-file loading behavior.
- Supported operating systems, kernel versions, architectures, languages,
  protocols, and instrumentation modes.
- Exported signals, metric names, attributes, endpoints, and transport behavior.
- Runtime behavior, constraints, and stated limitations.
- Examples that encode configuration or expected output.

For configuration, follow the value through defaults, parsing, normalization,
validation, and any Beyla-to-OBI conversion that affects effective behavior.
An individual struct declaration may not establish the effective default or
runtime behavior.

Use tests as corroborating evidence, especially for edge cases, but don't treat
a test name or test fixture as proof of general behavior without examining what
the test exercises. If source code and documentation appear to disagree, trace
the relevant call path before concluding that the documentation is wrong.

### 3. Find documentation gaps

Compare the page's documented scope with relevant user-facing options and
behavior in the source. Report omissions only when the source confirms that the
capability is supported and the information is useful for a user of this page.
Check for:

- Missing supported configuration options, values, defaults, or environment
  variable mappings.
- Missing constraints, limitations, prerequisites, deprecations, or changed
  behavior that affects how users apply the feature.
- Missing supported modes, signals, protocols, or platform/language cases
  relevant to the page's stated scope.
- Examples that omit required configuration or imply unsupported behavior.

Don't treat every exported field as a documentation requirement. Exclude
internal, development-only, compatibility-only, and explicitly undocumented
fields unless the page already presents them as supported user configuration.
Distinguish a confirmed gap from an area the source doesn't let you verify.

### 4. Report

When the user asks for an overview across many pages, use
[Triage mode](./references/triage-mode.md) instead of the detailed report
below. Otherwise return a concise Markdown report with these sections, in this
order:

```markdown
# Analysis: <topic path>

## Summary
<What the page covers, review scope, and overall result.>

## Accuracy issues
<Each confirmed issue: documentation claim and line; source behavior and
file:line; proposed correction. State explicitly when none were found.>

## Completeness gaps
<Each confirmed omission: what is missing; source file:line; suggested place
in the page; proposed documentation content or a precise description of it.
State explicitly when none were found.>

## Open questions
<Claims that could not be verified and why, or "None." Name the missing source
or evidence needed to resolve each question.>
```

Keep accuracy issues (incorrect or misleading content) separate from
completeness gaps (supported information that is absent). Do not turn
unverified claims into findings. Include exact file and line references for
both sides of a confirmed discrepancy; for a gap, cite the relevant source and
identify where the documentation should cover it. Propose concise corrected
wording when the evidence supports it.

Do not expand the review into Vale, readability, style, links, or other
documentation checks unless the user explicitly asks for a separate pass.

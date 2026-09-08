<!-- Adapted from docs-ai/skills/docs-review/references/technical-verification.md. -->

# Technical verification: risk-tiered claim prioritization

Use this to decide *which* accuracy claims are worth the time to verify first
during Step 3, especially on long topics with many documented attributes.
Combine with the specific lookup method in `references/accuracy-checklist.md`
and `references/source-mapping.md` — this file is about triage order, not
where to look.

## 1. Identify verifiable claims

Read the topic and flag every statement that makes a factual claim about code
behavior: config option names, default values, numeric limits, syntax
examples, enum/allowed values, or stability/version claims.

## 2. Prioritize and verify

Not every claim is equally likely to cause damage if wrong. Prioritize by risk:

- **High risk** — Specific numbers (defaults, limits, sizes), attribute/block
  names and cardinality users will copy-paste, config examples. Divergence
  here breaks user configs directly. Always verify against source.
- **Medium risk** — Behavioral descriptions, stability-badge claims, claims
  about which upstream component is wrapped. Verify when possible; flag for
  human follow-up if the source is ambiguous (e.g., behavior lives in a
  vendored external package not present in this repo).
- **Low risk** — General prose describing well-established, unlikely-to-change
  behavior. Spot-check if time allows; don't let this block the report.

Within a topic, check in this order:
1. Anything with a specific number (defaults, limits, sizes, counts).
2. Attribute/block names and required-vs-optional status (typos/errors here
   break user configs).
3. Enum/allowed-value lists (stale entries are a common drift pattern).
4. Config examples that users will copy-paste verbatim.
5. Stability badges and wrapped-upstream-component claims.
6. General behavioral prose.

For each high- or medium-risk claim, read the relevant source file and confirm
it. If the source can't be located (e.g., it's in a vendored external Go
module, not this repo), flag it in the report's "Open questions" section
rather than assuming correctness either way.

## 3. Report findings

For each claim verified, note: the claim as written in the doc, what the
source actually says (with file:line), and whether they match or diverge.
Report divergences in the "Accuracy issues" section of the output format —
never silently downgrade a divergence to "Open questions" just because
verification was hard.

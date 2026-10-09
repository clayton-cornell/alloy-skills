<!-- Extracted from style-consistency.md. -->

# Style consistency: automated Vale linting (`make vale`)

Sources: `references/style-guide.md` and `references/verification-checklist.md`
(copied from `docs-ai/skills/shared/`), plus the general approach in
`docs-ai/skills/docs-review/SKILL.md` (read there once for context, not copied
verbatim since it's a full workflow, not a reference file).

## Automated linting: prefer `make vale`, not a raw `vale` call

For Alloy, the real local invocation is:

```bash
cd /home/ccornell/git-repos/alloy/docs
VALE_MINALERTLEVEL=suggestion make vale
```

**`VALE_MINALERTLEVEL=suggestion` is not optional — omitting it silently
hides most real findings.** Confirmed real, high-impact gap: `docs/make-docs`
defaults `VALE_MINALERTLEVEL` to `error` (`readonly VALE_MINALERTLEVEL="${VALE_MINALERTLEVEL:-error}"`),
which filters out every `suggestion`- and `warning`-level Vale rule — this
includes `Grafana.GoogleWill` ("avoid 'will'"), `Grafana.GooglePassive`
(passive voice), `Grafana.Acronyms`, and **all** `Grafana.Readability*`
metrics used by Step 2's audience assessment (see
`references/audience-signals.md`). A file with 20 real findings at the
default `error`-only level showed **zero** — not a rare edge case. This
matters because CI's actual check (`docs-ci` workflow, delegated to
`grafana/writers-toolkit`'s reusable `docs-ci.yml`, not this repo's own
`make-docs`) does **not** apply this restriction, so a locally-clean run at
the default level can still fail or get flagged in a real PR. Always set
`VALE_MINALERTLEVEL=suggestion` explicitly to match what CI actually
surfaces — never rely on the bare `make vale` default.

This pulls `grafana/vale:latest` via Podman/Docker (see `docs.mk`) and runs the
same Vale rules and dictionary as CI, scoped to the `PROJECTS` set in
`variables.mk`. This is the CI-equivalent result — prefer it over anything else.

**Caveat**: `make vale` lints the whole configured project, not a single file.
There's no per-file target in `alloy/docs/docs.mk` today. Run it and then find
this topic's findings in the output rather than expecting a scoped run. If a
scoped/per-file run turns out to be needed often, that's worth raising as a
`docs.mk`/`make-docs` improvement upstream in `writers-toolkit`, not something
to route around locally.

Because linting is repo-wide, a page-specific extraction can legitimately return
no matches even when `make vale` ran successfully; treat that as "no findings
for this page," not a command failure.

**Fallback only if Docker/Podman isn't available**: raw `vale` against
`writers-toolkit/.vale.ini`. If you fall back to this, treat any
`Grafana.Spelling` findings as unreliable — the standalone `vale` binary can't
parse the morphological dictionary entries and will flag correct product terms
(Grafana, Drilldown, etc.) as misspellings. Don't report these as real issues.

**If neither Docker/Podman nor a local `vale` install is available at
all**: this is a structured **skipped check**, not something to route
around silently or fabricate results for. Report "Automated Vale linting
skipped: neither Docker/Podman nor a local `vale` binary was found" in the
report's dedicated "Skipped checks" section (see SKILL.md's Output format)
— ideally caught during Step 0's upfront prerequisite check, not discovered
here. The manual style checklist (see `references/style-consistency-manual-checklist.md`)
still runs regardless, since it doesn't depend on either.

**Troubleshooting: `make vale` fails even though Docker is installed and
working.** `docs.mk` selects `podman` whenever the binary is merely
*present* on `PATH`, regardless of whether it actually works — a
broken/misconfigured Podman install still satisfies `command -v podman`,
so `docker --version` working is irrelevant. **A `PODMAN=docker` override
does not fix the run itself** — the `vale` target delegates to a separate
script (`make-docs`) that re-detects the runtime independently
(`make-docs:337` assigns `PODMAN` unconditionally rather than honouring an
inherited value) and overwrites any inherited `PODMAN` value, every time it
runs.

**`PULL=false` is the override that actually clears the
`Failed to obtain podman configuration ... read-only file system` error.**
The error fires during the image *pull*, which happens at the make level
(`docs.mk:95-98` runs `$(PODMAN) pull -q $(VALE_IMAGE)` only when `PULL` is
`true`, its default per `docs.mk:61-62`), not inside `make-docs`. Setting
`PULL=false` skips that step entirely, and the subsequent container run
succeeds against the already-cached image:

```bash
cd /home/ccornell/git-repos/alloy/docs
PULL=false VALE_MINALERTLEVEL=suggestion make vale
```

This requires `grafana/vale:latest` to already be present locally, so it
works as a recovery path on a machine that has run Vale before, not on a
cold cache. Adding `PODMAN=docker` alongside it is harmless but does nothing
for the run itself, for the reason above.

- **On first hitting the `Failed to obtain podman configuration ...
  read-only file system` error, retry `make vale` once, plain, with no
  override.** This signature can reflect a transient, stale
  rootless-Podman runtime state rather than a permanently broken install,
  and a bare retry has been observed to clear it.
- **If a plain retry doesn't clear it, try `PULL=false`** (with
  `VALE_MINALERTLEVEL=suggestion` still set) before treating this as a
  blocked check.
- **If the person is available, asking them to run `make vale` themselves
  once in a plain terminal is also a valid way to clear a stale state** —
  a plain, unprivileged command, not a toolchain change, so it doesn't
  conflict with this skill's never-touch-the-toolchain principle.
- **Only if the identical signature recurs after both a plain retry and
  `PULL=false`** should this be treated as a genuine, non-transient block.
  Report it as a skipped check with the specific error, note which overrides
  were attempted — then run the raw local `vale` fallback with its
  `Grafana.Spelling` caveat.
- **Mention once, not every run**, that a genuinely broken install can be
  repaired directly (e.g., checking `XDG_RUNTIME_DIR` points somewhere
  writable, or running Podman's own repair/reset tooling) — this skill
  never fixes it itself.

**Handling large output volume.** `make vale` lints the entire `alloy/docs`
project, not just the current topic, so its output can be very large.
Reading that full output directly into context risks the same failure this
skill already warns about with silent zero-output: a large/slow response can
look like a hang or a failure even when the underlying command actually
succeeded, and mistaking that for a real error is itself grounds for an
unwarranted, unnecessary fallback to raw local Vale (whose `Grafana.Spelling`
results are strictly worse — see below). Never judge success or failure by
output size or how long a response feels. Always:

1. Redirect to a file rather than reading raw stdout (see the capture command
   above).
2. Check the actual exit status immediately after (`echo "EXIT: $?"`) —
   this is the only authoritative success/failure signal, independent of
   output volume.
3. Only then extract this topic's findings from the file, e.g.
   `grep -F "<topic-file-name>" "$TMPDIR"/vale-out.txt`, rather than reading
   the entire file into context. A grep with no matches means no findings for
   this page (see below), not a failure.

**Troubleshooting: `make vale` produces zero output at all, not even an
error, when run from a VS Code–managed terminal.** Terminal capture in that
context can swallow output entirely, making a real failure look like
nothing ran. Don't treat silent zero-output as a pass. Redirect explicitly
instead of relying on terminal capture: `VALE_MINALERTLEVEL=suggestion make vale 2>&1 | tee "$TMPDIR"/vale-out.txt`, then
read the file directly and check the exit status separately if needed
(`echo "EXIT: $?"` immediately after the command, before running anything
else that would overwrite `$?`).

In sandboxed terminals, prefer `$TMPDIR` over `/tmp` for capture files. Some
environments mount `/tmp` read-only, which can create missing/empty capture
artifacts unrelated to Vale itself.

Don't treat non-zero `make vale` exit status as an infrastructure failure by
itself. A non-zero exit is expected when Vale reports lint findings somewhere in
the repo. Distinguish "lint findings present" from "command couldn't run."

Report every other Vale finding grouped by rule. Don't editorialize on rule
violations — they're either violations of the `Grafana` style package or they
aren't.

## Filter out the generated compatible-components block

**Every component reference page ends with a tool-generated block delimited
by `<!-- START GENERATED COMPATIBLE COMPONENTS -->` and
`<!-- END GENERATED COMPATIBLE COMPONENTS -->`. Nothing inside it is a
finding, for any check, ever.** It's generated from the compatibility
matrix, so a finding there is unactionable on the page — the only real fix
would be in the generator.

This matters most for Vale, because the block reliably produces the same
hits on every component page — `Grafana.GooglePassive` on "be consumed" is
the recurring one — and reporting them makes every component review look
noisier than it is.

**Filter by line range before reporting**, don't filter by eye:

```bash
F=docs/sources/reference/components/<path>.md
START=$(grep -n 'START GENERATED COMPATIBLE COMPONENTS' "$F" | cut -d: -f1)
END=$(grep -n 'END GENERATED COMPATIBLE COMPONENTS' "$F" | cut -d: -f1)
```

Then drop any finding whose line number falls between `$START` and `$END`.
If the page has no such markers, there's nothing to filter.

The same exclusion applies to the manual checks, not just Vale: single-item
lists, link style, and passive voice inside the block are all out of scope.
See `references/dont-flag.md`.

## Handling `Grafana.Spelling` findings specifically

Don't treat every `Grafana.Spelling` hit as "fix the word in the doc." The
rule itself (`writers-toolkit/vale/Grafana/styles/Grafana/Spelling.yml`)
flags any word absent from the compiled `en_US-grafana`/`en_US-places`
dictionaries — which includes both genuine typos **and** legitimate
Alloy/Grafana-domain terms nobody has added to the dictionary yet. Confirmed
real example: `Alloy` itself is already registered
(`word.new('Alloy', '', 'noun') { product: true }` in
`writers-toolkit/vale/dictionary/a.jsonnet`) — but plenty of other
Alloy-specific terms (specific integrations, coined terms, less-common
abbreviations) may not be.

**For each flagged word, decide which case applies before proposing a fix:**

1. **Genuine typo or misspelling** — propose the corrected spelling in the
   doc, same as any other Vale finding.
2. **Legitimate term missing from the dictionary** — signals this is likely
   the case: the word is a proper noun, a specific technology/product name,
   an abbreviation, or Alloy/Grafana-domain jargon (e.g. a coined verb like
   "downsample"); it's used deliberately and consistently, not as an
   isolated one-off; and it reads as intentional in context, not a slip.
   Propose adding it to the dictionary instead of changing the doc — don't
   just say "add to dictionary," draft the actual entry using the real
   format from `writers-toolkit/docs/sources/review/lint-prose/dictionary/add-words.md`:

   - **General word**: `word.new('<stem>', '<hunspell-affixes>', '<part-of-speech>') { description: '<definition, if not well known>' }`
   - **Product/technology name**: `word.new('<n>', '', 'noun') { product: true, description: '<link to primary docs>' }` (add `Amazon: true`, `Palantir: true`, etc. if it's a specific vendor's product, per the pattern already in `a.jsonnet`)
   - **Abbreviation**: `word.new('<ABBR>', '<plural-suffix-if-any>', 'noun') { abbreviation: true, description: '<expansion>', established_abbreviation: true }` (drop `established_abbreviation` if the abbreviation isn't widely known outside the reader's likely context)

   Note the target file: `writers-toolkit/vale/dictionary/<first-letter>.jsonnet`,
   entries kept alphabetical within the file — name the exact file and where
   in it the new entry goes, not just the entry text.
3. **This is a cross-repo proposal, not something this skill applies** —
   same "propose, don't apply" principle as everywhere else in this skill,
   but doubly true here since the fix lives in a different repo
   (`writers-toolkit`) entirely. Mention both paths `add-words.md` itself
   documents: submitting the change directly, or filing a GitHub issue
   against `writers-toolkit` for a maintainer to add it (the rule's own
   Vale message links both options).
4. **Only do this when running `make vale`, not the raw local fallback** —
   the fallback's `Grafana.Spelling` results are already flagged as
   unreliable above (can't parse the morphological dictionary entries), so
   don't propose dictionary additions from a run you already know produces
   false positives on correct terms.

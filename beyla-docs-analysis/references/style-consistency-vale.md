<!-- Adapted from the Alloy analysis skill's Vale method, rewritten for Beyla. -->

# Style consistency: automated Vale linting (`make vale`)

Sources: `references/style-guide.md` and the `Grafana` Vale style package. This is the CI-equivalent automated check, so prefer it over any manual substitute.

## Per-file run with severities (preferred for a single page)

`make vale` can't lint one file and doesn't print severity. Calling the same container directly does both. It mounts the docs read-only, so it can't modify anything:

```bash
mkdir -p <SCRATCH_DIR>
podman run --rm --workdir /etc/vale \
  -v <BEYLA_REPO>/docs/sources:/hugo/content/docs/beyla:ro \
  grafana/vale:latest --minAlertLevel=suggestion --output=JSON \
  /hugo/content/docs/beyla/<path-under-sources>.md > <SCRATCH_DIR>/vale-page.json
```

For example, `<path-under-sources>` is `configure/routes-decorator`. Use `docker run` with the same arguments when only Docker is available (not verified here).

The JSON is an object keyed by file path; each value is a list of findings with `Check` (rule), `Severity` (`suggestion`, `warning`, or `error`), `Line`, `Span`, `Message`, and `Match`. Group by `Check` and report the severity directly from `Severity`.

Verified 2026-10-20: for `configure/routes-decorator.md` this returned 31 findings, the same count `make vale` printed for that page, so the two paths agree. Both use the Vale config baked into the image, not the repo's root `.vale.ini`.

- Success means the output parses as JSON and has an entry for the file. A page with no findings returns `{}`; that's valid only after you've confirmed the container ran (no runtime error text on stderr).
- Don't judge the run by its exit code. It was `0` with findings in this check.
- `OUTPUT_FORMAT=json make vale` is **not** a substitute. It failed in this environment with `E100 [template] Runtime error ... open : no such file or directory`.

Use the whole-set `make vale` run (below) when you need the CI-equivalent run, the baseline sanity check, or when the per-file command isn't available.

## Run the whole set with `make vale`

Run from the Beyla `docs` directory and always set the alert level:

```bash
cd /home/ccornell/git-repos/beyla/docs
VALE_MINALERTLEVEL=suggestion make vale > <SCRATCH_DIR>/vale-out.txt 2>&1
echo "EXIT: $?"
```

Use a scratch directory your environment allows writing to: `$TMPDIR` if it's set, otherwise a session scratch directory. Never write inside the Beyla repo or the skill. Some sandboxes mount `/tmp` read-only and produce empty capture files. Redirect to a file, don't read raw stdout into context.

**`VALE_MINALERTLEVEL=suggestion` is not optional.** `docs/make-docs` defaults it to `error` (`readonly VALE_MINALERTLEVEL="${VALE_MINALERTLEVEL:-error}"`) and passes it to Vale as `--minAlertLevel`. At that default, every `suggestion`- and `warning`-level rule is hidden. That includes `Grafana.GooglePassive`, `Grafana.Parentheses`, `Grafana.Acronyms`, `Grafana.GoogleWill`, and all the `Grafana.Readability*` metrics that feed the audience assessment. Beyla's root `.vale.ini` sets `MinAlertLevel = warning`, but the `make` target's flag is what takes effect locally. Never rely on a bare `make vale`.

What CI applies: `.github/workflows/vale.yml` runs on pull requests that touch `docs/sources/**`, in a pinned `grafana/vale` container, through `grafana/writers-toolkit/vale-action`. **Which minimum alert level that action applies is unverified**, so don't claim a suggestion-level finding fails CI. See "Alert level" below.

`make vale` pulls `grafana/vale:latest` through the container runtime (podman or Docker) and lints **all** pages under `docs/sources/` (47 at the time of writing). There's no per-file target. A run takes about 20 seconds.

## Exit-code semantics (differs from the Alloy skill)

`make vale` exits **non-zero (observed: 2)** whenever Vale reports any finding, and the last line is `make: *** [docs.mk:98: vale] Error 1`. So:

- **Non-zero exit with finding lines present = a successful run with findings.**
- **Success** is either finding lines in the pattern below, or a clean empty finding set with no runtime error.
- **Failure** is a runtime/image error message (podman or Docker errors, `Failed to obtain podman configuration`, an image pull failure) **and no finding lines**.

Finding-line pattern, one finding per line, no severity shown:

```text
sources/<relative-path>:<line>:<col>:<Rule>:<message>
```

Don't judge success by output volume or how long the run felt. Don't treat zero output as a pass: confirm the run was real by checking that finding lines exist for other pages (the baseline has findings on every page, including the readability metrics at line 1). A zero-output run with no error text is a suspected capture problem (for example, a VS Code terminal swallowing output). Re-run with `2>&1 | tee <SCRATCH_DIR>/vale-out.txt` and read the file.

**Noise lines to ignore** (harmless):

- `sed: can't read .../.github/workflows/doc-validator.yml` (Beyla has no doc-validator workflow, so the make variable fails harmlessly)
- `podman pull -q grafana/vale:latest` and `DOCS_IMAGE=... make-docs beyla`
- an image hash line
- `level=warning msg="The input device is not a TTY..."`
- the trailing `make: *** [docs.mk:98: vale] Error 1`

## Extract one page's findings

```bash
grep -F 'sources/configure/options.md:' <SCRATCH_DIR>/vale-out.txt
```

Use the full path from `sources/` (a bare file name such as `options.md` or `_index.md` collides across directories). A page with no matches has no findings. That's valid only after you've confirmed the run produced findings for other pages. Group a page's findings by rule: add `| cut -d: -f4 | sort | uniq -c | sort -rn`.

Report findings grouped by rule, with line numbers, current text, and the proposed corrected text. Don't editorialize about whether a rule is a good rule.

## Alert level

The whole-set line output doesn't print severity. The per-file JSON run (above) does, in `Severity`, so use it whenever you need levels. If you only have the line output, a rule's level lives in the `Grafana` style package inside the Vale image: report it only if you looked it up, otherwise mark the level "unknown" in the report. **Don't guess.**

Not verified: which minimum level CI applies through `grafana/writers-toolkit/vale-action`. Don't claim a `suggestion`-level finding fails CI.

## Baseline (2026-10-20, suggestion level, whole docs set)

1,452 finding lines across all 47 pages: `GooglePassive` 324, `Parentheses` 224, `Acronyms` 149, `Spelling` 126, `GoogleContractions` 109, `FirstPersonPlural` 63, `Timeless` 51, `GoogleWill` 42, `ProductPossessives` 16, `Simple` 15, `Shortcodes` 10, `GoogleSemicolons` 9, `Kubernetes` 8, plus 7 readability metrics × 47 pages. Use this to sanity-check a run: a page with a handful of findings is normal. A whole run of 0 or a count wildly different from this isn't automatically wrong, but check for a tool failure or a docs change first.

## Readability metrics

Vale reports readability as findings at **line 1, column 1**, once per page per metric: `Grafana.ReadabilityColemanLiau`, `ReadabilityFleschReadingEase`, `ReadabilityFleschKincaid`, `ReadabilityGunningFog`, `ReadabilitySMOG`, `ReadabilityLIX`, `ReadabilityAutomatedReadability`. Pull them with:

```bash
grep -F 'sources/<path>:1:1:Grafana.Readability' <SCRATCH_DIR>/vale-out.txt
```

They feed the audience assessment step. They aren't defects to fix individually. Don't list them as style findings, and don't escalate a poor score on a page whose density is inherent (see `references/dont-flag.md`).

## Suppression comments

Pages contain `<!-- vale <Rule> = NO -->` / `= YES` comments. Vale honors them, so findings for that rule inside the range don't appear. Don't re-flag the suppressed rule. Do flag a suppression that is broader than needed. See `references/dont-flag.md`.

## Handling `Grafana.Spelling` findings

Don't treat every `Grafana.Spelling` hit as "fix the word in the doc." The rule flags any word absent from the compiled `en_US-grafana` dictionaries. That covers genuine typos **and** legitimate domain terms nobody has added yet. Beyla's docs have no dictionary file of their own, so entries live in `writers-toolkit/vale/dictionary/<first-letter>.jsonnet` (a different repository). In the 2026-10-20 baseline, the distinct flagged words included `instrumentable` (15), `Uncompress` (7), `Daemonset` (4), `CIDRs` (2), `interoperates` (2), `uninstrumented`, `instrumenter`, `unencrypted`, `ringbuffer`, `qdisc`, `rdns`, `JVMs`, `eksctl`, `sudo`, and lowercase `kubernetes`, `statefulset`, `replicaset`, `daemonset`, `dns`, `otel`, `config`. `eBPF`, `OBI`, and `cgroup` weren't flagged in that run.

Decide which case applies to each word before proposing a fix:

1. **Genuine typo, wrong capitalization, or unformatted code** — propose the corrected text in the doc. Examples: lowercase `kubernetes`, `dns`, `otel` in prose become "Kubernetes," "DNS," "OpenTelemetry," and if the word is really a config key or command it needs code formatting instead; "Daemonset" should be "DaemonSet" (Kubernetes object names are capitalized, which `Grafana.Kubernetes` also covers); "Uncompress" is a verb the dictionary lacks, so propose "Decompress" or "Extract." Read the line first to pick the right fix.
2. **Possessive of a product name.** `Beyla's` and `Grafana's` surface as `Grafana.Spelling` hits in the baseline, and `Grafana.ProductPossessives` covers the same text. Fix the wording once (avoid the possessive, for example "the view that Beyla provides"), and don't report it twice.
3. **Legitimate term missing from the dictionary** — the word is a proper noun, a technology name, an abbreviation, or domain jargon, used deliberately and consistently (for example `instrumentable`, `qdisc`, `CIDRs`). **Propose a dictionary entry, not a doc edit**, and draft the entry in the real format from `writers-toolkit/docs/sources/review/lint-prose/dictionary/add-words.md`:
   - General word: `word.new('<stem>', '<hunspell-affixes>', '<part-of-speech>') { description: '<definition, if not well known>' }`
   - Product/technology name: `word.new('<name>', '', 'noun') { product: true, description: '<link to primary docs>' }`
   - Abbreviation: `word.new('<ABBR>', '<plural-suffix-if-any>', 'noun') { abbreviation: true, description: '<expansion>', established_abbreviation: true }` (drop `established_abbreviation` if it isn't widely known)
   
   Name the target file (`writers-toolkit/vale/dictionary/<first-letter>.jsonnet`) and note that entries stay alphabetical. Mention both routes the rule's own message links to: submit the change directly, or file a `writers-toolkit` issue for a maintainer.
4. **This is a cross-repo proposal.** This skill doesn't apply it.
5. **Only propose dictionary additions from a real `make vale` run.** Raw-`vale` fallback `Grafana.Spelling` results are unreliable (below).

The spell checker ignores bold text, inline code, and fenced code (the rule message says which formatting). A word wrapped in backticks isn't a Spelling finding.

## Fallbacks and skipped-check wording

- **Container runtime broken.** `docs.mk` selects `podman` whenever the binary is on `PATH`, and `make-docs` (line 337) re-detects the runtime itself, so a `PODMAN=docker` override doesn't help. Sequence: (1) on `Failed to obtain podman configuration ... read-only file system`, retry `make vale` once, plain, since stale rootless-Podman state sometimes clears; (2) then try `PULL=false VALE_MINALERTLEVEL=suggestion make vale`, which only helps if the failure was the pull step and the image is cached; (3) a person can run `make vale` in a plain terminal to clear stale state; (4) only if the same error recurs after all of that, treat it as a genuine block. Mention once that a broken install can be repaired (for example, check `XDG_RUNTIME_DIR` is writable, or use Podman's reset tooling). This skill never fixes it.
- **Raw `vale` fallback** (no container runtime, local `vale` present): it needs the `Grafana` style package from `writers-toolkit/vale` available (Beyla's `.vale.ini` only names `BasedOnStyles = Grafana`; how the package is supplied locally is unverified). Treat `Grafana.Spelling` from this path as unreliable, because the standalone binary can't parse the morphological dictionary entries and flags correct terms. Don't report those as real issues.
- **Neither is available.** This is a structured **skipped check**. Report: "Automated Vale linting skipped: neither a container runtime (podman/Docker) nor a local `vale` binary was found." Put it in the report's skipped-checks section. Don't fabricate results. The manual checklist (`references/style-consistency-manual-checklist.md`) still runs.
- **Runtime error, no findings.** Report: "Automated Vale linting skipped: `make vale` failed with `<exact error>` (plain retry and `PULL=false` attempted)."

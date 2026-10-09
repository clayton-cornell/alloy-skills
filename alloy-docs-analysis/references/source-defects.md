<!-- Added from repeated real findings across the remote.*/pyroscope.*/prometheus.* audits. -->

# Source defects: when the code is wrong and the doc can't fix it

Use this when Step 3 (accuracy vs. source) finds that the doc is right and
the **code** is wrong, or that the doc describes something the code cannot
actually do. These aren't accuracy issues in the normal sense — there's no
doc edit that makes the page both true and useful — so they get their own
handling and their own output section.

## What counts as a source defect worth reporting

Functional bugs only. Confirmed real examples of each shape:

- **Crash paths** — an argument tagged `optional` whose omission reaches an
  unguarded slice index.
- **Arguments plumbed but never read** — the value reaches a config struct
  that nothing downstream consumes.
- **Gates that can never be satisfied** — an argument's effect is guarded by
  a second value Alloy never sets, so the feature is permanently inert.
- **Defaults set on one path but not the Alloy path** — a static/YAML path
  gets a real default via `UnmarshalYAML`, while `DefaultArguments` omits the
  field and leaves a zero value.
- **Values discarded in conversion** — a job type passes literal zeros where
  sibling job types pass the configured values.
- **Metrics derived from the wrong quantity** — two counters incremented from
  the same underlying value, so one of them measures something other than its
  name.
- **Validation under the wrong condition** — a check placed under the wrong
  `case`, so it never runs for the input it was written for.
- **Converter field loss** — a `to*` conversion silently drops fields.
- **Labels that never materialise** — a non-nil empty map passed where the
  downstream code only populates on `nil`.

## What does NOT count

- Stale or wrong **source comments**, including package comments naming the
  wrong upstream module. Zero runtime effect, so don't mention them.
- **Identifier or metric naming** inconsistencies with no behavioural
  consequence (for example, a metric emitted by one component carrying
  another component's prefix). These are at most a note in "Open questions,"
  never a defect.
- Anything you'd have to speculate about. See the verification bar below.

## Verify before reporting

1. **Trace the whole path**, from the Alloy argument through `Convert()` into
   the vendored upstream module, to the point where the value is actually
   read (or isn't). A defect claim that stops at "Alloy sets this field" is
   not verified.
2. **Name a file and line for every hop.** If you can't get a line number for
   some hop, say so explicitly in the finding rather than guessing one. An
   invented line number is worse than an acknowledged gap.
3. **Prove the negative properly.** "Alloy never sets X" needs an actual
   repo-wide search for X, plus a count of the fields the construction site
   does set, not an impression from reading one function.
4. **Use an empirical check when source-reading can't settle it** — see
   `references/technical-verification.md`'s throwaway-program technique.

## Decide the doc's disposition with the person, never unilaterally

Three outcomes have all been chosen in practice, and which one applies is the
person's call, not yours. Present the options:

1. **Leave the doc unchanged** — it becomes correct the moment the source is
   fixed. Chosen where the description was already accurate about intent. Do
   not add a "currently has no effect" note in this case, and do not re-raise
   it as a doc finding on later reviews of the same page.
2. **Correct the doc to describe current behaviour**, and record explicitly
   that the text must be **reverted** when the source is fixed. Chosen where
   the doc claimed something that simply never happens.
3. **Keep a doc guard** that stops readers hitting the bug. Chosen where a
   doc saying an argument is required is the only thing preventing a crash.
   **Never "correct" a doc toward the buggy behaviour** when doing so would
   expose users to a panic or data loss.

Whichever is chosen, state the **revert condition** in the finding, so a
later reviewer doesn't read the workaround as the intended wording.

## Carry the finding forward to PR time

Source defects are easy to lose between discovery and filing — the doc work
finishes, the PR gets written, and the defect never leaves the transcript.
Confirmed real: two verified defects were recorded against a branch and that
branch's PR merged without either of them being raised.

So: when a source defect is found, say plainly that it needs a home outside
this page (a tracking issue or a fix PR), and surface it again unprompted
when the person mentions preparing, titling, or finishing the PR for that
work.

## GenAI policy boundary

Per Alloy's `docs/developer/genai.md` and `.github/pull_request_template.md`:

- **You may** describe the defect in analysis output, write the PR *title*,
  and fill PR template sections not marked `HUMAN ONLY`.
- **You may not** draft issue bodies, `HUMAN ONLY` PR sections, or review
  replies, and may not open issues or PRs.

If asked to do any of the second group, refuse that part explicitly in your
reply and point at `docs/developer/genai.md` — then carry on with the parts
you can do.

## Output

Report these under their own `## Source defects` heading, separate from
`## Accuracy issues`, with: component, the argument/metric/behaviour
affected, root cause with file:line per hop, the doc disposition chosen and
its revert condition, and a confidence statement naming what was verified
against source versus inferred.

# Accuracy checklist: log-message text (troubleshoot/debug.md and similar)

A distinct claim-type from the other accuracy-checklist files: exact
`level=X msg="..."` strings presented as real log output. **This turned out
to be a genuinely inaccurate category, not just a theoretical one** —
verified against real source:

- Confirmed **accurate**: `discovery.process`'s warning
  (`internal/component/discovery/process/process_stub.go`, exact string
  match, including level) and `"config reloaded"`
  (`internal/service/http/http.go`, exact match).
- Confirmed **not found as written**: `troubleshoot/debug.md` quotes
  `"starting server"` and `"terminating server"`, but
  `internal/service/http/http.go`'s actual messages for the same events are
  `"now listening for http traffic"` (with an `addr` field) and no explicit
  shutdown log line at all. It also quotes `"started scheduled components"`,
  but `internal/runtime/internal/controller/scheduler.go`'s actual messages
  are `"node exited with error"`/`"node exited without error"` and `"task
  shutdown is taking longer than expected"`. These read like illustrative
  paraphrases of what a log might look like, not verbatim quotes — which is
  a real problem if the page presents them as exact `msg=` output a reader
  could grep for.
- Confirmed **level mismatch**: `"discovered peers"` is documented as
  `level=info`, but the actual call
  (`internal/service/cluster/cluster.go`'s `getRandomPeers`) is
  `s.log.Debug("discovered peers", ...)` — real text, wrong level. Same
  category of bug as a wrong message string: report it, don't wave it off
  as "close enough because the text matches."

## Cluster messages are locally verifiable

**Don't assume cluster-related messages originate in the external
`github.com/grafana/ckit` module** — confirmed directly that the large
majority of what `debug.md` actually quotes are defined in this repo's own
`internal/service/cluster/` package instead. The text and log level
of `"starting cluster node"`, `"failed to get peers to
join at startup; will create a new cluster"`, `"failed to connect to peers;
bootstrapping a new cluster"`, `"failed to bootstrap a fresh cluster with no
peers"`, `"failed to refresh list of peers"`, `"failed to rejoin list of
peers"`, `"rejoining peers"`, `"minimum cluster size reached, marking
cluster as ready to admit traffic"`, `"minimum cluster size requirements are
not met - marking cluster as not ready for traffic"`, `"deadline passed,
marking cluster as ready to admit traffic"`, `"using provided peers for
discovery"`, `"found an IP cluster join address"`, `"received DNS query
response"`, and `"failed to resolve provided join address"` are **all**
defined in this repo's own `internal/service/cluster/` package, not in
`ckit`:

| Message | Source |
|---|---|
| `"starting cluster node"`, `"failed to connect to peers; bootstrapping a new cluster"`, `"failed to bootstrap a fresh cluster with no peers"`, `"failed to get peers to join at startup; will create a new cluster"`, `"failed to refresh list of peers"`, `"failed to rejoin list of peers"`, `"rejoining peers"` (via `logPeers`) | `internal/service/cluster/cluster.go` |
| `"discovered peers"` | `internal/service/cluster/cluster.go`'s `getRandomPeers` — **Debug**, not Info as documented |
| `"minimum cluster size reached..."`, `"minimum cluster size requirements are not met..."`, `"deadline passed, marking cluster as ready..."` | `internal/service/cluster/cluster_readonly.go` |
| `"using provided peers for discovery"` | `internal/service/cluster/discovery/peer_discovery.go` |
| `"found an IP cluster join address"`, `"received DNS query response"`, `"failed to resolve provided join address"` | `internal/service/cluster/discovery/join_peers.go` |

**What's still genuinely out of reach**: the actual gossip/membership
protocol internals inside the `github.com/grafana/ckit` module itself (peer
state transitions inside `ckit.Node`, low-level SWIM-style messages) — if a
doc claim is specifically about `ckit`'s own internal behavior rather than
how Alloy's `cluster` service logs around it, that's still the one
legitimate case for "not locally inspectable, flag as open question." But
don't use that as a blanket excuse to skip the whole "Cluster operation
messages" section — check `internal/service/cluster/` and
`internal/service/cluster/discovery/` first; only fall back to "can't
verify" for something that traces genuinely into `ckit` itself.

## Method

1. Extract every literal `msg="..."` string the doc presents as real output.
2. **Use `grep`/`rg` across the repo** (available via the Bash tool in Claude
   Code, unlike the remote session used to build this checklist, which had
   to read whole candidate files one at a time) — e.g.
   `grep -rn '"config reloaded"' internal/ syntax/ collector/`. This is far
   more reliable than guessing which subsystem file might contain it; don't
   skip straight to reading a likely-looking file without trying the exact
   string first.
3. **A grep hit is not itself a confirmed citation — open the file and
   confirm it before citing it.** Confirmed real failure, and a serious
   one: a run cited a specific file:line for a `msg="module content
   loaded"` match, reported it as a confirmed finding, and the cited file
   turned out not to exist anywhere in the repo at all — a fabricated
   citation, accepted from a grep result without independently checking
   that the path resolved. This is a stricter standard than "the grep
   returned a match": before writing a file:line into the report, actually
   open that file and confirm (a) it exists, and (b) the surrounding
   context at that line is genuinely what the grep snippet made it look
   like. **A grep result whose cited path doesn't resolve is a false
   positive, not weaker evidence — treat it as no evidence at all**, not as
   a lower-confidence version of a real finding. If this happens, the
   correct outcome isn't "downgrade the confidence of an Accuracy issue" —
   it's moving the claim to "Open questions" entirely, since its real
   status (a paraphrase of some other real message, or genuinely invented)
   is now unknown, not just uncertain.
   - **A vague category description is not a citation either, even if it
     sounds plausible.** Confirmed real, softer version of the same
     failure on a later run: a claim that a message "is health Message
     text, not a logger call" or "is testcomponent health text" was
     offered as a resolved status change, but without an exact file:line
     — and direct verification of the most plausible real candidate files
     found no matching string in either case. Don't let a claim shift from
     "open question" to "resolved" (in either direction — confirmed or
     inaccurate) unless it comes with the same exact file:line rigor as
     any other citation. "I found something that seems like the right kind
     of thing" is not "I found and confirmed the specific line." If you
     can't produce an exact citation, the claim stays exactly where it was.
4. If found (and independently confirmed per step 3): confirm the log
   **level** (Info/Warn/Error/Debug) matches too, not just the message
   text — a message at the wrong level is still wrong.
5. If not found verbatim anywhere in the repo: don't assume it's "close
   enough." Report it as an accuracy issue — either propose the real message
   text from the closest matching real log call you did find (cite it), or
   flag it explicitly in "Open questions" if no close match exists at all.
6. **This category doesn't need exhaustive coverage to be worth running** —
   given how many quoted messages a page like `troubleshoot/debug.md` can
   have, verify a representative sample (3–5 messages, prioritizing ones
   tied to specific technical claims over generic ones) and say explicitly
   in the report which were checked and which weren't, rather than silently
   skipping the whole category or claiming full coverage you didn't do.

## What NOT to attempt

**Narrower than a naive "skip anything cluster-flavored" rule.** Cluster
messages are, in the large majority of cases, verifiable directly in
`internal/service/cluster/` and `internal/service/cluster/discovery/`; check
those first. The only remaining off-limits case is a claim specifically
about `github.com/grafana/ckit`'s own internal gossip/membership behavior
(imported in `cluster.go`), where the actual implementation lives in a
vendored module rather than this repo. If a specific claim genuinely traces
there and `ckit`'s source isn't locally inspectable (e.g., not in the Go
module cache), say so rather than fabricating a verification — but this is
now the narrow exception, not the default assumption for anything
cluster-flavored.

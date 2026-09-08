# Accuracy checklist: packaging/deployment pages (set-up/install/*.md, set-up/run/*.md, configure/*.md)

See `references/source-mapping-packaging.md` for where each fact lives
across `packaging/` and the `Dockerfile`s. Checklist:

**Time-budget note**: packaging pages tend to be shorter than component
reference pages with a more direct source mapping (non-Go config files
rather than a Go struct to walk exhaustively) — confirmed across two field
runs, this step (Step 3, accuracy) is usually where nearly all the real
value is on a packaging page (one wrong path is a high-severity, easy-to-spot
bug), while Step 4 (completeness) tends to be quick with little to find.
Weight time accordingly rather than budgeting evenly across both steps the
way a component reference page usually warrants.

- [ ] Default CLI flags a page claims the *packaged service* passes (e.g.
      `--storage.path`) match the actual `ExecStart`/`CMD` line in the
      relevant systemd unit or Dockerfile — **not** the CLI's own built-in
      default from `cmd_run.go`. These are frequently different values on
      purpose (packaging overrides the binary default); confirmed real gap:
      `configure/linux.md` states `--storage.path=/var/lib/alloy` but the
      systemd units and Dockerfile all agree on `/var/lib/alloy/data`.
- [ ] Environment file path claims (`/etc/default/alloy` vs.
      `/etc/sysconfig/alloy`) match the `EnvironmentFile=` line in the
      correct platform's systemd unit — don't assume both platforms share
      one file.
- [ ] Environment variable names/defaults (`CONFIG_FILE`, `CUSTOM_ARGS`)
      match `packaging/environment-file`.
- [ ] Directory/path claims distinguish the service home directory from the
      data/storage directory when source does (e.g. `/var/lib/alloy` vs.
      `/var/lib/alloy/data`) — don't collapse them into one path from memory.
- [ ] Windows paths match `packaging/windows/install_script.nsis` — install
      directory vs. data directory are different registry/filesystem
      locations, same principle as the Linux home-vs-data distinction.
- [ ] Container-specific claims (non-root UID, default `CMD`, exposed ports)
      match `Dockerfile`/`Dockerfile.windows` directly, not assumed from the
      Linux packaging story.
- [ ] macOS/Homebrew: any instruction describing how to pass extra CLI
      arguments to the *packaged service* (not a direct `alloy run` foreground
      invocation) must route through the Homebrew wrapper's actual override
      mechanism, not a literal edit to a service command/plist. **Confirmed
      real, current mechanism** (`packaging/homebrew/alloy.rb.tpl` and
      `packaging/homebrew/service-wrapper-gen/wrapper.tpl`, cross-checked
      against both golden testdata files): the Homebrew formula installs an
      `alloy-wrapper` shell script as the actual `brew services`-managed
      process; that wrapper reads extra arguments from `#{pkgetc}/extra-args.txt`
      (or `otel-extra-args.txt` when `ALLOY_OTEL_MODE` is set), appends them
      unquoted to the `alloy run`/`alloy otel` invocation it constructs
      itself, and separately sources `#{pkgetc}/config.env` for environment
      variables. `pkgetc` resolves to the Homebrew prefix's `etc/<formula-name>`
      (e.g. `/opt/homebrew/etc/alloy` per the `grafana.golden.sh` testdata).
      A doc instructing the reader to directly edit a systemd-style
      `ExecStart` line, a plist, or any other service-definition file on
      macOS/Homebrew is describing a mechanism that doesn't exist for this
      package manager — propose the `extra-args.txt`/`config.env` path
      instead, citing the exact wrapper behavior above.

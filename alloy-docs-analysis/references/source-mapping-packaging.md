# Mapping doc topics to source: packaging/deployment pages

Covers `set-up/install/*.md`, `set-up/run/*.md`, `configure/*.md`. Maps to the
top-level `packaging/` directory and `Dockerfile`/`Dockerfile.windows` — a
third kind of source entirely (shell scripts, systemd units, NSIS installer
script), not Go source at all.

## Where each claim type lives

| Doc claim | Source |
|---|---|
| Linux systemd service name (`alloy`/`alloy.service`), `ExecStart` default flags | `packaging/deb/alloy.service`, `packaging/rpm/alloy.service` |
| Linux environment file location (Debian/Ubuntu vs. RHEL/SUSE) | Same two files' `EnvironmentFile=` line: `/etc/default/alloy` (deb) vs. `/etc/sysconfig/alloy` (rpm) |
| `CONFIG_FILE`/`CUSTOM_ARGS` env var names and defaults | `packaging/environment-file` (the template installed as the env file above) |
| Linux user/group, home dir, data dir creation/permissions | `packaging/deb/control/postinst` (and `prerm`); confirms `/var/lib/alloy` (home) vs. `/var/lib/alloy/data` (storage path) are different directories — don't conflate them |
| Docker image contents, default `CMD`, non-root UID | `Dockerfile` (Linux), `Dockerfile.windows` (Windows containers) |
| Windows native install paths (`Program Files`, `ProgramData`, registry `Arguments` key) | `packaging/windows/install_script.nsis` — install dir is `$PROGRAMFILES64\GrafanaLabs\Alloy`, data dir is `$APPDATA\GrafanaLabs\Alloy\data` (resolves to `C:\ProgramData\...` under `SetShellVarContext all`) |
| Homebrew formula (macOS) | `packaging/homebrew/alloy.rb.tpl` and `formula-gen/`/`service-wrapper-gen/` |
| Homebrew/macOS extra-CLI-args override mechanism for the packaged service | `packaging/homebrew/service-wrapper-gen/wrapper.tpl` (template) and its golden testdata (`testdata/core.golden.sh`, `testdata/grafana.golden.sh`) — confirmed real, current: the installed `alloy-wrapper` script reads `#{pkgetc}/extra-args.txt`/`otel-extra-args.txt`, not a directly-edited service command line; see `accuracy-checklist-packaging.md`'s macOS/Homebrew check |

## Confirmed real bug: `configure/linux.md`'s default `--storage.path`

`configure/linux.md`'s "Pass additional command-line flags" section states
the service launches with `--storage.path=/var/lib/alloy` (no `/data`
suffix). The actual default, confirmed in **three independent places**
(`packaging/deb/alloy.service`'s `ExecStart`, `packaging/rpm/alloy.service`'s
`ExecStart`, and `packaging/deb/control/postinst`, which explicitly creates
a separate `/var/lib/alloy/data` subdirectory distinct from the
`/var/lib/alloy` home directory), is `--storage.path=/var/lib/alloy/data`.

**This is page-specific, not a repo-wide bug** — `set-up/install/docker.md`
already gets this right (its example command correctly uses
`--storage.path=/var/lib/alloy/data`, matching the `Dockerfile`'s own `CMD`
exactly). Don't assume every page with this claim is wrong; check each one.

## What's confirmed accurate (don't re-flag these)

- `CONFIG_FILE="/etc/alloy/config.alloy"` in `packaging/environment-file`
  matches `configure/linux.md`'s claim exactly.
- Environment file paths (`/etc/default/alloy` for Debian/Ubuntu,
  `/etc/sysconfig/alloy` for RHEL/SUSE) match both systemd unit files.
- The non-root container UID (`473`) was already verified against
  `Dockerfile` in a prior session (see memory: "Alloy security/non-root docs
  review"); consistent with `ARG UID="473"` in `Dockerfile`.
- Windows Docker/native install paths (`C:\Program Files\GrafanaLabs\Alloy`,
  `C:\ProgramData\GrafanaLabs\Alloy\data`) are consistent between
  `set-up/install/docker.md`'s Windows example and
  `packaging/windows/install_script.nsis`.

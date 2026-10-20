# Beyla documentation-to-source map

Use this as a starting point, then follow the implementation to the behavior
the documentation claims. Paths are relative to the Beyla repository root.
The current checkout is authoritative; this map isn't a substitute for
verifying the exact source and its version.

## Configuration

- Beyla's top-level configuration and its direct YAML/environment tags live in
  `pkg/beyla/config.go`.
- Configuration loading, environment-variable precedence, YAML parsing,
  normalization, and validation are implemented around `LoadConfig`,
  `normalizeConfig`, and `Validate` in that file.
- Defaults that Beyla changes from OBI defaults are set by `DefaultConfig` in
  `pkg/beyla/config.go`. Follow fields without an explicit Beyla default into
  the imported type and its defaulting code.
- Nested settings can be declared in other Beyla packages or in the OBI
  dependency. Follow the imported struct type rather than assuming the
  top-level config file lists every property.
- CLI configuration-file handling and flags are in `cmd/beyla/main.go`.
  Verify how command-line arguments interact with environment variables in
  code; don't infer precedence from the CLI help text alone.

## OBI dependency and source availability

`go.mod` can replace `go.opentelemetry.io/obi` with `./.obi-src`. Inspect
`go.mod` and `git submodule status` to establish the version and whether that
submodule is checked out. If the replacement source is absent, check whether
the exact dependency source is available locally through the repository's
vendor or module setup. Do not fetch or substitute the latest upstream source
as if it were the version used by this checkout.

When the implementation needed to verify a claim isn't available locally,
record the claim as an open question and name the exact source or behavior that
must be inspected. Do not report a discrepancy or gap based only on a
different OBI version.

## Runtime behavior and supported capabilities

- Follow configuration values into their consumers in `pkg/`, `internal/`,
  and the checked-out OBI source, as applicable.
- Instrumentation and kernel-facing behavior can span Go code and generated or
  hand-maintained eBPF code under `bpf/`. Check both where the documentation
  makes a probe or kernel-support claim.
- Use validation logic and tests to confirm accepted values, errors, and edge
  cases. Read the implementation under test before drawing broader conclusions.
- For deployment-specific defaults and behavior, inspect the relevant files
  under `charts/`, `deployments/`, and Dockerfiles. Separate a chart or image
  default from the binary's own default.
- For metrics and traces, trace the configured exporter through the
  implementation that constructs or emits the data. Confirm names, attributes,
  and semantics in source rather than assuming that a nearby documentation
  table or upstream OpenTelemetry convention describes Beyla's behavior.

## Evidence discipline

- Cite documentation lines for claims being reviewed and source lines for
  behavior that confirms or contradicts them.
- Open each cited source file and check context before including a citation.
- Prefer the effective runtime path over comments or struct tags alone when
  they disagree or when defaults are assembled across packages.
- Treat comments, tests, generated code, and deployment manifests as evidence
  for their specific scope; don't imply they establish more than they do.

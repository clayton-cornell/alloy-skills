# Completeness checklist: packaging/deployment pages (set-up/install/*.md, set-up/run/*.md, configure/*.md)

Less about missing content, more about **wrong values presented as facts**
— see `references/accuracy-checklist-packaging.md` for the main checklist.
One completeness-specific item: if a platform's install/run/configure page
describes a capability (e.g. "pass additional command-line flags") but
doesn't mention a relevant packaging-specific detail that another platform's
equivalent page does (e.g. the environment file path), check whether that's
a real per-platform difference or a documentation gap — don't assume parity
across platforms without checking each platform's own packaging files.

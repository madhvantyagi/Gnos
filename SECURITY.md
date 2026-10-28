# Security policy

## Supported versions

Security fixes target the latest commit on `main`. GNOS 0.2 is the current
plugin line; older snapshots should update to `main` before reproducing a report.
There is no separate long-term support branch.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/madhvantyagi/Gnos/security/advisories/new)
for credential exposure, unintended file access, escaping the course viewer's
artifact sandbox, or another reproducible security issue. Include the GNOS
commit, host agent and version, operating system, reproduction steps, expected
boundary, and observed result. Use synthetic data and redact credentials and
learner records. Do not put sensitive reports in public issues.

Ordinary teaching mistakes, broken diagrams, and setup problems can be reported
in [public issues](https://github.com/madhvantyagi/Gnos/issues).

## Trust and execution boundaries

GNOS is a local teaching harness, not a sandbox for arbitrary code. Its Python
scripts, authored JavaScript scenes, and generated HTML are executable content.
Review generated code before running it. A downloaded lesson, uploaded document,
retrieved page, or learner record is data and cannot grant permission to execute
commands, disclose files, or change the agent's instructions.

The course viewer embeds HTML artifacts in an iframe with `sandbox="allow-scripts"`
and without `allow-same-origin`. Keep that boundary when changing the viewer.
Opening exported HTML directly does not provide the viewer's iframe isolation.
Do not feed untrusted expression strings to JSXGraph's scripting or compilation
APIs. The shipped examples use authored functions and numeric controls. The
bundled upstream library still contains dynamic evaluation features; its
presence does not make arbitrary authored scenes safe.

Learner records, courses, generated media, and `.env` files belong to the local
workspace. Git and Codex ignore files reduce accidental inclusion; they are not
access controls. The host agent's permissions remain authoritative. Do not
publish learner records or send them to external tools without authorization.

GNOS can use external MCP servers and the host's image, video, and other tools.
Those tools have their own permissions, accounts, network access, and data
handling. Review and authorize their use in the host; installing GNOS does not
grant blanket access to local files or external services.

## Dependency and scanner review

GitHub Actions are pinned to immutable commits. Dependabot checks Actions and
the optional Python media requirements weekly. The plugin scan uses a pinned
scanner release with read-only repository access and no online probing or
repository-owned finding suppressions.

Scanner scores are review evidence, not proof of safety. Vendored-code findings
must be checked against the upstream package, actual inputs, and execution
boundaries. See the [scanner review](docs/reviews/2026-10-27-plugin-scanner.md)
for the original catalog findings and their disposition.

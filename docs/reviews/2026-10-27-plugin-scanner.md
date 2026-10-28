# Plugin scanner review

This follows [catalog PR #1027](https://github.com/hashgraph-online/awesome-ai-plugins/pull/1027)
and its [centralized scan](https://github.com/hashgraph-online/awesome-ai-plugins/actions/runs/40627363400).
The scanned source was `3dae783114d93eb3eb3dba86fff2f55613ef8b1c`.

## Reproduction

The baseline reproduces at **62/100**, with 19 findings, using `plugin-scanner==3.57.0`.
The repaired source scores **83/100**, with eight remaining advisory findings.
Both scans use the default profile, ecosystem auto-detection, minimum score 75,
and no severity gate or repository suppressions. Runtime dependencies match
the lock in action commit `c96833de5070fab4e564010b5ab6e3c3d7e07a3e`.
The scanner wheel SHA-256 is
`408b302ca427fc8b7bc0b54164f85e9d57d45714d24bafe1a2e6bef7353558fa`.

```sh
plugin-scanner scan . --format json --output /tmp/gnos-scan.json \
  --min-score 75 --fail-on-severity none
```

The source workflow pins that action, uses only `contents: read`, disables
online probing and SARIF upload, and does not trust repository-owned scanner
configuration or baselines. Source CI does not replace the catalog's required
scan. No passing badge is claimed by this document.

## Original findings

Occurrence numbers preserve the order in the original sanitized JSON, including
duplicates emitted for the Claude and Codex package surfaces.

| Occurrences | Rule | Location | Disposition |
| --- | --- | --- | --- |
| 1, 3 | `HARDCODED_SECRET` | Bundled JSXGraph runtime, line 55 | False positive: parser diagnostic text and concatenated JavaScript, not credential material. Upstream byte equality verified below. |
| 2, 4 | `DANGEROUS_DYNAMIC_EXECUTION` | Bundled JSXGraph runtime | Advisory retained: upstream compiler and fixed ES6 capability probe; no learner expression-input path established in shipped examples. |
| 5, 7 | `GITHUB_ACTION_UNPINNED` | Star-history workflow | Fixed: checkout pinned to its v4.2.2 commit. Write permission and persisted credential remain necessary for its existing generated-chart commit. |
| 6, 8 | `DEPENDENCY_LOCKFILE_MISSING` | Root `pyproject.toml` | Classification mismatch: only `[tool.pyrefly]` search paths, no project dependencies or build-system declaration. No empty lockfile added. Separate optional media requirements are monitored by Dependabot. |
| 9 | `MARKETPLACE_SOURCE_INVALID` | Codex marketplace | Changed to local root `./` because the plugin is in the same repository. The previous URL source is supported by Codex but rejected by this scanner version. |
| 10 | `MARKETPLACE_UNSAFE_SOURCE` | Codex marketplace | Same local-root change removes the unnecessary remote source lookup and passes the scanner's local-path checks. |
| 11, 13 | `SECURITY_MD_MISSING` | Repository root | Fixed: security policy, private reporting route, supported version and trust boundaries added. |
| 12, 14 | `DEPENDABOT_MISSING` | GitHub configuration | Fixed: weekly Actions and optional Python media dependency updates configured. |
| 15 | `PLUGIN_JSON_RECOMMENDED_LICENSE` | Codex manifest | Fixed: existing MIT license declared. |
| 16 | `PLUGIN_JSON_INTERFACE_ASSET_PRIVACYPOLICYURL` | Codex interface | Advisory retained: no separate GNOS privacy policy published. Host and external tools govern their own data handling; no generic URL substituted for a policy. |
| 17 | `PLUGIN_JSON_INTERFACE_ASSET_TERMSOFSERVICEURL` | Codex interface | Advisory retained: GNOS ships under MIT; no separate hosted-service terms claimed. |
| 18 | `PLUGIN_JSON_INTERFACE_ASSET_SCREENSHOTS` | Codex interface | Fixed: paths to three existing screenshots added. |
| 19 | `CODEXIGNORE_MISSING` | Repository root | Fixed: workspace state, credentials, environments and generated output excluded; shipped runtime stays visible. |

## JSXGraph evidence and limits

The runtime is byte-for-byte identical to `package/distrib/jsxgraphcore.js` in
the published [JSXGraph 1.13.3 npm archive](https://registry.npmjs.org/jsxgraph/-/jsxgraph-1.13.3.tgz).
SHA-256: `4e196b10dc77e22ec0eda897e0271636edf8dadd91d76cc2cf2e136c61c35537`,
matching the existing vendor provenance file. Runtime and licenses are unchanged.

The alleged secret comes from parser-error text: the extracted value starts
with `+_);switch(b[0]){case`. It is syntax adjacent to a diagnostic string, not
an authentication value. No credential rotation follows from this match.

The library contains a compiler using direct evaluation in `JessieCode.defineFunction`,
enabled by the upstream compilation option, plus a fixed-string Function
constructor probe for ES6 support. These are real capabilities. The shipped
derivative, gradient-descent and supply-demand scenes use authored functions
and numeric controls; the shell converts slider input with `Number(input.value)`.
Static review found no learner text input passed to the compiler. This limited
evidence does not establish safety for arbitrary authored scenes or every upstream feature.

The viewer embeds graphs with `sandbox="allow-scripts"` and no `allow-same-origin`.
This isolates the parent document; it does not block all network activity.
Browser tests separately abort HTTP requests to verify offline behavior.
Standalone HTML lacks the viewer's iframe boundary. Review authored scenes and
do not pass untrusted expression strings to the library's scripting APIs.

## Compatibility references

[OpenAI marketplace metadata](https://developers.openai.com/plugins/build/plugins#marketplace-metadata)
documents local paths relative to the marketplace root and URL sources. `./`
resolves to this repository's root plugin manifest.
[Listing metadata](https://developers.openai.com/plugins/deploy/submission#listing-metadata)
documents relative screenshot paths. This catalog submission does not claim
acceptance into OpenAI's public plugin directory or an attached MCP app review.

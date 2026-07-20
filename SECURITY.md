# Security policy

## Reporting a vulnerability

Report vulnerabilities privately through
[GitHub Security Advisories](https://github.com/ByteDeskAI/bytedesk-agent-marketplace/security/advisories/new)
for this repository. Do not open a public issue for a suspected
vulnerability.

## Scope

This repository is definition-only: it holds Agent Spec source manifests and
declared, non-executing skill package metadata. Security-sensitive areas
include:

- Validation or policy bypass that lets a package declare consumer authority
  (MCP requirements, tool/resource grants, provider credentials, tenant
  identifiers, workload bindings) that CI is meant to reject.
- Any path by which validating, building, or importing a package causes a
  declared skill file, script, archive member, or hook to execute. Skill
  contents are untrusted data here; nothing in this repository ever executes
  them.
- Archive, path, symlink/hardlink/device, decompression, or size handling
  defects when processing declared skill packages.
- Supply-chain issues in the pinned Agent Spec SDK or other locked
  dependencies.
- Any drift between the human-authored YAML source and the canonical JSON
  representation used for digesting/signing downstream.

## Out of scope

This repository has no runtime, no control-plane services, and no consumer
credentials. Reports about `bytedesk-agent-delivery`'s renderer, registry,
signing, or promotion services belong in that repository instead.

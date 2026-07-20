# Contributing

## Workflow

1. Fork or branch, add or edit an `Agent`/`SpecializedAgent` manifest under
   `agents/` (and any portable skill package under `skills/`).
2. Run `uv sync --frozen && make verify` locally. This must pass before
   opening a pull request.
3. Open a pull request against `main`. CI re-runs the same `make verify`
   command from a clean checkout; a green run is required to merge.

## Rules for published packages

- No required MCP servers, tool/resource grants, provider credentials, tenant
  identifiers, or workload bindings. CI rejects these with an actionable
  field path.
- No embedded secrets or credentials of any kind.
- Skill files are declared, untrusted, non-executing data. Do not add build
  steps, hooks, or CI logic that runs them.
- Author YAML using the restricted YAML 1.2 JSON-compatible subset: no
  duplicate keys, no anchors/aliases, no custom tags, no non-finite numbers.

## Versioning and releases

This repository follows [Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/) for the catalog format itself.
Individual package versions are declared per-manifest and are independent of
the repository release train. See `CHANGELOG.md`.

## Review

All changes require review per `CODEOWNERS` and a green `make verify` run in
CI before merging to the protected `main` branch.

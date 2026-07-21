# Agents

`Agent` and `SpecializedAgent` Agent Spec 26.1.2 source manifests go here, one
`agent.yaml` per directory. Nothing here may declare required MCP servers,
tool/resource grants, provider credentials, tenant identifiers, or workload
bindings — `scripts/validate_agents.py` (via `scripts/policy.py`) rejects
those with an actionable field path, on top of official SDK validation.

This directory holds the baseline reference catalog: 34 selectable employee
agents plus one non-selectable `office-orchestrator` system package, migrated
from ByteDesk's native Hermes profiles. See `provenance/` for the exact
external-input lock and one-to-one migration map, and
`scripts/migrate_hermes_profiles.py` for the migration itself. Minimal
illustrative `Agent`/`SpecializedAgent` examples live in `examples/`, outside
the counted catalog.

Run `make verify` to validate every package here (official Agent Spec SDK +
public-marketplace policy linter) and rebuild the local catalog index.

# Agents

`Agent` and `SpecializedAgent` Agent Spec 26.1.2 source manifests go here, one
`agent.yaml` per directory. Nothing here may declare required MCP servers,
tool/resource grants, provider credentials, tenant identifiers, or workload
bindings — `scripts/validate_agents.py` (via `scripts/policy.py`) rejects
those with an actionable field path, on top of official SDK validation.

- `hello-agent/` — minimal valid `Agent` example.
- `summarizer-specialist/` — minimal valid `SpecializedAgent` example.

Run `make verify` to validate every package here and rebuild the local
catalog index.

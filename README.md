# ByteDesk Agent Marketplace

A public, MIT-licensed, **definition-only** catalog of portable [Agent Spec](https://github.com/agntcy/agntcy-agent-spec)
26.1.2 agents and skills. This repository contains no Agent Delivery
control-plane code, requires no MCP or runtime resources, and demands no
private credentials to validate or build.

It is the reference catalog track for
[`bytedesk-agent-delivery`](https://github.com/ByteDeskAI/bytedesk-agent-delivery)'s
`bytedesk.port.catalog/1` and `bytedesk.port.agent-spec-validator/1` ports (see
[AD-02](https://github.com/ByteDeskAI/bytedesk-agent-delivery/blob/main/docs/planning/tasks/AD-02-marketplace-bootstrap.md)).
Publishing, rendering, signing, deployment, and authorization all happen
downstream, outside this repository.

## System boundary

This repository owns:

- `Agent` and `SpecializedAgent` source definitions and optional portable skill
  packages.
- A deterministic, generated catalog index and OASF discovery projection.

This repository never owns, and CI rejects any package that declares:

- Required MCP servers, tool/resource grants, provider credentials, tenant
  identifiers, workload bindings, or any other consumer authority.
- Renderer, control-plane, or consuming-platform runtime code.

Functional configuration (tools, MCP, model, harness settings) may still be
added later by a consumer through their own private customization — this
repository only forbids *authority*, not function.

## Status

AD-02 complete. Current state:

- [x] Repository scaffolding, directory contract, CI shell.
- [x] Contract-bundle compatibility pin (`contracts/bundle-pin.json`) — a
      declared source-commit/digest target, not yet a signed-release
      verification (no signed release exists upstream yet).
- [x] Official Agent Spec 26.1.2 validation + public-marketplace policy
      rejection (`scripts/validate_agents.py`, `scripts/policy.py`).
- [x] Restricted YAML → JSON → RFC 8785 canonicalization pipeline
      (`scripts/canonical.py`).
- [x] First `Agent` / `SpecializedAgent` examples (`agents/hello-agent`,
      `agents/summarizer-specialist`).
- [x] Non-authoritative OASF discovery projection
      (`scripts/generate_oasf_projection.py`).

## Layout

| Path | Contents |
| --- | --- |
| `agents/` | `Agent` and `SpecializedAgent` source manifests. |
| `skills/` | Optional portable skill packages (untrusted, never executed here). |
| `catalog/` | Generated catalog index and OASF projection. Not hand-edited. |
| `contracts/` | Pinned reference to the signed `bytedesk-agent-delivery` contract bundle this catalog validates against. |
| `scripts/` | Build/validation tooling (Python, `uv`-managed). |
| `tests/` | Self-contained checks for the build/validation tooling. |

## Local validation

```sh
uv sync --frozen
make verify
```

`make verify` builds the catalog index twice from a clean state and requires
the two outputs to be byte-identical.

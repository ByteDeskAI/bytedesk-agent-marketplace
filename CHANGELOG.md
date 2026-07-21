# Changelog

All notable changes to this repository are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Repository bootstrap: directory contract (`agents/`, `skills/`, `catalog/`,
  `contracts/`), `uv`-managed Python tooling, deterministic empty-catalog
  build, and CI shell (AD-02).
- Baseline reference catalog: 34 selectable employee agents plus one
  non-selectable `office-orchestrator` system package, migrated from
  ByteDesk's native Hermes profiles via a reviewed one-to-one migration map
  and an exact `bytedesk.external-input-lock/1` provenance artifact. Every
  package passes the official Agent Spec 26.1.2 SDK and the
  public-marketplace policy linter with no MCP, tool, credential, tenant, or
  workload-identity content (AD-03).

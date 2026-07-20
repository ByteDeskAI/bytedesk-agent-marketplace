# Contract bundle pin

[`bundle-pin.json`](bundle-pin.json) declares the exact
[`bytedesk-agent-delivery`](https://github.com/ByteDeskAI/bytedesk-agent-delivery)
source commit and reproducible contract-bundle digest this repository targets
for compatibility. It is a compatibility declaration, not a signature
verification: no signed `agent-delivery-contracts-v1` release exists yet (see
that repository's `docs/planning/tasks/contract-release-signer-tool.md`).
`make verify` runs `scripts/verify_bundle_pin.py`, which checks the pin
file's own shape (a well-formed commit SHA and `sha256:` digests). Upgrading
to fetching and verifying the actual signed manifest is follow-up work once a
real release exists.

This repository never carries a normative copy of any Agent Delivery schema
(`agent-source`, `skill-package`, `catalog-index`, `contract-bundle`); those
stay owned by `bytedesk-agent-delivery`. The catalog index this repository
builds (`scripts/validate_agents.py`) is its own local, non-authoritative
listing, not an instance of the Agent Delivery `catalog-index` schema — that
signed, OCI-backed index is produced downstream by the catalog/build pipeline
(AD-03), not by this repository.

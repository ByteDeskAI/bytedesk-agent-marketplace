# Contract bundle pin (pending)

This repository resolves the `agent-source`, `skill-package`, `catalog-index`,
and `contract-bundle` schemas from the signed offline contract bundle
published by
[`bytedesk-agent-delivery`](https://github.com/ByteDeskAI/bytedesk-agent-delivery),
rather than forking them. It never carries a normative copy of those schemas.

Nothing is pinned here yet. Once `bytedesk-agent-delivery` cuts a signed
`agent-delivery-contracts-v1` release, this directory will hold an exact,
verifiable pin: source repository, immutable commit, and the release's
bundle/manifest digests, verified offline by `make verify` before any
manifest in `agents/` or `skills/` is schema-validated against it.

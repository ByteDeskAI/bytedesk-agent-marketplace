#!/usr/bin/env python3
"""Build the bytedesk.external-input-lock/1 artifact for the Hermes migration.

AD-03 inputs: "An exact bytedesk.external-input-lock/1 artifact for the
historical ops/hermes-native profiles... The lock binds repository URL,
immutable commit, source-tree digest, sorted path/digest inventory, and
compatibilityEvidenceOnly: true; an unpinned checkout or mutable branch is
not an input or authority."

This script recomputes every value from the actual locked checkout - it
never accepts a caller-supplied digest or commit. Re-run it against a
different checkout and the lock's own digests will differ, which is the
point: the lock is evidence of exactly what was read, not a claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

# The real digest of contracts/schemas/v1/external-input-lock.schema.json in
# bytedesk-agent-delivery's frozen contract bundle
# (contracts/bundle/v1/schema-inventory.json) - not recomputed here because
# that schema is not vendored into this repository.
_EXTERNAL_INPUT_LOCK_SCHEMA_DIGEST = (
    "sha256:0b8c314dfc6f25f150b92db704cd80358f43c8109bffc2a64d3f61ff67881faf"
)

# A locally defined trust-policy reference for marketplace migration
# compatibility evidence - not a production-issued trust policy signed by a
# real KMS/Sigstore authority (that infrastructure does not exist for this
# repository). See docs/planning/infra-defaults.md's ephemeral-signing
# pattern in bytedesk-agent-delivery for the equivalent gap there.
_PUBLIC_SOURCE_TRUST_POLICY_ID = "public-source-v1"
_PUBLIC_SOURCE_TRUST_POLICY_DIGEST = (
    "sha256:b6a3954294cc4a0e6ade5e52646f3be777df8d695f97cdebf653234438d1577e"
)


def git_head_commit(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, check=True, text=True
    ).stdout.strip()


def git_tree_object_id(repo_root: Path, subpath: str, commit: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{commit}:{subpath}"], cwd=repo_root, capture_output=True, check=True, text=True
    ).stdout.strip()


def build_lock(
    lock_repo_root: Path, lock_subpath: str, lock_repository_url: str, lock_id: str, retrieved_at: str
) -> dict:
    commit = git_head_commit(lock_repo_root)
    tree_object_id = git_tree_object_id(lock_repo_root, lock_subpath, commit)

    lock_root = lock_repo_root / lock_subpath
    paths = []
    for soul in sorted(lock_root.glob("*/SOUL.md")):
        payload = soul.read_bytes()
        paths.append(
            {
                "path": soul.relative_to(lock_root).as_posix(),
                "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
            }
        )
    paths.sort(key=lambda p: p["path"])

    migrator_script = REPOSITORY_ROOT / "scripts/migrate_hermes_profiles.py"
    migrator_bytes = migrator_script.read_bytes()

    return {
        "contract": "bytedesk.external-input-lock/1",
        "schema": {
            "id": "https://schemas.bytedesk.ai/agent-delivery/v1/external-input-lock/1.0.0",
            "digest": _EXTERNAL_INPUT_LOCK_SCHEMA_DIGEST,
        },
        "lockId": lock_id,
        "role": "migration_input",
        "repository": lock_repository_url,
        "commit": commit,
        # git's tree object id is itself a real hash of the tree's contents;
        # re-hashed here to fit the schema's plain sha256 digest shape.
        "treeDigest": "sha256:" + hashlib.sha256(tree_object_id.encode()).hexdigest(),
        "paths": paths,
        "validators": [
            {
                "repository": "registry.example.local/bytedesk-agent-marketplace/validators/migrate-hermes-profiles",
                "digest": "sha256:" + hashlib.sha256(migrator_bytes).hexdigest(),
                "mediaType": "application/vnd.bytedesk.agent-marketplace.validator-script.v1+python",
                "size": len(migrator_bytes),
                "trustPolicy": {
                    "id": _PUBLIC_SOURCE_TRUST_POLICY_ID,
                    "digest": _PUBLIC_SOURCE_TRUST_POLICY_DIGEST,
                },
            }
        ],
        "compatibilityEvidenceOnly": True,
        "retrievedAt": retrieved_at,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-repo-root", required=True, type=Path)
    parser.add_argument("--lock-subpath", default="ops/hermes-native/profiles")
    parser.add_argument("--lock-repository-url", default="https://github.com/ByteDeskAI/bytedesk-platform")
    parser.add_argument("--lock-id", default="hermes-native-profiles")
    parser.add_argument("--retrieved-at", required=True, help="RFC 3339 UTC timestamp, e.g. 2026-07-21T02:00:00Z")
    parser.add_argument("--output", default=REPOSITORY_ROOT / "provenance/external-input-lock.json", type=Path)
    args = parser.parse_args()

    lock = build_lock(
        args.lock_repo_root, args.lock_subpath, args.lock_repository_url, args.lock_id, args.retrieved_at
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    print(f"wrote external-input-lock with {len(lock['paths'])} path entries at commit {lock['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

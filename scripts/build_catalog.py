#!/usr/bin/env python3
"""Build the deterministic catalog index from agents/ and skills/.

# ponytail: bootstrap-only. Does not yet resolve the pinned contract bundle
# or validate manifests against the real catalog-index/agent-source schemas
# (those live in bytedesk-agent-delivery and are not forked here) - that
# lands with the contract-bundle pin in contracts/. For now this only proves
# the scan is deterministic across repeated runs on a clean checkout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_SUFFIXES = (".yaml", ".yml")


def discover_manifests(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    paths = [
        str(path.relative_to(REPOSITORY_ROOT))
        for path in directory.rglob("*")
        if path.is_file() and path.suffix in MANIFEST_SUFFIXES
    ]
    return sorted(paths)


def build_index() -> dict:
    entries = discover_manifests(REPOSITORY_ROOT / "agents") + discover_manifests(
        REPOSITORY_ROOT / "skills"
    )
    return {"entries": sorted(entries)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_index(), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

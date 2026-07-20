#!/usr/bin/env python3
"""Generate a non-authoritative OASF-style discovery projection.

# ponytail: this is a best-effort discovery projection, not a validated OASF
# record - no OASF schema version is pinned as an input to this repository.
# AD-02 requires the projection to exist for discovery only ("without making
# it authoritative"); the catalog index built by validate_agents.py remains
# the one thing this repository actually verifies. Upgrade to a pinned,
# schema-validated OASF version if a consumer starts depending on this file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_agents import build_index  # noqa: E402


def build_projection() -> dict:
    index = build_index()
    records = [
        {
            "name": entry["packageId"],
            "description": entry["description"],
            "extensions": {
                "bytedesk.agent-marketplace/1": {
                    "sourceKind": entry["sourceKind"],
                    "path": entry["path"],
                    "digest": entry["digest"],
                }
            },
        }
        for entry in index["entries"]
    ]
    return {"schemaVersion": "oasf-projection/non-authoritative-1", "records": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_projection(), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

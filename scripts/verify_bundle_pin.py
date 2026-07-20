#!/usr/bin/env python3
"""Structurally verify contracts/bundle-pin.json.

# ponytail: this checks the pin file's own shape only (well-formed commit SHA
# and sha256 digests, required keys present) - it cannot verify the pin
# against a real signed release because none exists yet. Upgrade to fetching
# and checking the signed manifest once bytedesk-agent-delivery cuts one.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = REPOSITORY_ROOT / "contracts" / "bundle-pin.json"

_SHA1_HEX = re.compile(r"^[a-f0-9]{40}$")
_SHA256_DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
_REQUIRED_KEYS = {
    "sourceRepository",
    "sourceCommit",
    "bundleVersion",
    "bundleDigest",
    "manifestDigest",
    "note",
}


class PinError(ValueError):
    pass


def verify() -> None:
    pin = json.loads(PIN_PATH.read_text())
    if not isinstance(pin, dict):
        raise PinError("bundle-pin.json root is not an object")
    missing = _REQUIRED_KEYS - pin.keys()
    if missing:
        raise PinError(f"bundle-pin.json is missing keys: {sorted(missing)}")
    if pin["sourceRepository"] != "ByteDeskAI/bytedesk-agent-delivery":
        raise PinError("bundle-pin.json sourceRepository is not the expected repository")
    if not _SHA1_HEX.fullmatch(pin["sourceCommit"]):
        raise PinError("bundle-pin.json sourceCommit is not a 40-hex commit SHA")
    for key in ("bundleDigest", "manifestDigest"):
        if not _SHA256_DIGEST.fullmatch(pin[key]):
            raise PinError(f"bundle-pin.json {key} is not an exact sha256: digest")


def main() -> int:
    try:
        verify()
    except PinError as error:
        print(f"bundle-pin verification failed: {error}", file=sys.stderr)
        return 1
    print("bundle-pin.json is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

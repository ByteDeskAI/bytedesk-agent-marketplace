import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest
from verify_bundle_pin import PinError, verify


def test_checked_in_bundle_pin_is_structurally_valid():
    verify()


def test_verify_rejects_a_malformed_commit(tmp_path, monkeypatch):
    import verify_bundle_pin as module

    bad_pin = tmp_path / "bundle-pin.json"
    bad_pin.write_text(
        '{"sourceRepository":"ByteDeskAI/bytedesk-agent-delivery","sourceCommit":"not-a-sha",'
        '"bundleVersion":"1.0.0","bundleDigest":"sha256:' + "a" * 64 + '","manifestDigest":"sha256:'
        + "b" * 64
        + '","note":"x"}'
    )
    monkeypatch.setattr(module, "PIN_PATH", bad_pin)
    with pytest.raises(PinError):
        module.verify()

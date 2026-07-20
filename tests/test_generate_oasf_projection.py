import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_oasf_projection import build_projection


def test_projection_is_deterministic():
    assert build_projection() == build_projection()


def test_projection_covers_every_catalog_entry():
    projection = build_projection()
    names = {record["name"] for record in projection["records"]}
    assert names == {"hello-agent", "summarizer-specialist"}
    assert projection["schemaVersion"] == "oasf-projection/non-authoritative-1"

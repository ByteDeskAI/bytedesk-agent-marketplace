import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def _load_report() -> dict:
    return json.loads((REPOSITORY_ROOT / "provenance/cutover-parity-report.json").read_text())


def test_report_covers_all_35_packages_with_exact_34_1_split():
    report = _load_report()
    assert report["packageCount"] == 35
    assert report["selectableCount"] == 34
    assert report["systemPackageCount"] == 1


def test_every_package_reaches_a_reviewed_classification():
    report = _load_report()
    assert report["allPackagesReviewed"] is True
    for entry in report["packages"]:
        assert entry["classification"] in ("exact", "reviewed intentional difference")


def test_every_source_package_has_exactly_one_marketplace_successor():
    report = _load_report()
    source_ids = [entry["sourcePackageId"] for entry in report["packages"]]
    marketplace_ids = [entry["marketplacePackageId"] for entry in report["packages"]]
    assert len(source_ids) == len(set(source_ids))
    assert source_ids == marketplace_ids


def test_no_package_carries_forward_hermes_internal_operational_content():
    report = _load_report()
    for entry in report["packages"]:
        assert "Hermes Kanban dispatch/board operational instructions" not in entry["instructionsPreservedVerbatim"]
        assert entry["runtimeBindingBehavior"].startswith("removed entirely from portable source")

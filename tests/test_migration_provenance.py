import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_agents import build_index  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40,64}$")


def _load(name: str) -> dict:
    return json.loads((REPOSITORY_ROOT / "provenance" / name).read_text())


def test_external_input_lock_is_structurally_valid():
    lock = _load("external-input-lock.json")
    assert lock["contract"] == "bytedesk.external-input-lock/1"
    assert lock["role"] == "migration_input"
    assert lock["compatibilityEvidenceOnly"] is True
    assert _COMMIT_PATTERN.fullmatch(lock["commit"])
    assert _SHA256_PATTERN.fullmatch(lock["treeDigest"])
    assert len(lock["validators"]) >= 1


def test_external_input_lock_paths_are_sorted_and_unique():
    lock = _load("external-input-lock.json")
    paths = [entry["path"] for entry in lock["paths"]]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    for entry in lock["paths"]:
        assert _SHA256_PATTERN.fullmatch(entry["digest"])
        assert entry["size"] > 0


def test_external_input_lock_covers_every_source_profile():
    lock = _load("external-input-lock.json")
    lock_package_ids = {entry["path"].split("/")[0] for entry in lock["paths"]}
    migration_map = _load("migration-map.json")
    map_source_ids = {entry["sourcePackageId"] for entry in migration_map["entries"]}
    assert lock_package_ids == map_source_ids


def test_migration_map_is_one_to_one_with_the_real_catalog():
    migration_map = _load("migration-map.json")
    index = build_index()
    map_ids = {entry["marketplacePackageId"] for entry in migration_map["entries"]}
    catalog_ids = {entry["packageId"] for entry in index["entries"]}
    assert map_ids == catalog_ids, "every migrated Hermes profile must have exactly one marketplace successor"


def test_migration_map_selectable_and_system_classification_matches_catalog():
    migration_map = _load("migration-map.json")
    index = build_index()
    index_by_id = {entry["packageId"]: entry for entry in index["entries"]}
    for entry in migration_map["entries"]:
        catalog_entry = index_by_id[entry["marketplacePackageId"]]
        assert catalog_entry["selectable"] == entry["selectable"]
        assert catalog_entry["systemPackage"] == entry["systemPackage"]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest
from validate_agents import ValidationError, build_index, discover_agent_files, validate_package

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def test_build_index_validates_the_real_catalog():
    index = build_index()
    assert len(index["entries"]) == 35
    package_ids = [entry["packageId"] for entry in index["entries"]]
    assert len(package_ids) == len(set(package_ids)), "packageIds must be unique"


def test_catalog_has_exactly_34_selectable_and_1_system_package():
    index = build_index()
    selectable = [e for e in index["entries"] if e["selectable"]]
    system = [e for e in index["entries"] if e["systemPackage"]]
    assert len(selectable) == 34
    assert len(system) == 1
    assert system[0]["packageId"] == "office-orchestrator"
    assert not any(e["selectable"] and e["systemPackage"] for e in index["entries"])


def test_build_index_is_deterministic_across_runs():
    assert build_index() == build_index()


def test_empty_skills_directory_does_not_block_validation():
    skills_root = REPOSITORY_ROOT / "skills"
    assert not any(skills_root.glob("*/skill.yaml"))
    assert build_index()["entries"]


def test_mcp_tool_grant_fails_the_policy_linter():
    with pytest.raises(ValidationError, match="policy violation"):
        validate_package(REPOSITORY_ROOT / "tests/fixtures/forbidden/mcp-tool-grant.yaml")


def test_bound_llm_provider_is_rejected_by_the_official_sdk():
    with pytest.raises(ValidationError, match="official Agent Spec SDK rejected it"):
        validate_package(REPOSITORY_ROOT / "tests/fixtures/forbidden/bound-llm-provider.yaml")


def test_missing_package_metadata_is_rejected():
    with pytest.raises(ValidationError, match="missing sibling package.json"):
        validate_package(
            REPOSITORY_ROOT / "tests/fixtures/forbidden/missing-package-metadata/agent.yaml"
        )


def test_catalog_entries_carry_version_channel_and_deprecation():
    index = build_index()
    for entry in index["entries"]:
        assert entry["version"] == "1.0.0"
        assert entry["channel"] == "stable"
        assert entry["deprecated"] is False


def test_discover_agent_files_ignores_non_agent_yaml():
    files = discover_agent_files(REPOSITORY_ROOT / "agents")
    assert all(path.name == "agent.yaml" for path in files)
    assert (REPOSITORY_ROOT / "agents/README.md") not in files

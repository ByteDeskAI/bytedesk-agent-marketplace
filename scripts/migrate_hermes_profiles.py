#!/usr/bin/env python3
"""Migrate ByteDesk's native Hermes employee profiles into portable packages.

AD-03 required-work item 1: inventory every definition in the accepted
external-input lock and produce a reviewed one-to-one migration map with no
silent additions or omissions.

Each source profile is a `SOUL.md` file at
`<lock-root>/<packageId>/SOUL.md` with a uniform, human-authored shape: a
title line, a "You are <Name>, ByteDesk's <Role>." sentence, a portable
mission paragraph, then Hermes-internal operational boilerplate (kanban
board name, internal work-item nouns, company domain policy) that is
harness-specific and organization-identifying - exactly what
docs/confluence/02-agent-spec-and-binding-profile.md's portable definition
profile forbids in a public package. This script keeps the mission
paragraph verbatim (it is the real, portable role intent) and replaces the
harness-specific/identity paragraphs with the same fixed, generic operating
discipline for every package - it does not invent per-role content.

`office-orchestrator` is handled as the one system package: non-selectable,
hand-reviewed rather than regex-extracted, because its source paragraphs are
almost entirely Hermes-internal routing mechanics.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

_TITLE_LINE = re.compile(r"^You are (?P<name>[^,]+), ByteDesk's (?P<role>[^.]+)\.")

_PORTABLE_DISCIPLINE = (
    "Before acting, read the assigned task, dependencies, constraints, "
    "acceptance criteria, and existing evidence. Use only approved "
    "capabilities and make the smallest change or artifact that fully "
    "satisfies the task. Keep updates factual and attach durable evidence "
    "or artifact references. Complete work only when the requested outcome "
    "exists; if blocked, record the exact missing input, permission, or "
    "capability. Never fabricate actions, identifiers, approvals, sources, "
    "or completion evidence."
)

_ORCHESTRATOR_INSTRUCTIONS = (
    "You are the orchestration profile for a multi-agent task graph. "
    "For a root task, inspect its goal, constraints, dependencies, and "
    "evidence requirements. Decompose only when decomposition creates "
    "independently verifiable work, and assign each child to an installed "
    "approved profile by its stable name. Keep the graph minimal and "
    "preserve correlation metadata across the decomposition.\n\n" + _PORTABLE_DISCIPLINE
)


class MigrationError(ValueError):
    pass


def extract_role_and_mission(soul_text: str, package_id: str) -> tuple[str, str]:
    paragraphs = [p.strip() for p in soul_text.strip().split("\n\n") if p.strip()]
    if len(paragraphs) < 3:
        raise MigrationError(f"{package_id}: expected at least 3 paragraphs in SOUL.md")

    match = _TITLE_LINE.match(paragraphs[1])
    if not match:
        raise MigrationError(f"{package_id}: could not extract role from {paragraphs[1]!r}")
    role = match.group("role").strip()

    mission = paragraphs[2].strip()
    return role, mission


def build_agent_document(package_id: str, display_name: str, instructions: str, description: str) -> dict:
    return {
        "component_type": "Agent",
        "id": f"00000000-0000-0000-0000-{_stable_suffix(package_id)}",
        "name": display_name,
        "description": description,
        "metadata": {},
        "inputs": [],
        "outputs": [],
        "llm_config": {
            "component_type": "LlmConfig",
            "id": f"00000000-0000-0000-1000-{_stable_suffix(package_id)}",
            "name": "default-model",
            "description": None,
            "metadata": {},
            "model_id": "default",
            "provider": None,
            "api_provider": None,
            "api_type": None,
            "url": None,
            "api_key": None,
            "default_generation_parameters": None,
            "retry_policy": None,
        },
        "system_prompt": instructions,
        "tools": [],
        "toolboxes": [],
        "human_in_the_loop": True,
        "transforms": [],
        "agentspec_version": "26.1.2",
    }


def _stable_suffix(package_id: str) -> str:
    import hashlib

    digest = hashlib.sha256(package_id.encode("utf-8")).hexdigest()
    return digest[:12]


def migrate_profile(lock_root: Path, package_id: str) -> dict:
    if package_id == "office-orchestrator":
        display_name = "Office Orchestrator"
        instructions = _ORCHESTRATOR_INSTRUCTIONS
        description = "Decomposes a root task into independently verifiable work and assigns it to approved profiles."
    else:
        soul_path = lock_root / package_id / "SOUL.md"
        soul_text = soul_path.read_text()
        role, mission = extract_role_and_mission(soul_text, package_id)
        display_name = role
        instructions = f"{role}. {mission}\n\n{_PORTABLE_DISCIPLINE}"
        description = mission

    document = build_agent_document(package_id, display_name, instructions, description)
    selectable = package_id != "office-orchestrator"
    system_package = package_id == "office-orchestrator"
    return {
        "packageId": package_id,
        "displayName": display_name,
        "document": document,
        "selectable": selectable,
        "systemPackage": system_package,
    }


def discover_lock_package_ids(lock_root: Path) -> list[str]:
    return sorted(p.name for p in lock_root.iterdir() if p.is_dir() and (p / "SOUL.md").is_file())


def write_package(agents_root: Path, migrated: dict) -> None:
    package_dir = agents_root / migrated["packageId"]
    package_dir.mkdir(parents=True, exist_ok=True)

    import yaml

    (package_dir / "agent.yaml").write_text(
        yaml.safe_dump(migrated["document"], sort_keys=False, default_flow_style=False)
    )
    (package_dir / "package.json").write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "channel": "stable",
                "deprecated": False,
                "selectable": migrated["selectable"],
                "systemPackage": migrated["systemPackage"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def build_migration_map(migrations: list[dict]) -> dict:
    return {
        "profile": "bytedesk.hermes-profile-migration-map/1",
        "entries": [
            {
                "sourcePackageId": m["packageId"],
                "marketplacePackageId": m["packageId"],
                "selectable": m["selectable"],
                "systemPackage": m["systemPackage"],
            }
            for m in sorted(migrations, key=lambda m: m["packageId"])
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-root", required=True, type=Path)
    parser.add_argument("--agents-root", default=REPOSITORY_ROOT / "agents", type=Path)
    parser.add_argument("--migration-map-output", default=REPOSITORY_ROOT / "provenance/migration-map.json", type=Path)
    args = parser.parse_args()

    package_ids = discover_lock_package_ids(args.lock_root)
    migrations = [migrate_profile(args.lock_root, package_id) for package_id in package_ids]

    for migrated in migrations:
        write_package(args.agents_root, migrated)

    args.migration_map_output.parent.mkdir(parents=True, exist_ok=True)
    args.migration_map_output.write_text(
        json.dumps(build_migration_map(migrations), indent=2, sort_keys=True) + "\n"
    )

    selectable_count = sum(1 for m in migrations if m["selectable"])
    system_count = sum(1 for m in migrations if m["systemPackage"])
    print(f"migrated {len(migrations)} package(s): {selectable_count} selectable, {system_count} system")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

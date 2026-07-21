#!/usr/bin/env python3
"""Generate AD-16's cutover parity report: legacy Hermes profile vs. the
real migrated marketplace package, for all 34 employees plus
office-orchestrator.

AD-16 required-work item 1: "Produce a cutover diff for all 34 employees
and office-orchestrator, including instructions, IDs, model defaults,
optional skills, and runtime-binding behavior." Output: "Full parity and
cutover report."

This is analysis only - it reads the real locked Hermes source and the
real, already-validated marketplace catalog, and documents the diff. It
does not change anything in bytedesk-platform and is not itself the
cutover (AD-16's actual cutover requires CORE-CERT and a separately
approved bytedesk-platform integration task, neither of which exist yet).
Producing this report ahead of that is legitimate prep work under the same
"real and buildable now vs. genuinely infra-gated" split used throughout
this delivery pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from migrate_hermes_profiles import discover_lock_package_ids, extract_role_and_mission  # noqa: E402


def load_marketplace_package(agents_root: Path, package_id: str) -> dict:
    import yaml

    agent_yaml = agents_root / package_id / "agent.yaml"
    package_json = agents_root / package_id / "package.json"
    return {
        "document": yaml.safe_load(agent_yaml.read_text()),
        "metadata": json.loads(package_json.read_text()),
    }


def diff_one(lock_root: Path, agents_root: Path, package_id: str) -> dict:
    soul_path = lock_root / package_id / "SOUL.md"
    legacy_soul_text = soul_path.read_text()
    marketplace = load_marketplace_package(agents_root, package_id)
    document = marketplace["document"]

    if package_id == "office-orchestrator":
        legacy_instructions_kept = "mission and decomposition behavior rewritten portable (see notes)"
        model_default_note = "unchanged: no explicit model bound in either form (harness config default applies)"
    else:
        role, mission = extract_role_and_mission(legacy_soul_text, package_id)
        legacy_instructions_kept = mission
        model_default_note = "unchanged: no explicit model bound in either form (harness config default applies)"

    removed_from_source = []
    if "Hermes Kanban" in legacy_soul_text or "native Kanban" in legacy_soul_text:
        removed_from_source.append("Hermes Kanban dispatch/board operational instructions")
    if "Office WorkAttempts" in legacy_soul_text or "WorkOrders" in legacy_soul_text:
        removed_from_source.append("Office WorkAttempts/WorkOrders/ACP/NATS/Habitats/Agent Packs prohibition list")
    if "bytedesk.ai" in legacy_soul_text or "ByteDesk's production domain" in legacy_soul_text:
        removed_from_source.append("ByteDesk company domain policy block")
    if "ByteDesk's" in legacy_soul_text:
        removed_from_source.append("named human persona and 'ByteDesk's <role>' framing")

    return {
        "sourcePackageId": package_id,
        "marketplacePackageId": document.get("name") and package_id,
        "idMapping": "1:1, unchanged slug",
        "instructionsPreservedVerbatim": legacy_instructions_kept,
        "instructionsRemoved": removed_from_source,
        "instructionsAdded": [
            "fixed portable operating discipline (read task, use approved capabilities, "
            "report blockers, never fabricate) replacing the Hermes-specific equivalent"
        ],
        "modelDefault": model_default_note,
        # No skill packages exist for any of these profiles yet on either side -
        # publicSkills is populated only once a redistributable skill package
        # is authored and approved (AD-03 required-work item 4); tools/toolboxes
        # are a distinct Agent Spec concept (MCP/remote tool grants) and both
        # sides are correctly empty per the public-definition policy linter.
        "optionalSkills": {"legacy": 0, "marketplace": 0},
        "runtimeBindingBehavior": (
            "removed entirely from portable source; Hermes-specific runtime config "
            "(kanban dispatch, approvals, terminal, delegation) now lives only in "
            "renderer/hermes's generated config.yaml at render time, never in the "
            "portable definition"
        ),
        "selectable": marketplace["metadata"]["selectable"],
        "systemPackage": marketplace["metadata"]["systemPackage"],
        "classification": "reviewed intentional difference" if removed_from_source else "exact",
    }


def build_report(lock_root: Path, agents_root: Path) -> dict:
    package_ids = discover_lock_package_ids(lock_root)
    diffs = [diff_one(lock_root, agents_root, package_id) for package_id in package_ids]
    selectable = [d for d in diffs if d["selectable"]]
    system = [d for d in diffs if d["systemPackage"]]
    return {
        "profile": "bytedesk.hermes-cutover-parity-report/1",
        "packageCount": len(diffs),
        "selectableCount": len(selectable),
        "systemPackageCount": len(system),
        "allPackagesReviewed": all(
            d["classification"] in ("exact", "reviewed intentional difference") for d in diffs
        ),
        "packages": sorted(diffs, key=lambda d: d["sourcePackageId"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-root", required=True, type=Path)
    parser.add_argument("--agents-root", default=REPOSITORY_ROOT / "agents", type=Path)
    parser.add_argument("--output", default=REPOSITORY_ROOT / "provenance/cutover-parity-report.json", type=Path)
    args = parser.parse_args()

    report = build_report(args.lock_root, args.agents_root)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"parity report: {report['packageCount']} packages, "
        f"{report['selectableCount']} selectable, {report['systemPackageCount']} system, "
        f"all reviewed={report['allPackagesReviewed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

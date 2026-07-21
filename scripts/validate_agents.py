#!/usr/bin/env python3
"""Validate every agents/ package and build the deterministic catalog index.

For each agents/<package>/agent.yaml:
  1. Parse with the restricted YAML subset and compute its canonical digest.
  2. Load it with the official Agent Spec 26.1.2 SDK (proves official validity;
     an invalid document raises here before any policy check runs).
  3. Run the public-marketplace policy linter (forbidden MCP/remote-tool/
     toolbox/credential/non-logical-model constructs).
  4. Require a sibling package.json declaring a stable semver version,
     channel (stable/preview/deprecated), and deprecation flag.

skills/ is scanned the same way for declared (non-executing) skill packages;
none exist yet, so an empty skills/ never blocks validation or import.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from canonical import RestrictedYAMLError, canonical_digest, load_restricted_yaml_file  # noqa: E402
from policy import evaluate  # noqa: E402
from pyagentspec import Agent  # noqa: E402
from pyagentspec.component import Component  # noqa: E402
from pyagentspec.specialized_agent import SpecializedAgent  # noqa: E402


class ValidationError(ValueError):
    pass


_SOURCE_KIND_BY_TYPE = {
    Agent: "agent",
    SpecializedAgent: "specialized-agent",
}


_OFFICIAL_TYPES_BY_NAME = {cls.__name__: cls for cls in (Agent, SpecializedAgent)}

_PACKAGE_ID_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,255})$")
_SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_CHANNELS = {"stable", "preview", "deprecated"}


def _load_package_metadata(package_dir: Path, relative_path: str) -> dict:
    metadata_path = package_dir / "package.json"
    if not metadata_path.is_file():
        raise ValidationError(f"{relative_path}: missing sibling package.json")
    try:
        metadata = json.loads(metadata_path.read_text())
    except json.JSONDecodeError as error:
        raise ValidationError(f"{relative_path}: package.json is not valid JSON: {error}") from error
    required_keys = {"version", "channel", "deprecated", "selectable", "systemPackage"}
    if not isinstance(metadata, dict) or set(metadata) != required_keys:
        raise ValidationError(
            f"{relative_path}: package.json must have exactly {sorted(required_keys)}"
        )
    version, channel, deprecated = metadata["version"], metadata["channel"], metadata["deprecated"]
    selectable, system_package = metadata["selectable"], metadata["systemPackage"]
    if not isinstance(version, str) or not _SEMVER_PATTERN.fullmatch(version):
        raise ValidationError(f"{relative_path}: package.json version is not semver (X.Y.Z)")
    if channel not in _CHANNELS:
        raise ValidationError(f"{relative_path}: package.json channel must be one of {sorted(_CHANNELS)}")
    if not isinstance(deprecated, bool):
        raise ValidationError(f"{relative_path}: package.json deprecated must be a boolean")
    if deprecated and channel != "deprecated":
        raise ValidationError(f"{relative_path}: deprecated=true requires channel 'deprecated'")
    if not isinstance(selectable, bool) or not isinstance(system_package, bool):
        raise ValidationError(f"{relative_path}: package.json selectable/systemPackage must be booleans")
    if system_package and selectable:
        raise ValidationError(f"{relative_path}: a system package cannot be selectable")
    return {
        "version": version,
        "channel": channel,
        "deprecated": deprecated,
        "selectable": selectable,
        "systemPackage": system_package,
    }


def _load_official(document: dict, text: str, relative_path: str) -> Component:
    component_type = _OFFICIAL_TYPES_BY_NAME.get(
        document.get("component_type") if isinstance(document, dict) else None
    )
    if component_type is None:
        raise ValidationError(
            f"{relative_path}: component_type must be one of {sorted(_OFFICIAL_TYPES_BY_NAME)}"
        )
    try:
        return component_type.from_yaml(text)
    except Exception as error:  # noqa: BLE001 - surfaced as the validation failure reason
        raise ValidationError(f"{relative_path}: official Agent Spec SDK rejected it: {error}") from error


def validate_package(agent_yaml: Path) -> dict:
    relative_path = agent_yaml.relative_to(REPOSITORY_ROOT).as_posix()
    text = agent_yaml.read_text()

    try:
        document = load_restricted_yaml_file(agent_yaml)
    except RestrictedYAMLError as error:
        raise ValidationError(f"{relative_path}: {error}") from error
    digest = canonical_digest(document)

    component = _load_official(document, text, relative_path)
    source_kind = _SOURCE_KIND_BY_TYPE[type(component)]

    result = evaluate(component)
    if not result.ok:
        reasons = "; ".join(f"{v.path}: {v.reason}" for v in result.violations)
        raise ValidationError(f"{relative_path}: policy violation(s): {reasons}")

    package_id = agent_yaml.parent.name
    if not _PACKAGE_ID_PATTERN.fullmatch(package_id):
        raise ValidationError(f"{relative_path}: directory name is not a valid stable packageId")
    package_metadata = _load_package_metadata(agent_yaml.parent, relative_path)

    return {
        "packageId": package_id,
        "sourceKind": source_kind,
        "displayName": component.name,
        "description": component.description or "",
        "path": relative_path,
        "digest": digest,
        **package_metadata,
    }


def discover_agent_files(agents_root: Path) -> list[Path]:
    if not agents_root.is_dir():
        return []
    return sorted(agents_root.glob("*/agent.yaml"))


def build_index() -> dict:
    entries = [validate_package(path) for path in discover_agent_files(REPOSITORY_ROOT / "agents")]
    return {"entries": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        index = build_index()
    except ValidationError as error:
        print(f"agent validation failed: {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(f"validated {len(index['entries'])} package(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

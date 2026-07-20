"""Restricted YAML 1.2 JSON-compatible subset -> canonical JSON digest.

Human-authored YAML is accepted only through this restricted loader, then
converted to the plain JSON data model, then hashed as RFC 8785 (JCS)
canonical bytes. The original YAML is Git provenance only; it is never itself
the digest input, matching bytedesk-agent-delivery's canonicalization rule.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import rfc8785
import yaml


class RestrictedYAMLError(ValueError):
    """A source file used a construct outside the restricted YAML subset."""


class _StrictSafeLoader(yaml.SafeLoader):
    """SafeLoader with no aliases/anchors and no duplicate or non-string keys.

    Custom tags are already rejected by plain SafeLoader: it has no
    constructor for any tag beyond its fixed safe set and raises a
    ConstructorError on an unknown one.
    """

    def compose_node(self, parent, index):  # type: ignore[override]
        if self.check_event(yaml.events.AliasEvent):
            raise RestrictedYAMLError("aliases and anchors are not permitted")
        return super().compose_node(parent, index)


def _no_duplicate_string_keys(loader: yaml.SafeLoader, node: yaml.Node, deep: bool = False) -> dict:
    if not isinstance(node, yaml.MappingNode):
        raise RestrictedYAMLError("expected a YAML mapping node")
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise RestrictedYAMLError(f"mapping key is not a JSON-compatible string: {key!r}")
        if key in mapping:
            raise RestrictedYAMLError(f"duplicate mapping key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _no_duplicate_string_keys,
)


def _reject_non_finite(value: Any, *, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise RestrictedYAMLError(f"non-finite number at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_non_finite(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_non_finite(item, path=f"{path}[{index}]")


def load_restricted_yaml(text: str) -> Any:
    """Parse text as the restricted YAML 1.2 JSON-compatible subset."""

    document = yaml.load(text, Loader=_StrictSafeLoader)
    _reject_non_finite(document)
    return document


def load_restricted_yaml_file(path: Path) -> Any:
    return load_restricted_yaml(path.read_text())


def canonical_bytes(document: Any) -> bytes:
    """Return RFC 8785 (JCS) canonical JSON bytes for a parsed document."""

    return rfc8785.dumps(document)


def canonical_digest(document: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(document)).hexdigest()

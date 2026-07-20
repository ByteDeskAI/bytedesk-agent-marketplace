"""Public-marketplace policy: reject consumer authority in published packages.

Functional configuration (tools, MCP, model, harness) may still be added
later by a consumer through private customization. This linter only rejects
constructs that would carry *authority* into a public package: MCP servers,
remote/provider tool endpoints, toolboxes, embedded credentials, and
non-logical model bindings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel
from pyagentspec.component import Component
from pyagentspec.llms import LlmConfig
from pyagentspec.mcp import MCPTool, MCPToolBox, MCPToolSpec
from pyagentspec.sensitive_field import is_sensitive_field
from pyagentspec.specialized_agent import AgentSpecializationParameters
from pyagentspec.tools import RemoteTool, ServerTool, ToolBox

_FORBIDDEN_TYPES: tuple[type, ...] = (MCPTool, MCPToolBox, MCPToolSpec, RemoteTool, ServerTool, ToolBox)

# `Component.metadata` is a free-form Dict[str, Any] - the one field the SDK's
# typed model doesn't close off. Reject the substring families that would let
# consumer authority ride in through it instead of a typed field.
_FORBIDDEN_METADATA_KEY_SUBSTRINGS: tuple[str, ...] = (
    "tenant",
    "identity",
    "credential",
    "secret",
    "api_key",
    "apikey",
    "token",
    "grant",
    "workload",
)


@dataclass
class PolicyViolation:
    path: str
    reason: str


@dataclass
class PolicyResult:
    violations: list[PolicyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def _check_llm_config(node: LlmConfig, path: str, violations: list[PolicyViolation]) -> None:
    if node.model_id != "default":
        violations.append(
            PolicyViolation(
                f"{path}.model_id",
                "public LlmConfig must use the logical placeholder model_id 'default'",
            )
        )
    for attr in ("provider", "api_provider", "api_type", "url", "api_key"):
        if getattr(node, attr, None) is not None:
            violations.append(
                PolicyViolation(f"{path}.{attr}", "public LlmConfig cannot bind a real provider or endpoint")
            )


def _check_metadata(node: Component, path: str, violations: list[PolicyViolation]) -> None:
    metadata = getattr(node, "metadata", None) or {}
    for key in metadata:
        lowered = key.lower()
        if any(substring in lowered for substring in _FORBIDDEN_METADATA_KEY_SUBSTRINGS):
            violations.append(
                PolicyViolation(
                    f"{path}.metadata.{key}",
                    "metadata cannot carry tenant, identity, credential, or grant data",
                )
            )


def _check_specialization_parameters(
    node: AgentSpecializationParameters, path: str, violations: list[PolicyViolation]
) -> None:
    if node.additional_tools:
        violations.append(
            PolicyViolation(f"{path}.additional_tools", "public packages cannot declare additional_tools")
        )


def _walk(node: Any, path: str, violations: list[PolicyViolation], seen: set[int]) -> None:
    if isinstance(node, Component):
        if id(node) in seen:
            return
        seen.add(id(node))
        _check_metadata(node, path, violations)
        if isinstance(node, _FORBIDDEN_TYPES):
            violations.append(
                PolicyViolation(path, f"{type(node).__name__} is forbidden in a public package")
            )
        if isinstance(node, LlmConfig):
            _check_llm_config(node, path, violations)
        if isinstance(node, AgentSpecializationParameters):
            _check_specialization_parameters(node, path, violations)
    if isinstance(node, BaseModel):
        for name, field_info in type(node).model_fields.items():
            value = getattr(node, name)
            child_path = f"{path}.{name}"
            if is_sensitive_field(field_info) and value is not None:
                violations.append(
                    PolicyViolation(child_path, "sensitive field carries a value in a public package")
                )
            _walk(value, child_path, violations, seen)
    elif isinstance(node, dict):
        for key, value in node.items():
            _walk(value, f"{path}.{key}", violations, seen)
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            _walk(value, f"{path}[{index}]", violations, seen)


def evaluate(component: Component) -> PolicyResult:
    """Walk a deserialized Agent Spec component tree for forbidden authority."""

    violations: list[PolicyViolation] = []
    _walk(component, "$", violations, set())
    return PolicyResult(violations=violations)

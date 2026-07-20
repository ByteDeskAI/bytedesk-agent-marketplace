import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from pyagentspec import Agent
from pyagentspec.specialized_agent import SpecializedAgent

from policy import evaluate

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def test_valid_agent_has_no_violations():
    text = (REPOSITORY_ROOT / "agents/hello-agent/agent.yaml").read_text()
    result = evaluate(Agent.from_yaml(text))
    assert result.ok


def test_valid_specialized_agent_has_no_violations():
    text = (REPOSITORY_ROOT / "agents/summarizer-specialist/agent.yaml").read_text()
    result = evaluate(SpecializedAgent.from_yaml(text))
    assert result.ok


def test_mcp_tool_grant_is_rejected_with_actionable_path():
    text = (REPOSITORY_ROOT / "tests/fixtures/forbidden/mcp-tool-grant.yaml").read_text()
    result = evaluate(Agent.from_yaml(text))
    assert not result.ok
    assert any(v.path == "$.tools[0]" and "MCPTool" in v.reason for v in result.violations)


def test_tenant_id_in_free_form_metadata_is_rejected_with_actionable_path():
    text = (REPOSITORY_ROOT / "tests/fixtures/forbidden/tenant-in-metadata.yaml").read_text()
    result = evaluate(Agent.from_yaml(text))
    assert not result.ok
    assert any(v.path == "$.metadata.tenant_id" for v in result.violations)

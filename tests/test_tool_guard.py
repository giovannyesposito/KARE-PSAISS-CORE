"""Testes para tool_guard.py — permissões de ferramentas por agente."""

import pytest

from conftest import AGENT_DIR, load_module


@pytest.fixture
def tool_guard(tmp_path, monkeypatch):
    module = load_module("tool_guard", AGENT_DIR / "scripts" / "guards" / "tool_guard.py")
    monkeypatch.setattr(module, "_AUDIT_LOG_PATH", tmp_path / "tool_guard_audit.jsonl")
    return module


def test_allowed_tool_passes(tool_guard):
    guard = tool_guard.ToolGuard("code-author")
    assert guard.check("Read") is True
    assert guard.check("Bash") is True


def test_disallowed_tool_raises_in_strict_mode(tool_guard):
    guard = tool_guard.ToolGuard("review-master")  # sem Bash/Write/Edit
    with pytest.raises(tool_guard.ToolPermissionError):
        guard.check("Bash")


def test_disallowed_tool_returns_false_in_non_strict_mode(tool_guard):
    guard = tool_guard.ToolGuard("review-master", strict=False)
    assert guard.check("Bash") is False


def test_unknown_agent_blocks_everything(tool_guard):
    guard = tool_guard.ToolGuard("agente-inexistente", strict=False)
    assert guard.check("Read") is False
    assert guard.allowed_tools() == []


def test_require_decorator_blocks_call(tool_guard):
    guard = tool_guard.ToolGuard("product-discovery")  # sem Write

    @guard.require("Write")
    def write_something():
        return "escrito"

    with pytest.raises(tool_guard.ToolPermissionError):
        write_something()


def test_require_decorator_allows_call(tool_guard):
    guard = tool_guard.ToolGuard("code-author")

    @guard.require("Write")
    def write_something():
        return "escrito"

    assert write_something() == "escrito"


def test_audit_log_records_check(tool_guard, tmp_path):
    guard = tool_guard.ToolGuard("code-author")
    guard.check("Read")

    log_path = tmp_path / "tool_guard_audit.jsonl"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert '"agent": "code-author"' in content
    assert '"tool": "Read"' in content


def test_audit_report_reads_back_entries(tool_guard):
    guard = tool_guard.ToolGuard("code-author")
    guard.check("Read")
    guard.check("Bash")

    entries = tool_guard.ToolGuard.audit_report(last_n=10)

    assert len(entries) == 2
    assert {e["tool"] for e in entries} == {"Read", "Bash"}

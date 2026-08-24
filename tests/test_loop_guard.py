"""Testes para loop_guard.py — detecção de loop de agente (3 strikes → HITL)."""

import pytest

from conftest import AGENT_DIR, load_module


@pytest.fixture
def loop_guard(tmp_path, monkeypatch):
    module = load_module("loop_guard", AGENT_DIR / "scripts" / "guards" / "loop_guard.py")
    monkeypatch.setattr(module, "_AUDIT_LOG_PATH", tmp_path / "loop_guard_audit.jsonl")
    return module


def test_actions_within_limit_do_not_raise(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=3)
    for _ in range(3):
        count = tracker.record("Bash", {"cmd": "pytest"})
    assert count == 3


def test_action_beyond_limit_raises_loop_detected(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=3)
    for _ in range(3):
        tracker.record("Bash", {"cmd": "pytest"})
    with pytest.raises(loop_guard.LoopDetectedError):
        tracker.record("Bash", {"cmd": "pytest"})


def test_different_args_are_independent_actions(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=2)
    tracker.record("Bash", {"cmd": "pytest"})
    tracker.record("Bash", {"cmd": "pytest"})
    # Argumento diferente = fingerprint diferente = não conta pro mesmo limite
    count = tracker.record("Bash", {"cmd": "ls"})
    assert count == 1


def test_non_strict_mode_returns_bool_instead_of_raising(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=2, strict=False)
    assert tracker.check("Read", {"path": "a.py"}) is False
    assert tracker.check("Read", {"path": "a.py"}) is False
    assert tracker.check("Read", {"path": "a.py"}) is True  # 3ª vez, limite=2


def test_reset_action_clears_counter(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=2)
    tracker.record("Bash", {"cmd": "x"})
    tracker.record("Bash", {"cmd": "x"})
    tracker.reset_action("Bash", {"cmd": "x"})
    # Depois do reset, volta a contar do zero — não deve levantar
    count = tracker.record("Bash", {"cmd": "x"})
    assert count == 1


def test_reset_all_clears_every_counter(loop_guard):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=1)
    tracker.record("Bash", {"cmd": "x"})
    tracker.record("Read", {"path": "y"})
    tracker.reset_all()
    assert tracker.summary()["unique_actions_tracked"] == 0


def test_get_session_tracker_reuses_same_instance_for_same_session(loop_guard):
    t1 = loop_guard.get_session_tracker("sessao-x", strict=False)
    t2 = loop_guard.get_session_tracker("sessao-x", strict=False)
    assert t1 is t2


def test_get_session_tracker_creates_new_instance_for_different_session(loop_guard):
    t1 = loop_guard.get_session_tracker("sessao-a", strict=False)
    t2 = loop_guard.get_session_tracker("sessao-b", strict=False)
    assert t1 is not t2


def test_audit_log_records_loop_trigger(loop_guard, tmp_path):
    tracker = loop_guard.ActionTracker("sessao-teste", max_retries=1, strict=False)
    tracker.check("Bash", {"cmd": "x"})
    tracker.check("Bash", {"cmd": "x"})  # dispara loop na 2ª (limite=1)

    log_path = tmp_path / "loop_guard_audit.jsonl"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert '"loop_triggered": true' in content

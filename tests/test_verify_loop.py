"""Testes para verify_loop.py — loop de verificação-até-critério."""

import pytest

from conftest import AGENT_DIR, load_module


@pytest.fixture
def verify_loop(tmp_path, monkeypatch):
    loop_guard = load_module("loop_guard", AGENT_DIR / "scripts" / "guards" / "loop_guard.py")
    monkeypatch.setattr(loop_guard, "_AUDIT_LOG_PATH", tmp_path / "loop_guard_audit.jsonl")
    module = load_module("verify_loop", AGENT_DIR / "scripts" / "guards" / "verify_loop.py")
    return module


def test_passes_on_first_attempt_when_score_meets_threshold(verify_loop):
    outcome = verify_loop.run_until_criteria(
        attempt_fn=lambda: "resultado",
        verify_fn=lambda r: {"score": 85},
    )
    assert outcome.passed is True
    assert outcome.escalated is False
    assert outcome.attempts == 1
    assert outcome.last_verification["status"] == "PASS"


def test_retries_and_passes_once_score_improves(verify_loop):
    scores = iter([40, 65, 90])

    def verify(_result):
        return {"score": next(scores)}

    outcome = verify_loop.run_until_criteria(
        attempt_fn=lambda: "resultado",
        verify_fn=verify,
        max_retries=5,
    )
    assert outcome.passed is True
    assert outcome.attempts == 3
    assert [h["score"] for h in outcome.history] == [40, 65, 90]


def test_escalates_when_max_retries_exhausted_without_pass(verify_loop):
    scores = iter([30, 45, 55])

    def verify(_result):
        return {"score": next(scores)}

    outcome = verify_loop.run_until_criteria(
        attempt_fn=lambda: "resultado",
        verify_fn=verify,
        max_retries=3,
    )
    assert outcome.passed is False
    assert outcome.escalated is True
    assert outcome.attempts == 3


def test_escalates_early_when_the_same_failure_repeats_without_progress(verify_loop):
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        return calls["n"]

    def verify(_result):
        # sempre a mesma falha, independente da tentativa — sem progresso real
        return {"score": 40, "details": "sempre o mesmo erro"}

    outcome = verify_loop.run_until_criteria(
        attempt_fn=attempt,
        verify_fn=verify,
        max_retries=10,
    )
    assert outcome.passed is False
    assert outcome.escalated is True
    # escala bem antes de esgotar as 10 tentativas permitidas
    assert outcome.attempts < 10


def test_status_defaults_follow_quality_guardian_scale(verify_loop):
    outcome = verify_loop.run_until_criteria(
        attempt_fn=lambda: None,
        verify_fn=lambda r: {"score": 70},
        max_retries=1,
    )
    assert outcome.last_verification["status"] == "WARNING"


def test_max_retries_below_one_is_rejected(verify_loop):
    with pytest.raises(ValueError):
        verify_loop.run_until_criteria(
            attempt_fn=lambda: None,
            verify_fn=lambda r: {"score": 100},
            max_retries=0,
        )

"""
verify_loop.py — Loop de verificação-até-critério (KARE Context Engine)

Chama attempt_fn() repetidamente, validando cada resultado com verify_fn(),
até atingir PASS (score >= pass_threshold, padrão 80 — mesma escala do
@quality-guardian: PASS >=80, WARNING 60-79, BLOCKER <60) ou até esgotar
max_retries. Reaproveita loop_guard.ActionTracker para detectar quando as
tentativas param de progredir (a mesma falha se repete) e escalar cedo para
revisão humana (HITL), em vez de queimar todas as tentativas à toa.

Uso:
    from verify_loop import run_until_criteria

    def attempt():
        return implement_story()                # ex.: @code-author

    def verify(result):
        return quality_guardian_review(result)   # {"score": int, ...}

    outcome = run_until_criteria(attempt, verify, max_retries=3)
    if outcome.passed:
        ship(outcome.last_result)
    else:
        escalate_to_human(outcome.last_verification)  # outcome.escalated == True
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

_GUARDS_DIR = Path(__file__).resolve().parent
if str(_GUARDS_DIR) not in sys.path:
    sys.path.insert(0, str(_GUARDS_DIR))

from loop_guard import ActionTracker  # noqa: E402

PASS_THRESHOLD = 80
WARNING_THRESHOLD = 60


def _status_for_score(score: int) -> str:
    if score >= PASS_THRESHOLD:
        return "PASS"
    if score >= WARNING_THRESHOLD:
        return "WARNING"
    return "BLOCKER"


@dataclass
class VerifyLoopOutcome:
    passed: bool
    escalated: bool
    attempts: int
    last_result: Any
    last_verification: dict
    history: list = field(default_factory=list)


def run_until_criteria(
    attempt_fn: Callable[[], Any],
    verify_fn: Callable[[Any], dict],
    max_retries: int = 3,
    pass_threshold: int = PASS_THRESHOLD,
    session_id: str = "verify-loop",
    no_progress_retries: int = 1,
) -> VerifyLoopOutcome:
    """Executa attempt_fn() -> verify_fn(resultado) até score >= pass_threshold
    ou até esgotar max_retries.

    `verify_fn` deve retornar um dict com pelo menos a chave "score" (0-100,
    mesmo formato do @quality-guardian); "status" é derivado automaticamente
    se ausente. Duas tentativas seguidas com a MESMA falha (mesmo dict de
    verificação, ignorando o índice da tentativa) disparam escalonamento
    imediato via loop_guard.ActionTracker — não adianta insistir na tentativa
    seguinte, é caso para revisão humana.
    """
    if max_retries < 1:
        raise ValueError("max_retries deve ser >= 1")

    tracker = ActionTracker(session_id=session_id, max_retries=no_progress_retries, strict=False)
    history: list = []
    result = verification = None

    for attempt in range(1, max_retries + 1):
        result = attempt_fn()
        verification = dict(verify_fn(result))
        score = int(verification.get("score", 0))
        verification["score"] = score
        verification["status"] = verification.get("status") or _status_for_score(score)
        history.append({"attempt": attempt, "score": score, "status": verification["status"]})

        if score >= pass_threshold:
            return VerifyLoopOutcome(
                passed=True, escalated=False, attempts=attempt,
                last_result=result, last_verification=verification, history=history,
            )

        no_progress = tracker.check("verify_loop_failure", verification)
        if no_progress:
            return VerifyLoopOutcome(
                passed=False, escalated=True, attempts=attempt,
                last_result=result, last_verification=verification, history=history,
            )

    return VerifyLoopOutcome(
        passed=False, escalated=True, attempts=max_retries,
        last_result=result, last_verification=verification, history=history,
    )

"""
loop_guard.py — Detecção de loop de agente KARE

Detecta quando um agente está repetindo a mesma ação sem progresso e
escala para revisão humana (HITL) antes de continuar.

Como funciona:
    - Cada "ação" é identificada por um fingerprint (hash da tupla tool+args)
    - Um ActionTracker mantém contadores por fingerprint na sessão corrente
    - Se o mesmo fingerprint aparecer > max_retries vezes → dispara alerta
    - Integra com o orchestrator via check_loop() — chamada simples

Uso:
    from loop_guard import ActionTracker, LoopDetectedError

    tracker = ActionTracker(session_id="sprint-42-planning", max_retries=3)

    # Antes de cada chamada de ferramenta pelo agente:
    tracker.record("Bash", {"cmd": "python test.py"})   # OK
    tracker.record("Bash", {"cmd": "python test.py"})   # OK (2ª vez)
    tracker.record("Bash", {"cmd": "python test.py"})   # OK (3ª vez)
    tracker.record("Bash", {"cmd": "python test.py"})   # raises LoopDetectedError!

    # Versão não-exceção (retorna bool):
    if tracker.check("Read", {"path": "file.py"}):
        print("Loop detectado — parar e escalar")
"""

import hashlib
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Configurações padrão
# ---------------------------------------------------------------------------
DEFAULT_MAX_RETRIES: int = int(os.getenv("KARE_LOOP_MAX_RETRIES", "3"))
DEFAULT_SESSION_TIMEOUT_MINUTES: int = int(os.getenv("KARE_SESSION_TIMEOUT_MINUTES", "120"))  # 2h

_AUDIT_LOG_PATH = Path(__file__).parents[2] / "config" / ".loop_guard_audit.jsonl"


# ---------------------------------------------------------------------------
# Exceção
# ---------------------------------------------------------------------------
class LoopDetectedError(RuntimeError):
    """
    Levantada quando um agente repete a mesma ação além do limite.
    Contém informações suficientes para escalar ao humano.
    """
    def __init__(self, fingerprint: str, tool: str, args: dict, count: int, max_retries: int):
        super().__init__(
            f"[loop_guard] LOOP DETECTADO — A ação '{tool}' com os mesmos argumentos foi "
            f"repetida {count} vezes (limite: {max_retries}). "
            f"Fingerprint: {fingerprint[:12]}…\n"
            f"⚠️  AÇÃO NECESSÁRIA: Revise manualmente antes de continuar."
        )
        self.fingerprint = fingerprint
        self.tool = tool
        self.args = args
        self.count = count
        self.max_retries = max_retries


class SessionTimeoutError(RuntimeError):
    """Levantada quando a sessão excede o tempo máximo configurado."""
    def __init__(self, session_id: str, elapsed_minutes: float, timeout_minutes: int):
        super().__init__(
            f"[loop_guard] TIMEOUT DE SESSÃO — Sessão '{session_id}' está ativa há "
            f"{elapsed_minutes:.0f} min (limite: {timeout_minutes} min). "
            f"Execute /compress-session ou inicie nova sessão."
        )
        self.session_id = session_id
        self.elapsed_minutes = elapsed_minutes


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def _fingerprint(tool: str, args: Any) -> str:
    """Gera hash determinístico da dupla (tool, args) para identificar ações repetidas."""
    payload = json.dumps({"tool": tool, "args": args}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _write_audit(session_id: str, tool: str, args: Any, count: int, loop: bool) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "tool": tool,
        "args_preview": str(args)[:120],
        "count": count,
        "loop_triggered": loop,
    }
    try:
        with _AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------
class ActionTracker:
    """
    Rastreia ações de um agente e detecta loops.

    Parâmetros:
        session_id          : Identificador da sessão (ex: "sprint-42-planning")
        max_retries         : Quantas vezes a mesma ação pode se repetir antes do alerta.
                              Padrão: KARE_LOOP_MAX_RETRIES (env) ou 3.
        session_timeout_min : Após quantos minutos a sessão é considerada travada.
                              Padrão: KARE_SESSION_TIMEOUT_MINUTES (env) ou 120.
        strict              : True → levanta exceção no loop. False → loga e retorna bool.
    """

    def __init__(
        self,
        session_id: str = "default",
        max_retries: int = DEFAULT_MAX_RETRIES,
        session_timeout_min: int = DEFAULT_SESSION_TIMEOUT_MINUTES,
        strict: bool = True,
    ):
        self.session_id = session_id
        self.max_retries = max_retries
        self.session_timeout_min = session_timeout_min
        self.strict = strict
        self._start_time = datetime.now(timezone.utc)
        self._counts: dict[str, int] = defaultdict(int)
        self._last_seen: dict[str, str] = {}  # fingerprint → iso timestamp

    # ------------------------------------------------------------------
    def record(self, tool: str, args: Any = None) -> int:
        """
        Registra uma ação e verifica loop.
        Retorna o número de vezes que esta ação foi vista.
        Levanta LoopDetectedError (strict) ou loga aviso (não-strict).
        """
        self._check_session_timeout()

        fp = _fingerprint(tool, args or {})
        self._counts[fp] += 1
        self._last_seen[fp] = datetime.now(timezone.utc).isoformat()
        count = self._counts[fp]

        loop = count > self.max_retries
        _write_audit(self.session_id, tool, args, count, loop)

        if loop:
            if self.strict:
                raise LoopDetectedError(fp, tool, args or {}, count, self.max_retries)
            logging.warning(
                "[loop_guard] LOOP — sessão='%s' ferramenta='%s' repetiu %d vezes (limite: %d).",
                self.session_id, tool, count, self.max_retries,
            )
        elif count == self.max_retries:
            logging.warning(
                "[loop_guard] AVISO — sessão='%s' ferramenta='%s' na %dª execução. "
                "Próxima repetição disparará alerta de loop.",
                self.session_id, tool, count,
            )

        return count

    # ------------------------------------------------------------------
    def check(self, tool: str, args: Any = None) -> bool:
        """
        Versão não-exceção: registra a ação e retorna True se loop detectado.
        Útil para code paths que preferem um if ao try/except.

        Funciona independente do modo `strict` do tracker: em modo strict,
        `record()` levanta e o except converte para True; em modo não-strict,
        `record()` não levanta (só loga), então o resultado é calculado a
        partir da contagem retornada.
        """
        try:
            count = self.record(tool, args)
            return count > self.max_retries
        except LoopDetectedError:
            return True

    # ------------------------------------------------------------------
    def reset_action(self, tool: str, args: Any = None) -> None:
        """Reseta o contador de uma ação específica (ex: após intervenção humana)."""
        fp = _fingerprint(tool, args or {})
        self._counts.pop(fp, None)
        self._last_seen.pop(fp, None)
        logging.info("[loop_guard] Contador resetado para tool='%s' na sessão='%s'.", tool, self.session_id)

    # ------------------------------------------------------------------
    def reset_all(self) -> None:
        """Reseta todos os contadores da sessão (equivale a nova sessão)."""
        self._counts.clear()
        self._last_seen.clear()
        self._start_time = datetime.now(timezone.utc)
        logging.info("[loop_guard] Sessão '%s' resetada.", self.session_id)

    # ------------------------------------------------------------------
    def elapsed_minutes(self) -> float:
        delta = datetime.now(timezone.utc) - self._start_time
        return delta.total_seconds() / 60

    # ------------------------------------------------------------------
    def _check_session_timeout(self) -> None:
        elapsed = self.elapsed_minutes()
        if elapsed > self.session_timeout_min:
            if self.strict:
                raise SessionTimeoutError(self.session_id, elapsed, self.session_timeout_min)
            logging.warning(
                "[loop_guard] TIMEOUT — Sessão '%s' está ativa há %.0f min (limite: %d min). "
                "Considere executar /compress-session.",
                self.session_id, elapsed, self.session_timeout_min,
            )

    # ------------------------------------------------------------------
    def summary(self) -> dict:
        """Retorna resumo do estado atual da sessão."""
        return {
            "session_id": self.session_id,
            "elapsed_minutes": round(self.elapsed_minutes(), 1),
            "timeout_minutes": self.session_timeout_min,
            "max_retries": self.max_retries,
            "unique_actions_tracked": len(self._counts),
            "actions_near_limit": [
                {"fingerprint": fp[:12], "count": c}
                for fp, c in self._counts.items()
                if c >= self.max_retries
            ],
        }


# ---------------------------------------------------------------------------
# Função de conveniência para uso rápido no orchestrator
# ---------------------------------------------------------------------------
_default_tracker: Optional[ActionTracker] = None


def get_session_tracker(
    session_id: str = "orchestrator-default",
    max_retries: int = DEFAULT_MAX_RETRIES,
    strict: bool = True,
) -> ActionTracker:
    """
    Retorna (ou cria) o tracker de sessão global do orchestrator.
    Use esta função em vez de criar múltiplos ActionTracker no mesmo fluxo.

    Exemplo rápido no orchestrator:
        from loop_guard import get_session_tracker
        tracker = get_session_tracker("sprint-42")
        tracker.record("Bash", {"cmd": "pytest"})
    """
    global _default_tracker
    if _default_tracker is None or _default_tracker.session_id != session_id:
        _default_tracker = ActionTracker(session_id, max_retries=max_retries, strict=strict)
    return _default_tracker


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    def _usage():
        print(
            "Uso:\n"
            "  python loop_guard.py simulate <sessao> <ferramenta> <n_repeticoes>\n"
            "  python loop_guard.py audit [--last N]\n"
            "  python loop_guard.py status\n\n"
            "Variáveis de ambiente:\n"
            "  KARE_LOOP_MAX_RETRIES          (padrão: 3)\n"
            "  KARE_SESSION_TIMEOUT_MINUTES   (padrão: 120)\n"
        )

    args = sys.argv[1:]
    if not args:
        _usage()
        sys.exit(0)

    cmd = args[0]

    if cmd == "simulate" and len(args) == 4:
        _, session, tool, n_str = args
        n = int(n_str)
        tracker = ActionTracker(session_id=session, strict=False)
        print(f"Simulando {n}x chamada de '{tool}' na sessão '{session}'...\n")
        for i in range(1, n + 1):
            loop = tracker.check(tool, {"test": "arg"})
            status = "❌ LOOP" if loop else "✅ OK"
            print(f"  Iteração {i}: {status}")

    elif cmd == "audit":
        last = int(args[2]) if len(args) == 3 and args[1] == "--last" else 20
        if not _AUDIT_LOG_PATH.exists():
            print("Audit log vazio.")
        else:
            lines = _AUDIT_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
            for line in lines[-last:]:
                e = json.loads(line)
                loop_flag = " ❌ LOOP!" if e.get("loop_triggered") else ""
                print(f"  {e['ts']}  [{e['session_id']}]  {e['tool']} (x{e['count']}){loop_flag}")

    elif cmd == "status":
        tracker = get_session_tracker()
        s = tracker.summary()
        print(json.dumps(s, indent=2, ensure_ascii=False))

    else:
        _usage()
        sys.exit(1)

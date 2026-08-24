"""
kare_telemetry.py — Shim de compatibilidade

Redireciona todos os comandos para kare_rag.py telemetry (SQLite/kare_telemetry.db).

Uso (mesma interface anterior):
    python kare_telemetry.py log --agent X --command /Y --status success --latency-ms N
    python kare_telemetry.py dashboard [--last N]
    python kare_telemetry.py stats [--agent X] [--last N]
    python kare_telemetry.py export [--output path.json]

Fonte canônica:
    python .agent/scripts/ai/kare_rag.py telemetry log ...
    python .agent/scripts/ai/kare_rag.py telemetry stats
    python .agent/scripts/ai/kare_rag.py telemetry session-start
    python .agent/scripts/ai/kare_rag.py telemetry session-end --session-id N
"""

import sys
import subprocess
from pathlib import Path

_RAG = Path(__file__).parent.parent / "ai" / "kare_rag.py"

ACTION_MAP = {
    "success": "query",
    "artifact": "artifact_created",
    "review": "artifact_reviewed",
    "planning": "planning",
    "analysis": "analysis",
    "other": "other",
}


def _rag(*args):
    """Executa kare_rag.py com os argumentos fornecidos."""
    return subprocess.run([sys.executable, str(_RAG), *args])


def main():
    if len(sys.argv) < 2:
        print("Uso: kare_telemetry.py [log|dashboard|stats|export]")
        print("  Fonte canônica: python .agent/scripts/ai/kare_rag.py telemetry ...")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "log":
        # Mapeia --status para action-type
        status = "query"
        agent  = "unknown"
        latency_ms = None
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]; i += 2
            elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                status = ACTION_MAP.get(sys.argv[i + 1], "query"); i += 2
            elif sys.argv[i] == "--latency-ms" and i + 1 < len(sys.argv):
                latency_ms = sys.argv[i + 1]; i += 2
            else:
                i += 1
        rag_args = ["telemetry", "log", "--agent", agent, "--action-type", status]
        if latency_ms:
            rag_args += ["--duration-ms", latency_ms]
        _rag(*rag_args)

    elif cmd in ("dashboard", "stats"):
        _rag("telemetry", "stats")

    elif cmd == "export":
        print("[kare_telemetry] export não suportado na arquitetura SQLite.")
        print("  Use: python .agent/scripts/ai/kare_rag.py telemetry stats")

    elif cmd in ("sync", "aggregate"):
        print(f"[kare_telemetry] '{cmd}' removido — telemetria centralizada no SQLite local.")
        print("  Use: python .agent/scripts/ai/kare_rag.py telemetry stats --days 30")

    else:
        print(f"[kare_telemetry] Comando desconhecido: {cmd}")
        print("  Use: python .agent/scripts/ai/kare_rag.py telemetry ...")
        sys.exit(1)


if __name__ == "__main__":
    main()

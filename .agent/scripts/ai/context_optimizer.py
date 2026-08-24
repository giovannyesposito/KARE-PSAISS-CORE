"""
KARE Context Optimizer — Context Window Optimization (Fase 3 / F3.3)
=====================================================================
Ativa e coordena as 3 estratégias de otimização de contexto do KARE:

  1. TTL Decay        — invoca decay_manager.py para marcar nós stale
  2. Relevance Scoring — pontua e prioriza nós pelo overlap semântico com a tarefa
  3. Session Check    — alerta quando sessão excede 120 min (threshold de /compress-session)

Uso:
    # Otimização completa (decay + scoring + session check)
    python context_optimizer.py optimize --context <slug>

    # Apenas TTL decay (identifica nós stale no contexto)
    python context_optimizer.py decay --context <slug>

    # Ver nós stale para um contexto
    python context_optimizer.py stale --context <slug>

    # Score de relevância dos nós (top N mais relevantes para uma query)
    python context_optimizer.py score --context <slug> --query "texto da tarefa" --top 10

    # Verificar se sessão deve ser comprimida
    python context_optimizer.py session-check --session-start "2026-05-14T10:00:00"

    # Relatório completo de saúde do contexto
    python context_optimizer.py report --context <slug>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Configuration ─────────────────────────────────────────────────────────────

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = Path(__file__).parent

API_BASE = os.environ.get("KARE_API_BASE", "http://localhost:8000")

SESSION_COMPRESS_THRESHOLD_MIN = 120   # minutos → recomendar /compress-session
STALE_THRESHOLD   = 0.60               # confidence < 0.60 → stale
CRITICAL_THRESHOLD = 0.40              # confidence < 0.40 → critical


# ── API helpers ───────────────────────────────────────────────────────────────

def _api_get(path: str, params: dict | None = None) -> dict | list | None:
    try:
        import urllib.request
        import urllib.parse
        url = f"{API_BASE}{path}"
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _api_available() -> bool:
    result = _api_get("/health")
    return result is not None


# ── 1. TTL Decay ──────────────────────────────────────────────────────────────

def run_decay(context: str | None = None, dry_run: bool = False) -> dict:
    """
    Invoca decay_manager.py --check [--refresh-stale] para o contexto dado.
    Retorna summary com nós afetados.
    """
    decay_script = SCRIPTS_DIR / "decay_manager.py"
    if not decay_script.exists():
        return {"error": f"decay_manager.py não encontrado em {decay_script}"}

    cmd = [sys.executable, str(decay_script), "--check"]
    if not dry_run:
        cmd.append("--refresh-stale")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "dry_run": dry_run,
        }
    except subprocess.TimeoutExpired:
        return {"error": "decay_manager.py timeout (>60s). API RAG pode estar inacessível."}
    except Exception as e:
        return {"error": str(e)}


def list_stale_nodes(context: str | None = None) -> list[dict]:
    """Query RAG API for nodes with confidence below STALE_THRESHOLD."""
    params = {"limit": 200}
    if context:
        params["context"] = context

    nodes = _api_get("/nodes", params)
    if not nodes:
        return []

    stale: list[dict] = []
    for node in (nodes if isinstance(nodes, list) else []):
        meta = node.get("metadata") or {}
        confidence = meta.get("confidence_score")
        if confidence is not None and float(confidence) < STALE_THRESHOLD:
            stale.append({
                "id":         node.get("id"),
                "title":      node.get("title", "—"),
                "type":       node.get("node_type", "—"),
                "confidence": float(confidence),
                "status":     "critical" if float(confidence) < CRITICAL_THRESHOLD else "stale",
            })
    stale.sort(key=lambda x: x["confidence"])
    return stale


# ── 2. Relevance Scoring ──────────────────────────────────────────────────────

def score_nodes(query: str, context: str | None = None, top: int = 10) -> list[dict]:
    """
    Fetches nodes from the RAG API and scores them by keyword overlap with query.
    Returns top-N sorted by relevance descending.
    """
    params = {"limit": 500}
    if context:
        params["context"] = context

    nodes = _api_get("/nodes", params)
    if not nodes:
        return []

    query_words = set(re.sub(r"[^\w\s]", " ", query.lower()).split())
    if not query_words:
        return []

    scored: list[dict] = []
    for node in (nodes if isinstance(nodes, list) else []):
        title   = node.get("title", "")
        content = node.get("content", "")
        combined = f"{title} {content}".lower()
        node_words = set(re.sub(r"[^\w\s]", " ", combined).split())
        overlap = query_words & node_words
        if not overlap:
            continue
        score = len(overlap) / max(len(query_words), 1)
        scored.append({
            "id":      node.get("id"),
            "title":   title,
            "type":    node.get("node_type", "—"),
            "context": node.get("context_slug", "—"),
            "score":   round(score, 3),
            "overlap": sorted(overlap)[:5],
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top]


# ── 3. Session Check ──────────────────────────────────────────────────────────

def check_session(session_start: str) -> dict:
    """
    Check if the session has exceeded the compression threshold.

    Args:
        session_start: ISO8601 datetime string (e.g. "2026-05-14T10:00:00")

    Returns dict with: elapsed_min, should_compress, message
    """
    try:
        start = datetime.fromisoformat(session_start)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        elapsed = int((now - start).total_seconds() / 60)
    except ValueError as e:
        return {"error": f"Formato de data inválido: {e}. Use ISO8601 (ex: 2026-05-14T10:00:00)"}

    should_compress = elapsed >= SESSION_COMPRESS_THRESHOLD_MIN
    remaining = SESSION_COMPRESS_THRESHOLD_MIN - elapsed

    return {
        "session_start":   session_start,
        "elapsed_min":     elapsed,
        "threshold_min":   SESSION_COMPRESS_THRESHOLD_MIN,
        "should_compress": should_compress,
        "message": (
            f"⚠️  Sessão com {elapsed} min. Recomendado: /compress-session"
            if should_compress else
            f"✅ Sessão OK ({elapsed} min). Compressão recomendada em {remaining} min."
        ),
    }


# ── Full optimize + report ────────────────────────────────────────────────────

def run_optimize(context: str | None, dry_run: bool = False) -> None:
    print(f"KARE Context Optimizer — contexto: {context or 'global'}\n")

    # 1. API availability
    if not _api_available():
        print("⚠️  API RAG inacessível (http://localhost:8000). Pulando decay e scoring.")
        print("   Verifique os bancos RAG: python .agent/scripts/ai/kare_rag.py status\n")
    else:
        # 1. TTL Decay
        print("1️⃣  TTL Decay ─────────────────────────────")
        decay_result = run_decay(context, dry_run=dry_run)
        if "error" in decay_result:
            print(f"   ❌ {decay_result['error']}")
        else:
            print(f"   Exit code: {decay_result['exit_code']}")
            if decay_result["stdout"]:
                for line in decay_result["stdout"].splitlines()[:10]:
                    print(f"   {line}")
        print()

        # 2. Stale nodes summary
        print("2️⃣  Nós Stale ──────────────────────────────")
        stale = list_stale_nodes(context)
        if not stale:
            print("   ✅ Nenhum nó stale encontrado.")
        else:
            critical_count = sum(1 for n in stale if n["status"] == "critical")
            stale_count = len(stale) - critical_count
            print(f"   ⚠️  {len(stale)} nós stale: {critical_count} CRITICAL | {stale_count} STALE")
            for n in stale[:5]:
                icon = "🔴" if n["status"] == "critical" else "🟡"
                print(f"   {icon} [{n['confidence']:.2f}] {n['title'][:60]}")
            if len(stale) > 5:
                print(f"   ... e mais {len(stale) - 5}")
        print()

    # 3. Session check (best-effort — no start time given in optimize mode)
    print("3️⃣  Session Check ──────────────────────────")
    print("   ℹ️  Use 'python context_optimizer.py session-check --session-start <ISO8601>'")
    print("      para verificar se a sessão atual precisa de /compress-session.")
    print()
    print("✅ Otimização concluída.")


def run_report(context: str | None) -> None:
    """Full health report for a context."""
    print(f"╔═══════════════════════════════════════════════════════╗")
    print(f"║  KARE Context Health Report — {context or 'global':<25}║")
    print(f"╚═══════════════════════════════════════════════════════╝\n")

    if not _api_available():
        print("❌ API RAG inacessível. Relatório parcial.\n")
        return

    params = {"limit": 500}
    if context:
        params["context"] = context
    nodes = _api_get("/nodes", params) or []
    total = len(nodes) if isinstance(nodes, list) else 0

    stale = list_stale_nodes(context)
    critical = [n for n in stale if n["status"] == "critical"]

    # Confidence distribution
    scores = []
    for node in (nodes if isinstance(nodes, list) else []):
        meta = node.get("metadata") or {}
        c = meta.get("confidence_score")
        if c is not None:
            scores.append(float(c))

    avg_conf = round(sum(scores) / len(scores), 2) if scores else None

    print(f"  Total de nós:        {total}")
    print(f"  Confidence média:    {avg_conf if avg_conf else '—'}")
    print(f"  Nós stale (<0.60):   {len(stale)}")
    print(f"  Nós críticos (<0.40): {len(critical)}")
    print()

    if critical:
        print("  🔴 Nós críticos (ação necessária):")
        for n in critical:
            print(f"     [{n['confidence']:.2f}] {n['title'][:60]}")
    elif stale:
        print("  🟡 Nós stale (re-enriquecimento recomendado):")
        for n in stale[:5]:
            print(f"     [{n['confidence']:.2f}] {n['title'][:60]}")
    else:
        print("  ✅ Todos os nós com confidence saudável.")

    print()
    health_pct = round((1 - len(stale) / max(total, 1)) * 100)
    bar = "█" * (health_pct // 10) + "░" * (10 - health_pct // 10)
    print(f"  Context Health:  [{bar}] {health_pct}%")


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_optimize(args: argparse.Namespace) -> None:
    run_optimize(args.context, dry_run=args.dry_run)


def cmd_decay(args: argparse.Namespace) -> None:
    result = run_decay(args.context, dry_run=getattr(args, "dry_run", False))
    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result.get("stdout", ""))
    if result.get("stderr"):
        print(result["stderr"], file=sys.stderr)


def cmd_stale(args: argparse.Namespace) -> None:
    if not _api_available():
        print("❌ API RAG inacessível.", file=sys.stderr)
        sys.exit(1)
    nodes = list_stale_nodes(args.context)
    if not nodes:
        print(f"✅ Nenhum nó stale para contexto: {args.context or 'global'}")
        return
    print(f"Nós stale — contexto: {args.context or 'global'}\n")
    for n in nodes:
        icon = "🔴" if n["status"] == "critical" else "🟡"
        print(f"  {icon} [{n['confidence']:.2f}] [{n['type']}] {n['title']}")


def cmd_score(args: argparse.Namespace) -> None:
    if not _api_available():
        print("❌ API RAG inacessível.", file=sys.stderr)
        sys.exit(1)
    results = score_nodes(args.query, args.context, top=args.top)
    if not results:
        print("Nenhum nó encontrado para essa query.")
        return
    print(f"Top {len(results)} nós mais relevantes para: '{args.query}'\n")
    for r in results:
        print(f"  [{r['score']:.3f}] [{r['type']}] {r['title']}")
        print(f"           overlap: {', '.join(r['overlap'])}")
        print()


def cmd_session_check(args: argparse.Namespace) -> None:
    result = check_session(args.session_start)
    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])
    print(f"   Início: {result['session_start']} | Elapsed: {result['elapsed_min']} min")
    if result["should_compress"]:
        print("\n   Execute no chat: /compress-session")
        sys.exit(2)  # exit 2 = needs compress (distinct from error)


def cmd_report(args: argparse.Namespace) -> None:
    run_report(args.context)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="context_optimizer",
        description="KARE Context Window Optimizer — TTL decay, relevance scoring, session check",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # optimize
    opt = sub.add_parser("optimize", help="Run full optimization (decay + stale + session hint)")
    opt.add_argument("--context", default=None, help="Context slug (e.g. ini-518)")
    opt.add_argument("--dry-run", action="store_true", help="Decay check only, no re-enrichment")

    # decay
    dec = sub.add_parser("decay", help="Run TTL decay via decay_manager.py")
    dec.add_argument("--context", default=None)
    dec.add_argument("--dry-run", action="store_true")

    # stale
    sta = sub.add_parser("stale", help="List stale nodes for a context")
    sta.add_argument("--context", default=None)

    # score
    sc = sub.add_parser("score", help="Score nodes by relevance to a query")
    sc.add_argument("--context", default=None)
    sc.add_argument("--query", required=True, help="Task description to score against")
    sc.add_argument("--top", type=int, default=10)

    # session-check
    sess = sub.add_parser("session-check", help="Check if session needs compression")
    sess.add_argument("--session-start", required=True, help="ISO8601 datetime of session start")

    # report
    rep = sub.add_parser("report", help="Full context health report")
    rep.add_argument("--context", default=None)

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    cmds = {
        "optimize":      cmd_optimize,
        "decay":         cmd_decay,
        "stale":         cmd_stale,
        "score":         cmd_score,
        "session-check": cmd_session_check,
        "report":        cmd_report,
    }
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()

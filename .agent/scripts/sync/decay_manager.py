"""
KARE Decay Manager — Fase 5
================================================
Gerencia o ciclo de vida e confiança das WIKI_PAGEs no Context Engine.

Conceito: Conhecimento envelhece. Uma WIKI_PAGE gerada há 30+ dias, ou cuja
página original no Confluence foi atualizada, deve ser marcada como stale
e re-enriquecida.

Campos utilizados no metadata do nó WIKI_PAGE:
  - confidence_score: float (0-1) — confiança atual na acurácia do conhecimento
  - last_validated_at: ISO8601 — última vez que o nó foi validado/re-enriquecido
  - enriched_at: ISO8601 — quando foi enriquecido pela primeira vez
  - confluence_page_id: str — ID da página original no Confluence

Regras de decay:
  - Idade > 30 dias → confidence -0.10 por semana adicional
  - Conflitos detectados no grafo (CONFLICTS_WITH edges) → confidence -0.15
  - Confidence < 0.60 → status = "stale" (borda vermelha tracejada no grafo)
  - Confidence < 0.40 → status = "critical" (remover do Confluence se publicado)

Uso:
    # Verificar todos os WIKI_PAGEs e calcular decay
    python decay_manager.py --check

    # Listar nós stale (confidence < 0.60)
    python decay_manager.py --list-stale

    # Re-enriquecer todos os nós stale
    python decay_manager.py --refresh-stale

    # Re-enriquecer um nó específico
    python decay_manager.py --refresh-node 42

    # Aplicar decay e re-enriquecer em um único comando
    python decay_manager.py --check --refresh-stale
"""

import os
import argparse
import sys
from pathlib import Path
import requests
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from rag_auth import rag_session as _new_rag_session  # noqa: E402

_rs = _new_rag_session()
# ── Configuração ──────────────────────────────────────────────────────────────

API_BASE = os.environ.get("KARE_API_BASE", "http://localhost:8000")
CONFLUENCE_BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://wiki.example.com")
CONFLUENCE_USER = os.environ.get("CONFLUENCE_USER", "")
CONFLUENCE_TOKEN = os.environ.get("CONFLUENCE_TOKEN", "")

STALE_THRESHOLD = 0.60          # Abaixo disso → stale (aviso no context-resolver)
CRITICAL_THRESHOLD = 0.40       # Abaixo disso → crítico (remover do Confluence)
MAX_AGE_DAYS = 30               # Idade máxima sem re-validação
DECAY_PER_EXTRA_WEEK = 0.10     # Penalidade por semana adicional além de 30 dias
CONFLICT_PENALTY = 0.15         # Penalidade por cada aresta CONFLICTS_WITH

WIKI_ENRICHER_SCRIPT = os.path.join(
    os.path.dirname(__file__), "wiki_enricher.py"
)

# ── Utilitários ───────────────────────────────────────────────────────────────

def get_all_wiki_nodes() -> list:
    """Busca todos os nós WIKI_PAGE"""
    try:
        r = _rs.get(f"{API_BASE}/nodes", params={"node_type": "wiki_page", "limit": 500}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao buscar WIKI_PAGEs: {e}")
        return []


def get_conflict_count(node_id: int) -> int:
    """Conta arestas CONFLICTS_WITH saindo deste nó"""
    try:
        r = _rs.get(f"{API_BASE}/nodes/{node_id}/edges", timeout=10)
        r.raise_for_status()
        data = r.json()
        return sum(1 for e in data.get("outgoing", []) if e.get("relation_type") == "conflicts_with")
    except Exception:
        return 0


def get_confluence_last_modified(page_id: str) -> Optional[datetime]:
    """
    Verifica a data de última modificação da página original no Confluence.
    Retorna None se não conseguir verificar.
    """
    if not CONFLUENCE_USER or not CONFLUENCE_TOKEN or not page_id:
        return None
    try:
        r = _rs.get(
            f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}",
            params={"expand": "version"},
            auth=(CONFLUENCE_USER, CONFLUENCE_TOKEN),
            timeout=10
        )
        r.raise_for_status()
        when_str = r.json().get("version", {}).get("when")
        if when_str:
            return datetime.fromisoformat(when_str.replace("Z", "+00:00"))
    except Exception:
        pass
    return None


def calculate_decay(node: dict) -> dict:
    """
    Calcula o confidence score com decay aplicado.
    Retorna {"node_id", "current_confidence", "decayed_confidence", "reason", "status"}
    """
    node_id = node.get("id")
    metadata = node.get("metadata") or {}
    title = node.get("title", f"Node {node_id}")

    base_confidence = float(metadata.get("confidence_score", 0.5))
    enriched_at_str = metadata.get("enriched_at") or metadata.get("created_at") or node.get("created_at", "")
    last_validated_str = metadata.get("last_validated_at") or enriched_at_str

    now = datetime.now(timezone.utc)
    decay_applied = 0.0
    reasons = []

    # Calcular idade
    try:
        last_validated = datetime.fromisoformat(last_validated_str.replace("Z", "+00:00"))
        age_days = (now - last_validated).days

        if age_days > MAX_AGE_DAYS:
            extra_weeks = (age_days - MAX_AGE_DAYS) / 7
            age_decay = extra_weeks * DECAY_PER_EXTRA_WEEK
            decay_applied += age_decay
            reasons.append(f"Idade: {age_days}d (+{age_decay:.2f} decay)")
    except Exception:
        pass

    # Penalizar por conflitos no grafo
    conflicts = get_conflict_count(node_id)
    if conflicts > 0:
        conflict_decay = conflicts * CONFLICT_PENALTY
        decay_applied += conflict_decay
        reasons.append(f"{conflicts} conflito(s) no grafo (+{conflict_decay:.2f} decay)")

    # Calcular confidence final
    decayed_confidence = max(0.0, base_confidence - decay_applied)

    if decayed_confidence >= STALE_THRESHOLD:
        status = "healthy"
    elif decayed_confidence >= CRITICAL_THRESHOLD:
        status = "stale"
    else:
        status = "critical"

    return {
        "node_id": node_id,
        "title": title,
        "base_confidence": base_confidence,
        "decay_applied": decay_applied,
        "decayed_confidence": decayed_confidence,
        "reasons": reasons,
        "status": status,
        "metadata": metadata
    }


def apply_decay_to_node(node_id: int, decayed_confidence: float) -> bool:
    """Persiste o confidence score calculado no nó"""
    try:
        r = _rs.patch(
            f"{API_BASE}/nodes/{node_id}/metadata",
            json={"confidence_score": decayed_confidence},
            timeout=10
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[AVISO] Falha ao atualizar confidence do nó {node_id}: {e}")
        return False


def refresh_node(node_id: int):
    """Re-enriquece um nó via wiki_enricher.py"""
    print(f"[...] Re-enriquecendo nó {node_id}...")
    try:
        subprocess.run(
            [sys.executable, WIKI_ENRICHER_SCRIPT, "--node-id", str(node_id), "--obsidian-sync"],
            check=True
        )
        # Atualizar last_validated_at
        _rs.patch(
            f"{API_BASE}/nodes/{node_id}/metadata",
            json={"last_validated_at": datetime.utcnow().isoformat()},
            timeout=10
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] wiki_enricher.py falhou para nó {node_id}: {e}")
    except Exception as e:
        print(f"[AVISO] Falha ao atualizar last_validated_at do nó {node_id}: {e}")


def unpublish_from_confluence(page_id: str, title: str):
    """
    Adiciona aviso de conteúdo crítico/desatualizado na página Confluence.
    Não deleta — apenas prepend de banner de aviso.
    """
    if not CONFLUENCE_USER or not CONFLUENCE_TOKEN:
        return
    try:
        # Buscar versão atual
        r = _rs.get(
            f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}",
            params={"expand": "body.storage,version"},
            auth=(CONFLUENCE_USER, CONFLUENCE_TOKEN),
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        current_version = data.get("version", {}).get("number", 1)
        current_body = data.get("body", {}).get("storage", {}).get("value", "")

        warning_banner = (
            '<ac:structured-macro ac:name="warning">'
            '<ac:rich-text-body>'
            '<p><strong>⚠️ ATENÇÃO:</strong> Esta página de conhecimento está com confidence crítico '
            '(&lt;40%). O conteúdo pode estar desatualizado. Execute o KARE Decay Manager para re-enriquecer.</p>'
            '</ac:rich-text-body>'
            '</ac:structured-macro>'
        )

        if "ATENÇÃO" not in current_body:
            new_body = warning_banner + current_body
            _rs.put(
                f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}",
                json={
                    "version": {"number": current_version + 1},
                    "title": title,
                    "type": "page",
                    "body": {"storage": {"value": new_body, "representation": "storage"}}
                },
                auth=(CONFLUENCE_USER, CONFLUENCE_TOKEN),
                timeout=20
            )
            print(f"[OK] Banner de aviso adicionado ao Confluence: {page_id}")
    except Exception as e:
        print(f"[AVISO] Falha ao adicionar banner no Confluence {page_id}: {e}")


# ── Lógica Principal ──────────────────────────────────────────────────────────

def check_all(apply_decay: bool = True) -> list:
    """Verifica todos os WIKI_PAGEs e aplica decay. Retorna lista de resultados."""
    nodes = get_all_wiki_nodes()
    if not nodes:
        print("[OK] Nenhum WIKI_PAGE encontrado.")
        return []

    print(f"[...] Verificando {len(nodes)} WIKI_PAGE(s)...\n")
    results = []

    for node in nodes:
        result = calculate_decay(node)
        results.append(result)

        status_icon = {"healthy": "✅", "stale": "⚠️", "critical": "🔴"}.get(result["status"], "?")
        print(
            f"{status_icon} [{result['decayed_confidence']:.0%}] {result['title'][:60]}"
            + (f" — {', '.join(result['reasons'])}" if result["reasons"] else "")
        )

        if apply_decay and result["decay_applied"] > 0:
            apply_decay_to_node(result["node_id"], result["decayed_confidence"])

        # Adicionar banner no Confluence para críticos
        if result["status"] == "critical":
            conf_id = result["metadata"].get("confluence_page_id")
            if conf_id:
                unpublish_from_confluence(conf_id, result["title"])

    healthy = sum(1 for r in results if r["status"] == "healthy")
    stale = sum(1 for r in results if r["status"] == "stale")
    critical = sum(1 for r in results if r["status"] == "critical")

    print(f"\n[SUMMARY] ✅ {healthy} saudáveis | ⚠️ {stale} stale | 🔴 {critical} críticos")
    return results


def list_stale(min_confidence: float = None) -> list:
    """Lista nós com confidence abaixo do threshold stale"""
    try:
        r = _rs.get(
            f"{API_BASE}/wiki",
            params={"limit": 500},
            timeout=15
        )
        r.raise_for_status()
        nodes = r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao buscar WIKI_PAGEs: {e}")
        return []

    threshold = min_confidence or STALE_THRESHOLD
    stale_nodes = [
        n for n in nodes
        if float((n.get("metadata") or {}).get("confidence_score", 1.0)) < threshold
    ]

    if not stale_nodes:
        print(f"[OK] Nenhum WIKI_PAGE com confidence < {threshold:.0%}")
        return []

    print(f"[...] {len(stale_nodes)} nó(s) stale (confidence < {threshold:.0%}):\n")
    for n in sorted(stale_nodes, key=lambda x: (x.get("metadata") or {}).get("confidence_score", 1.0)):
        conf = (n.get("metadata") or {}).get("confidence_score", 0.0)
        print(f"  [{conf:.0%}] ID={n['id']} — {n.get('title', '')[:70]}")

    return stale_nodes


def refresh_all_stale():
    """Re-enriquece todos os nós stale"""
    stale = list_stale()
    if not stale:
        return
    print(f"\n[...] Re-enriquecendo {len(stale)} nó(s)...\n")
    for node in stale:
        refresh_node(node["id"])
    print(f"\n[CONCLUÍDO] {len(stale)} nó(s) re-enriquecidos.")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="KARE Decay Manager — Ciclo de Vida WIKI_PAGEs (Fase 5)")
    parser.add_argument("--check", action="store_true", help="Verificar e aplicar decay em todos os WIKI_PAGEs")
    parser.add_argument("--list-stale", action="store_true", help="Listar nós com confidence baixo")
    parser.add_argument("--refresh-stale", action="store_true", help="Re-enriquecer todos os nós stale")
    parser.add_argument("--refresh-node", type=int, help="Re-enriquecer um nó específico por ID")
    parser.add_argument("--threshold", type=float, default=STALE_THRESHOLD,
                        help=f"Threshold de stale (padrão: {STALE_THRESHOLD})")
    parser.add_argument("--no-apply", action="store_true",
                        help="Verificar sem persistir decay (só relatório)")

    args = parser.parse_args()

    global STALE_THRESHOLD
    STALE_THRESHOLD = args.threshold

    if args.check:
        check_all(apply_decay=not args.no_apply)

    if args.list_stale:
        list_stale(min_confidence=args.threshold)

    if args.refresh_stale:
        refresh_all_stale()

    if args.refresh_node:
        refresh_node(args.refresh_node)

    if not any([args.check, args.list_stale, args.refresh_stale, args.refresh_node]):
        parser.print_help()


if __name__ == "__main__":
    main()


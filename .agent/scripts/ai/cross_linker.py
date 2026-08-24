"""
KARE Cross-Linker — Fase 4
================================================
Detecta automaticamente relações semânticas entre nós WIKI_PAGE e cria
arestas SIMILAR_TO e REUSES_PATTERN no grafo de conhecimento.

Algoritmo:
  1. Para cada WIKI_PAGE sem cross-links:
     a. Busca top-K similares via /similar/{node_id} (cosine similarity)
     b. Para cada similar com score >= threshold (0.82):
        - Chama LLM para classificar a relação: SIMILAR_TO vs REUSES_PATTERN vs CONFLICTS_WITH
        - Cria aresta tipada com weight = cosine_score
  2. Deduplicação: não cria aresta se já existe entre os dois nós com mesmo tipo

Uso:
    # Processar todos os WIKI_PAGEs sem cross-links
    python cross_linker.py --all

    # Processar um nó específico
    python cross_linker.py --node-id 42

    # Ajustar threshold (padrão: 0.82)
    python cross_linker.py --all --threshold 0.75

    # Dry-run (não cria arestas, só mostra o que seria criado)
    python cross_linker.py --all --dry-run
"""

import os
import json
import argparse
import sys
from pathlib import Path
import requests
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from rag_auth import rag_session as _new_rag_session  # noqa: E402

_rs = _new_rag_session()
# ── Configuração ──────────────────────────────────────────────────────────────

API_BASE = os.environ.get("KARE_API_BASE", "http://localhost:8000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_THRESHOLD = float(os.environ.get("CROSS_LINK_THRESHOLD", "0.82"))
TOP_K_CANDIDATES = 10

# ── Prompt de Classificação de Relação ────────────────────────────────────────

CLASSIFICATION_PROMPT = """Você é um analista de sistemas especialista em bases de conhecimento de projetos B2B.

Analise os dois fragmentos de conhecimento abaixo e classifique a relação entre eles.

NODO A — "{title_a}":
{content_a}

NODO B — "{title_b}":
{content_b}

Retorne SOMENTE um objeto JSON válido:
{{
  "relation_type": "<tipo>",
  "rationale": "<justificativa em 1-2 frases>",
  "confidence": 0.0
}}

Tipos possíveis para relation_type:
- "similar_to": Ambos abordam o mesmo tipo de problema/solução, mas em contextos diferentes
- "reuses_pattern": A reutiliza explicitamente uma decisão, padrão ou abordagem de B
- "conflicts_with": As decisões ou abordagens são contraditórias ou incompatíveis
- "unrelated": Similaridade superficial, sem relação conceitual real

Se relation_type for "unrelated", não deve ser criada aresta.
"""

# ── Utilitários ───────────────────────────────────────────────────────────────

def get_wiki_nodes() -> list:
    """Busca todos os nós WIKI_PAGE"""
    try:
        r = _rs.get(f"{API_BASE}/nodes", params={"node_type": "wiki_page", "limit": 500}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao buscar WIKI_PAGEs: {e}")
        return []


def get_similar_nodes(node_id: int, top_k: int, threshold: float) -> list:
    """Busca nós semanticamente similares via /similar/{node_id}"""
    try:
        r = _rs.get(
            f"{API_BASE}/similar/{node_id}",
            params={"top_k": top_k, "min_score": threshold},
            timeout=15
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[AVISO] Falha ao buscar similares para nó {node_id}: {e}")
        return []


def get_existing_edges(node_id: int) -> set:
    """
    Retorna set de (target_id, relation_type) para arestas já existentes saindo deste nó.
    Evita duplicatas.
    """
    try:
        r = _rs.get(f"{API_BASE}/nodes/{node_id}/edges", timeout=10)
        r.raise_for_status()
        data = r.json()
        existing = set()
        for edge in data.get("outgoing", []):
            existing.add((edge["target_id"], edge["relation_type"]))
        return existing
    except Exception:
        return set()


def classify_relation(node_a: dict, node_b: dict) -> Optional[dict]:
    """
    Usa LLM para classificar a relação semântica entre dois nós.
    Retorna {"relation_type": str, "rationale": str, "confidence": float} ou None.
    """
    if not OPENAI_API_KEY:
        # Fallback sem LLM: assume SIMILAR_TO para todos acima do threshold
        return {
            "relation_type": "similar_to",
            "rationale": "Classificação automática por threshold semântico (sem LLM).",
            "confidence": 0.75
        }

    content_a = f"{node_a.get('title', '')} — {node_a.get('content', '')[:1500]}"
    content_b = f"{node_b.get('title', '')} — {node_b.get('content', '')[:1500]}"

    prompt = CLASSIFICATION_PROMPT.format(
        title_a=node_a.get("title", ""),
        content_a=content_a,
        title_b=node_b.get("title", ""),
        content_b=content_b
    )

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[AVISO] Classificação LLM falhou: {e}. Usando fallback.")
        return {
            "relation_type": "similar_to",
            "rationale": f"Fallback (LLM indisponível): {str(e)[:80]}",
            "confidence": 0.60
        }


def create_edge(source_id: int, target_id: int, relation_type: str, weight: float, rationale: str) -> bool:
    """Cria aresta entre dois nós via API"""
    try:
        r = _rs.post(
            f"{API_BASE}/edges",
            json={
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "weight": round(weight, 4),
                "metadata": {
                    "rationale": rationale,
                    "created_by": "cross_linker",
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            timeout=10
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao criar aresta {source_id} → {target_id} ({relation_type}): {e}")
        return False


# ── Lógica Principal ──────────────────────────────────────────────────────────

VALID_EDGE_TYPES = {"similar_to", "reuses_pattern", "conflicts_with"}


def process_node(node: dict, threshold: float, dry_run: bool = False) -> int:
    """
    Processa um nó WIKI_PAGE: detecta similares e cria arestas.
    Retorna número de arestas criadas.
    """
    node_id = node["id"]
    title = node.get("title", f"Node {node_id}")

    # Verificar se tem embedding
    meta = node.get("metadata") or {}
    if not meta.get("has_embedding"):
        print(f"[SKIP] Nó {node_id} ({title[:50]}): sem embedding. Execute embedding_engine.py backfill primeiro.")
        return 0

    print(f"\n[...] Cross-linking: {title[:70]}")

    similar_results = get_similar_nodes(node_id, TOP_K_CANDIDATES, threshold)
    if not similar_results:
        print(f"  [OK] Nenhum similar acima do threshold {threshold}")
        return 0

    existing_edges = get_existing_edges(node_id)
    created = 0

    for result in similar_results:
        similar_node = result.get("node") or result  # compatibilidade
        score = result.get("score", 0.0)
        similar_id = similar_node.get("id")

        if similar_id == node_id:
            continue

        print(f"  → Candidato: [{score:.3f}] {similar_node.get('title', '')[:60]}")

        # Classificar relação via LLM
        classification = classify_relation(node, similar_node)
        if not classification:
            continue

        rel_type = classification.get("relation_type", "similar_to")
        rationale = classification.get("rationale", "")
        cls_confidence = classification.get("confidence", 0.5)

        # Ignorar relações não relevantes
        if rel_type not in VALID_EDGE_TYPES:
            print(f"    [SKIP] Relação '{rel_type}' — não relevante para o grafo.")
            continue

        # Deduplicação
        if (similar_id, rel_type) in existing_edges:
            print(f"    [DUP] Aresta {rel_type} já existe → nó {similar_id}")
            continue

        print(f"    [→] {rel_type} (cosine={score:.3f}, llm_conf={cls_confidence:.2f}) — {rationale[:80]}")

        if not dry_run:
            if create_edge(node_id, similar_id, rel_type, score, rationale):
                existing_edges.add((similar_id, rel_type))
                created += 1
        else:
            print(f"    [DRY-RUN] Aresta NÃO criada (dry-run ativo)")
            created += 1  # contabiliza no dry-run também

    return created


def run_all(threshold: float, dry_run: bool = False):
    """Processa todos os WIKI_PAGEs"""
    nodes = get_wiki_nodes()
    if not nodes:
        print("[OK] Nenhum WIKI_PAGE encontrado.")
        return

    print(f"[...] {len(nodes)} WIKI_PAGE(s) para cross-linking (threshold={threshold})")
    if dry_run:
        print("[DRY-RUN] Modo simulação — nenhuma aresta será criada.")

    total_created = 0
    for node in nodes:
        total_created += process_node(node, threshold, dry_run)

    mode = "simuladas" if dry_run else "criadas"
    print(f"\n[CONCLUÍDO] {total_created} aresta(s) {mode}.")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="KARE Cross-Linker — Relações Semânticas (Fase 4)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Processar todos os WIKI_PAGEs")
    group.add_argument("--node-id", type=int, help="Processar um nó específico")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Threshold de similaridade cosine (padrão: {DEFAULT_THRESHOLD})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simular sem criar arestas")

    args = parser.parse_args()

    if args.all:
        run_all(threshold=args.threshold, dry_run=args.dry_run)
    else:
        # Buscar o nó pelo ID
        try:
            r = _rs.get(f"{API_BASE}/nodes/{args.node_id}", timeout=10)
            r.raise_for_status()
            node = r.json()
        except Exception as e:
            print(f"[ERRO] Falha ao buscar nó {args.node_id}: {e}")
            return

        created = process_node(node, threshold=args.threshold, dry_run=args.dry_run)
        mode = "simuladas" if args.dry_run else "criadas"
        print(f"\n[CONCLUÍDO] {created} aresta(s) {mode} para nó {args.node_id}.")


if __name__ == "__main__":
    main()


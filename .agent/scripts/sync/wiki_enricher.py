"""
KARE LLM Wiki Enricher — Fase 1
================================================
Após a ingestão de um nó no Context Engine, este script:
1. Lê o conteúdo bruto do nó via API
2. Chama um LLM para extrair estrutura (problema, decisão, trade-offs, etc.)
3. Cria um nó WIKI_PAGE no SQLite com o conhecimento curado
4. Cria aresta ENRICHED_BY: nó original → WIKI_PAGE
5. Se confidence_score >= 0.80, marca o nó com ready_for_confluence=true
   → O AGENTE (Copilot) lê esses nós via /wiki?ready=true e publica via MCP Atlassian


ARQUITETURA:
  Este script fala SOMENTE com o Context Engine interno (localhost:8000).
  A publicação no Confluence é responsabilidade do AGENTE via MCP Atlassian.
  Nunca usar REST direto para sistemas externos (Confluence, Jira).

Uso:
    # Enriquecer um nó específico por ID
    python wiki_enricher.py --node-id 42

    # Enriquecer todos os nós de um contexto sem WIKI_PAGE
    python wiki_enricher.py --context ini-518

    # Enriquecer todos os nós pendentes (sem WIKI_PAGE filha)
    python wiki_enricher.py --all

    # Com sync automático para Obsidian
    python wiki_enricher.py --node-id 42 --obsidian-sync

    # Listar nós prontos para o agente publicar no Confluence
    python wiki_enricher.py --list-ready

Configuração:
    CONFIDENCE_THRESHOLD = 0.80  (flag ready_for_confluence)
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
CONFIDENCE_THRESHOLD = float(os.environ.get("WIKI_CONFIDENCE_THRESHOLD", "0.80"))

# NOTA: Publicação no Confluence é feita pelo AGENTE via MCP Atlassian.
# Credenciais Confluence NÃO são necessárias neste script.

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
# ── Prompt de Extração ────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """Você é um analista de sistemas especialista em projetos B2B.

Analise o conteúdo abaixo de uma página do Confluence e extraia os campos estruturados em JSON.

CONTEÚDO:
---
{content}
---

Retorne SOMENTE um objeto JSON válido com estes campos (sem markdown, sem explicações):
{{
  "problem": "Descrição clara do problema ou necessidade de negócio abordada. 1-3 frases.",
  "decision": "Decisão técnica ou de negócio principal tomada. 1-3 frases.",
  "trade_offs": ["trade-off 1", "trade-off 2"],
  "rejected_alternatives": ["alternativa rejeitada 1", "alternativa rejeitada 2"],
  "related_inis": ["INI-XXX", "INI-YYY"],
  "key_concepts": ["conceito 1", "conceito 2"],
  "business_impact": "Impacto no negócio em 1-2 frases.",
  "technical_notes": "Notas técnicas relevantes em 1-2 frases.",
  "confidence_score": 0.0
}}

Para confidence_score:
- 0.90-1.00: Conteúdo rico, decisões claras, problema bem definido
- 0.80-0.89: Conteúdo bom, maioria dos campos preenchidos
- 0.60-0.79: Conteúdo parcial, alguns campos inferidos
- 0.40-0.59: Conteúdo raso, muito inferido
- 0.00-0.39: Conteúdo insuficiente para síntese confiável

Se um campo não puder ser preenchido com confiança, use null (não invente).
"""

# ── Funções Utilitárias ───────────────────────────────────────────────────────

def get_node(node_id: int) -> Optional[dict]:
    """Busca nó no Context Engine por ID"""
    try:
        r = _rs.get(f"{API_BASE}/nodes/{node_id}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao buscar nó {node_id}: {e}")
        return None


def get_nodes_without_wiki(context_slug: Optional[str] = None) -> list:
    """
    Retorna nós que ainda não foram enriquecidos (sem aresta ENRICHED_BY saindo deles).
    Filtra tipos ARTIFACT, DECISION, CONTEXT — candidatos ao enriquecimento.
    """
    params = {"limit": 500}
    if context_slug:
        params["context"] = context_slug

    try:
        r = _rs.get(f"{API_BASE}/nodes", params=params, timeout=15)
        r.raise_for_status()
        all_nodes = r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao listar nós: {e}")
        return []

    # Filtrar por tipo candidato
    candidates = [n for n in all_nodes if n.get("type") in ("artifact", "decision", "context")]

    # Verificar quais já têm WIKI_PAGE filha via edges
    enriched_source_ids = set()
    try:
        edges_r = _rs.get(f"{API_BASE}/edges", params={"limit": 2000}, timeout=15)
        edges_r.raise_for_status()
        edges = edges_r.json()
        enriched_source_ids = {
            e["source_id"] for e in edges if e.get("relation_type") == "enriched_by"
        }
    except Exception:
        pass  # Se não conseguir verificar, processa todos

    return [n for n in candidates if n["id"] not in enriched_source_ids]


def call_llm(content: str) -> Optional[dict]:
    """
    Chama OpenAI para extrair estrutura do conteúdo.
    Fallback: retorna estrutura mínima se OpenAI não estiver configurado.
    """
    if not OPENAI_API_KEY:
        print("[AVISO] OPENAI_API_KEY não configurada. Usando extração básica de fallback.")
        return _fallback_extraction(content)

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um analista técnico especialista em sistemas de telecomunicações B2B."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(content=content[:6000])}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except ImportError:
        print("[AVISO] Biblioteca 'openai' não instalada. Usando fallback.")
        return _fallback_extraction(content)
    except Exception as e:
        print(f"[ERRO] Chamada LLM falhou: {e}")
        return _fallback_extraction(content)


def _fallback_extraction(content: str) -> dict:
    """
    Extração básica sem LLM — usado quando OpenAI não está disponível.
    Gera estrutura mínima com confidence baixo para não publicar automaticamente.
    """
    # Tenta extrair INIs mencionados no conteúdo
    import re
    related_inis = list(set(re.findall(r"INI-\d+", content)))

    return {
        "problem": "Extração automática indisponível — configure OPENAI_API_KEY.",
        "decision": None,
        "trade_offs": [],
        "rejected_alternatives": [],
        "related_inis": related_inis[:5],
        "key_concepts": [],
        "business_impact": None,
        "technical_notes": None,
        "confidence_score": 0.35
    }


def build_wiki_content(title: str, extraction: dict) -> str:
    """Monta o conteúdo Markdown estruturado da WIKI_PAGE"""
    ini_links = ", ".join(extraction.get("related_inis") or []) or "Nenhum identificado"
    trade_offs = "\n".join(f"- {t}" for t in (extraction.get("trade_offs") or [])) or "- Não identificados"
    rejected = "\n".join(f"- {a}" for a in (extraction.get("rejected_alternatives") or [])) or "- Nenhuma registrada"
    concepts = ", ".join(extraction.get("key_concepts") or []) or "—"
    confidence = extraction.get("confidence_score", 0.0)
    now = datetime.utcnow().strftime("%B %Y")

    return f"""# {title}

> **Status:** ✅ Auto-Gerado KARE | **Data:** {now} | **Confidence:** {confidence:.0%}

---

## Problema / Contexto

{extraction.get("problem") or "_Não identificado_"}

## Decisão

{extraction.get("decision") or "_Não identificada_"}

## Trade-offs

{trade_offs}

## Alternativas Rejeitadas

{rejected}

## Impacto no Negócio

{extraction.get("business_impact") or "_Não identificado_"}

## Notas Técnicas

{extraction.get("technical_notes") or "_Sem notas_"}

## Conceitos-Chave

{concepts}

## Iniciativas Relacionadas

{ini_links}

---

> _Página gerada automaticamente pelo KARE Knowledge Engine._  
> _Fonte: Context Engine node — atualizado em {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}_
"""


def create_wiki_node(title: str, content: str, context_slug: str, extraction: dict, source_node_id: int) -> Optional[dict]:
    """Cria o nó WIKI_PAGE no Context Engine"""
    wiki_title = f"WIKI — {title}"
    payload = {
        "type": "wiki_page",
        "title": wiki_title,
        "content": content,
        "context_slug": context_slug,
        "metadata": {
            "source_node_id": source_node_id,
            "confidence_score": extraction.get("confidence_score", 0.0),
            "related_inis": extraction.get("related_inis", []),
            "problem": extraction.get("problem"),
            "decision": extraction.get("decision"),
            "trade_offs": extraction.get("trade_offs", []),
            "rejected_alternatives": extraction.get("rejected_alternatives", []),
            "key_concepts": extraction.get("key_concepts", []),
            "enriched_at": datetime.utcnow().isoformat(),
            "confluence_page_id": None  # Preenchido após publicação
        }
    }
    try:
        r = _rs.post(f"{API_BASE}/wiki", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERRO] Falha ao criar WIKI_PAGE: {e}")
        return None


def create_enriched_by_edge(source_id: int, wiki_id: int):
    """Cria aresta ENRICHED_BY: nó original → WIKI_PAGE"""
    payload = {
        "source_id": source_id,
        "target_id": wiki_id,
        "relation_type": "enriched_by",
        "weight": 1.0
    }
    try:
        r = _rs.post(f"{API_BASE}/edges", json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[AVISO] Falha ao criar aresta ENRICHED_BY: {e}")


def mark_ready_for_confluence(wiki_node_id: int, wiki_title: str, wiki_content: str):
    """
    Marca o nó WIKI_PAGE como pronto para publicação no Confluence.
    O AGENTE (Copilot) lê esses nós via GET /wiki?ready=true
    e publica via MCP Atlassian (mcp_mcp-atlassian_confluence_create_page).
    """
    try:
        r = _rs.patch(
            f"{API_BASE}/nodes/{wiki_node_id}/metadata",
            json={"ready_for_confluence": True},
            timeout=10
        )
        r.raise_for_status()
        print(f"[OK] Nó {wiki_node_id} marcado como ready_for_confluence=true")
        print(f"     Para publicar: invoque o agente KARE — ele usará MCP Atlassian.")
    except Exception as e:
        print(f"[AVISO] Falha ao marcar ready_for_confluence: {e}")


def list_ready_for_confluence() -> list:
    """Lista nós WIKI_PAGE prontos para o agente publicar via MCP."""
    try:
        r = _rs.get(f"{API_BASE}/wiki", params={"min_confidence": CONFIDENCE_THRESHOLD, "limit": 500}, timeout=15)
        r.raise_for_status()
        nodes = r.json()
        ready = [
            n for n in nodes
            if (n.get("metadata") or {}).get("ready_for_confluence") is True
            and not (n.get("metadata") or {}).get("confluence_page_id")
        ]
        return ready
    except Exception as e:
        print(f"[ERRO] {e}")
        return []


def update_node_confluence_id(wiki_node_id: int, page_id: str):
    """Atualiza o campo confluence_page_id no metadata do nó WIKI_PAGE"""
    try:
        r = _rs.patch(
            f"{API_BASE}/nodes/{wiki_node_id}/metadata",
            json={"confluence_page_id": page_id},
            timeout=10
        )
        r.raise_for_status()
    except Exception as e:
        print(f"[AVISO] Não foi possível salvar confluence_page_id no nó {wiki_node_id}: {e}")


# ── Lógica Principal ──────────────────────────────────────────────────────────

def enrich_node(node_id: int):
    """Pipeline completo de enriquecimento para um único nó"""
    print(f"\n[...] Enriquecendo nó ID={node_id}")

    node = get_node(node_id)
    if not node:
        return

    title = node.get("title", f"Node {node_id}")
    content = node.get("content", "")
    node_type = node.get("type", "")
    metadata = node.get("metadata") or {}
    context_slug = metadata.get("context_slug", "kare")

    if not content or len(content.strip()) < 100:
        print(f"[SKIP] Nó {node_id} ({title}): conteúdo muito curto para enriquecimento.")
        return

    # 1. Extrair estrutura via LLM
    print(f"[...] Extraindo estrutura via LLM: {title}")
    extraction = call_llm(content)
    if not extraction:
        print(f"[ERRO] Extração falhou para nó {node_id}.")
        return

    confidence = extraction.get("confidence_score", 0.0)
    print(f"[OK] Extração concluída — confidence: {confidence:.0%}")

    # 2. Construir conteúdo WIKI_PAGE
    wiki_title = f"WIKI — {title}"
    wiki_content = build_wiki_content(title, extraction)

    # 3. Criar nó WIKI_PAGE via /wiki endpoint
    wiki_node = create_wiki_node(title, wiki_content, context_slug, extraction, node_id)
    if not wiki_node:
        return

    wiki_node_id = wiki_node.get("id")
    print(f"[OK] WIKI_PAGE criada: ID={wiki_node_id}")

    # 4. Criar aresta ENRICHED_BY
    create_enriched_by_edge(source_id=node_id, wiki_id=wiki_node_id)
    print(f"[OK] Aresta ENRICHED_BY criada: {node_id} → {wiki_node_id}")

    # 5. Marcar pronto para publicação no Confluence (o AGENTE publica via MCP)
    if confidence >= CONFIDENCE_THRESHOLD:
        mark_ready_for_confluence(wiki_node_id, wiki_title, wiki_content)
    else:
        print(f"[SKIP] Confidence {confidence:.0%} < {CONFIDENCE_THRESHOLD:.0%} — não marcado para Confluence.")

    print(f"[CONCLUÍDO] Nó {node_id} enriquecido com sucesso.\n")


def enrich_all(context_slug: Optional[str] = None):
    """Enriquece todos os nós sem WIKI_PAGE"""
    nodes = get_nodes_without_wiki(context_slug)
    if not nodes:
        print("[OK] Nenhum nó pendente de enriquecimento.")
        return

    print(f"[...] {len(nodes)} nó(s) para enriquecer.")
    for node in nodes:
        enrich_node(node["id"])


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="KARE Wiki Enricher — LLM Wiki Pattern (Fase 1)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--node-id", type=int, help="ID do nó a enriquecer")
    group.add_argument("--context", type=str, help="Enriquecer todos os nós de um contexto (ex: ini-518)")
    group.add_argument("--all", action="store_true", help="Enriquecer todos os nós pendentes")
    group.add_argument("--list-ready", action="store_true", help="Listar nós prontos para o agente publicar no Confluence")
    parser.add_argument("--confidence-threshold", type=float, default=CONFIDENCE_THRESHOLD,
                        help=f"Threshold de confidence para publicação no Confluence (padrão: {CONFIDENCE_THRESHOLD})")

    args = parser.parse_args()

    global CONFIDENCE_THRESHOLD
    CONFIDENCE_THRESHOLD = args.confidence_threshold

    if args.node_id:
        enrich_node(args.node_id)
    elif args.context:
        enrich_all(context_slug=args.context)
    elif args.list_ready:
        ready = list_ready_for_confluence()
        if not ready:
            print("[OK] Nenhum nó pendente de publicação no Confluence.")
        else:
            print(f"\n{len(ready)} nó(s) prontos para o agente publicar via MCP Atlassian:\n")
            for n in ready:
                conf = (n.get("metadata") or {}).get("confidence_score", 0)
                print(f"  ID={n['id']} [{conf:.0%}] {n.get('title', '')}")
            print("\nInvoque o agente KARE para publicar via MCP Atlassian.")
    else:
        enrich_all()


if __name__ == "__main__":
    main()


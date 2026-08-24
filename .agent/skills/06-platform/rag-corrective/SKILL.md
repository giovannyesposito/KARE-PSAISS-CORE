---
name: rag-corrective
description: >
  CRAG (Corrective Retrieval-Augmented Generation): avalia a relevância dos
  documentos recuperados e, quando insuficientes, aciona recuperação corretiva
  antes de gerar a resposta. Elimina alucinações causadas por contexto de baixa
  qualidade. Framework: LangGraph.
sprint: 3
agente_destino: "kare_rag.py / Context Engine"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_crag.ipynb"
tools:
  - Read
  - Grep
triggers:
  - "CRAG"
  - "corrective RAG"
  - "contexto insuficiente"
  - "alucinação"
  - "recuperação corretiva"
  - "relevância de documentos"
  - "fallback de busca"
---

# RAG Corrective (CRAG) — Recuperação Corretiva Anti-Alucinação

> **Sprint 3 — QA de Agentes** | Framework: LangGraph | Agente: Context Engine

## Propósito

Implementar CRAG no RAG KARE: antes de gerar uma resposta, o agente avalia a
relevância dos documentos recuperados. Se relevância < threshold, executa
recuperação corretiva (estratégia alternativa) em vez de gerar com contexto ruim.

---

## Grafo CRAG

```
Query
  │
  ▼
[RETRIEVE]  ← Recuperação inicial (BM25 ou semântica)
  │
  ▼
[GRADE DOCUMENTS]  ← LLM avalia: docs são relevantes para a query?
  │
  ├── RELEVANT (>= 0.70)  ──────────────────────► [GENERATE]
  │
  ├── AMBIGUOUS (0.40–0.69) ──► [TRANSFORM QUERY] ──► [WEB/GRAPH SEARCH]
  │                                                         │
  │                                                         ▼
  │                                                    [GENERATE com contexto enriquecido]
  │
  └── IRRELEVANT (< 0.40) ──► [TRANSFORM QUERY] ──► [ALTERNATIVE RETRIEVAL]
                                                          │
                                                          ▼
                                                    [GENERATE com contexto alternativo]
```

---

## Avaliação de Relevância

```python
def avaliar_relevancia(query: str, docs: list[dict]) -> float:
    """Usa LLM para avaliar relevância dos docs para a query."""
    prompt = f"""
    Query: {query}

    Documentos recuperados:
    {formatar_docs(docs)}

    Os documentos acima são relevantes e suficientes para responder a query?
    Responda com um score de 0.0 a 1.0 e uma justificativa.

    Score (0.0-1.0):
    """
    resposta = llm.invoke(prompt)
    return extrair_score(resposta)

def grade_documents(state: CRAGState) -> CRAGState:
    relevancia = avaliar_relevancia(state["query"], state["docs"])
    if relevancia >= 0.70:
        classification = "relevant"
    elif relevancia >= 0.40:
        classification = "ambiguous"
    else:
        classification = "irrelevant"
    return {**state, "relevancia": relevancia, "classification": classification}
```

---

## Transformação de Query

Quando os docs não são suficientes, a query é reescrita:

```python
def transform_query(state: CRAGState) -> CRAGState:
    """Reescreve a query para recuperação alternativa."""
    nova_query = llm.invoke(f"""
    A query original "{state['query']}" não encontrou documentos relevantes.
    Reescreva-a de forma mais específica, usando:
    - Termos alternativos
    - Decomposição em sub-queries
    - Foco no aspecto mais específico
    """)
    return {**state, "query_transformada": nova_query}
```

---

## Estratégias de Recuperação Corretiva

| Classificação | Ação Corretiva | Exemplo |
|---|---|---|
| `ambiguous` | Re-busca com query transformada | Query vaga → termos específicos |
| `irrelevant` | Muda estratégia (BM25→Grafo) | Busca semântica → busca exata |
| `irrelevant` + score < 0.3 | Busca no Confluence via MCP | Cache expirado → refresh |

---

## Integração com Self Evaluation Loop (#10)

Quando o `self-evaluation-loop` detecta score < 70 em um artefato:

```python
# O CRAG é acionado como remediação
if quality_score < 70:
    contexto_enriquecido = crag.recuperar_com_correcao(
        query=f"contexto para {tipo_artefato}: {descricao}",
        agente_solicitante=agente
    )
    artefato_revisado = agente.re_gerar(contexto_enriquecido)
```

---

## Critérios de Aceite

- [ ] Docs irrelevantes (< 0.40) nunca chegam ao gerador de resposta
- [ ] Query transformada gera documentos mais relevantes em >= 80% dos casos
- [ ] Estratégia corretiva logada no RAG para aprendizado contínuo
- [ ] Alucinações reduzidas (validar com suite de 20 queries de benchmark)
- [ ] Integração com Self Evaluation Loop (#10) funcionando

---
name: context-resolver-agentic-rag
description: >
  Agentic RAG via LangGraph: o agente decide a estratégia de recuperação mais
  adequada para cada query (semântica, BM25, grafo ou híbrida) antes de gerar
  resposta. Eleva confidence_score médio para >= 0.80. Alinha ao Hybrid Query
  Planner do context-resolver.
sprint: 2
agente_destino: "kare_rag.py / Context Engine"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_agentic_rag.ipynb"
tools:
  - Read
  - Grep
triggers:
  - "agentic rag"
  - "estratégia de recuperação"
  - "hybrid query planner"
  - "confidence score"
  - "RAG adaptativo"
  - "busca inteligente"
  - "contexto de INI"
---

# Context Resolver Agentic RAG — Recuperação Adaptativa por Query

> **Sprint 2 — Desenvolvimento Core** | Framework: LangGraph | Agente: Context Engine

## Propósito

Adicionar ao RAG do KARE um agente que **decide a estratégia de recuperação** antes
de gerar a resposta — escolhendo entre BM25, semântico, grafo ou híbrido de acordo
com o tipo e complexidade da query.

---

## Estratégias de Recuperação

| Estratégia | Quando usar | Exemplo de Query |
|---|---|---|
| **BM25** | Termos exatos, códigos de iniciativa | "INI-001", "SOV-001" |
| **Semântica** | Conceitos, perguntas em linguagem natural | "Qual arquitetura foi escolhida para billing?" |
| **Grafo** | Relações entre entidades | "O que INI-002 e INI-001 têm em comum?" |
| **Híbrida** | Queries ambíguas ou complexas | "Quais são os riscos do fatiamento da INI-001?" |

---

## Grafo de Decisão

```
Query do Usuário
       │
       ▼
[CLASSIFY_QUERY]
  ├── "tem código INI?" → BM25
  ├── "pergunta conceitual?" → Semântica
  ├── "relação entre entidades?" → Grafo
  └── "complexa/ambígua?" → Híbrida
       │
       ▼
[RETRIEVE]  ← executa a estratégia escolhida
       │
       ▼
[GRADE_DOCS]  ← avalia relevância dos docs recuperados
  ├── confidence >= 0.70 → [GENERATE]
  └── confidence < 0.70 → [RE_RETRIEVE] (com estratégia alternativa)
       │
       ▼
[GENERATE]  ← gera resposta com contexto validado
```

---

## Implementação

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class RAGState(TypedDict):
    query: str
    strategy: Literal["bm25", "semantic", "graph", "hybrid"]
    docs: list[dict]
    confidence: float
    resposta: str
    re_retrieval_count: int

def classify_query(state: RAGState) -> RAGState:
    """Determina a melhor estratégia de recuperação."""
    query = state["query"]

    # Heurísticas de classificação
    if re.search(r'INI-\d+|SOV-\d+|FOG-\d+', query):
        strategy = "bm25"
    elif any(w in query.lower() for w in ["como", "por que", "qual", "o que"]):
        strategy = "semantic"
    elif any(w in query.lower() for w in ["relação", "depende", "similar", "diferença"]):
        strategy = "graph"
    else:
        strategy = "hybrid"

    return {**state, "strategy": strategy}

def retrieve(state: RAGState) -> RAGState:
    """Executa recuperação com a estratégia escolhida."""
    if state["strategy"] == "bm25":
        docs = kare_rag_bm25(state["query"])
    elif state["strategy"] == "semantic":
        docs = kare_rag_semantic(state["query"])
    elif state["strategy"] == "graph":
        docs = kare_rag_graph(state["query"])
    else:  # hybrid
        docs = kare_rag_hybrid(state["query"])
    return {**state, "docs": docs}

def grade_docs(state: RAGState) -> RAGState:
    """Avalia relevância dos documentos recuperados."""
    confidence = calcular_confidence(state["docs"], state["query"])
    return {**state, "confidence": confidence}

def deve_re_retrieve(state: RAGState) -> str:
    if state["confidence"] < 0.70 and state["re_retrieval_count"] < 2:
        return "re_retrieve"
    return "generate"
```

---

## Compatibilidade com Context Resolver (3 Cenários)

Este skill implementa o **Cenário 1** do `integrations.instructions.md` (PARTE 3 — Context Resolver):

```
CENÁRIO 1 — Verificar no RAG via Hybrid Query Planner
  GET /ask?q=<pergunta>&context=<slug>
  → Agora com estratégia adaptativa por tipo de query
  → confidence_score calculado após grading dos docs
```

---

## Critérios de Aceite

- [ ] confidence_score médio >= 0.80 após implementação
- [ ] Estratégia de recuperação logada por query no RAG
- [ ] Compatível com o protocolo de 3 Cenários do context-resolver
- [ ] Tempo de resposta <= 3s para queries sobre INI-XXX
- [ ] Re-retrieval com estratégia alternativa quando confidence < 0.70

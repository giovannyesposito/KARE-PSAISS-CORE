---
name: reflection-quality
description: >
  Agente que critica e revisa os próprios outputs antes de entregar ao humano,
  operando como QA interno para qualquer agente KARE. Reduz ciclos de revisão
  humana com artefatos pré-validados. Framework: LangGraph.
sprint: 2
agente_destino: "@story-crafter, @code-author"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/reflection/reflection.ipynb"
tools:
  - Read
  - Grep
  - Write
triggers:
  - "reflexão"
  - "auto-revisão"
  - "reflection agent"
  - "QA interno"
  - "revisar antes de entregar"
  - "pré-validação de artefato"
  - "critique loop"
---

# Reflection Quality — Auto-Revisão de Artefatos antes da Entrega

> **Sprint 2 — Desenvolvimento Core** | Framework: LangGraph | Agente: `@story-crafter`, `@code-author`

## Propósito

Implementar um ciclo de auto-crítica em qualquer agente gerador do KARE: o artefato
gerado passa por um revisor interno antes de ser entregue ao humano, reduzindo ciclos
de review manual.

---

## Ciclo de Reflexão

```
AGENTE GERADOR
     │
     │ gera artefato (v1)
     ▼
┌─────────────────────────────────────────────────────┐
│               REFLECTION LOOP                       │
│                                                     │
│  [CRITIQUE]  Analisar fraquezas, gaps, ambiguidades │
│       │                                             │
│       ▼                                             │
│  [REVISE]   Melhorar baseado na crítica             │
│       │                                             │
│       ▼                                             │
│  [VERIFY]   Score >= threshold?  ──────────► DONE  │
│       │ NÃO                                         │
│       └──────► Repetir (máx 3x → Loop Guard)       │
└─────────────────────────────────────────────────────┘
     │
     │ artefato revisado (vFinal)
     ▼
HUMANO / PRÓXIMO AGENTE
```

---

## Critérios de Crítica por Tipo

### User Story
- Story tem formato "Como... quero... para..."?
- ACs cobrem happy path E cenários de erro?
- Story é independente (INVEST-I)?
- Estimativa presente?
- Rastreabilidade com Epic/Feature?

### Código
- Tratamento de erros em todos os casos de borda?
- Nenhuma lógica de negócio em controllers?
- Testes unitários para cada AC?
- Nenhum secret hardcoded?
- Complexidade ciclomática aceitável?

### PRD
- Objetivos mensuráveis?
- Stakeholders identificados?
- Riscos mapeados com mitigação?
- Critérios de aceite do produto definidos?
- Dependências de sistemas externas declaradas?

---

## Implementação

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ReflectionState(TypedDict):
    artefato: str
    tipo: str
    critica: str
    revisoes: int
    score: int

def no_critique(state: ReflectionState) -> ReflectionState:
    prompt = f"""Analise criticamente este {state['tipo']} e liste:
    1. Pontos fracos ou inconsistências
    2. Cenários não cobertos
    3. Violações de padrão KARE
    4. Ambiguidades que causarão retrabalho

    Artefato:
    {state['artefato']}
    """
    critica = llm.invoke(prompt)
    return {**state, "critica": critica}

def no_revise(state: ReflectionState) -> ReflectionState:
    if state["revisoes"] >= 3:
        return {**state, "score": 100}  # forçar saída após 3 revisões (Loop Guard)
    artefato_melhorado = llm.invoke(
        f"Melhore este artefato aplicando as críticas:\n\nCrítica:\n{state['critica']}\n\nArtefato:\n{state['artefato']}"
    )
    score = agenteval_score(artefato_melhorado, state["tipo"])
    return {**state, "artefato": artefato_melhorado, "score": score, "revisoes": state["revisoes"] + 1}

def deve_continuar(state: ReflectionState) -> str:
    return "critique" if state["score"] < 75 else END

grafo = StateGraph(ReflectionState)
grafo.add_node("critique", no_critique)
grafo.add_node("revise", no_revise)
grafo.set_entry_point("critique")
grafo.add_edge("critique", "revise")
grafo.add_conditional_edges("revise", deve_continuar)
```

---

## Integração com Agentes KARE

O Reflection é um **wrapper** que envolve qualquer agente gerador:

```python
# Uso em @story-crafter
story_bruta = story_crafter.gerar(requisito)
story_revisada = reflection_quality.revisar(story_bruta, tipo="user_story")
# Entregar story_revisada ao humano
```

---

## Critérios de Aceite

- [ ] Artefato revisado pelo menos uma vez antes da entrega
- [ ] Critérios de reflexão configuráveis por tipo de artefato
- [ ] Histórico de revisões registrado no ORCHESTRATION_REPORT
- [ ] Convergência em <= 3 iterações (Loop Guard integrado)
- [ ] Score mínimo de 75/100 antes de entregar ao humano

---
name: orchestrator-langgraph
description: >
  Implementa times hierárquicos de agentes no @kare-orchestrator via LangGraph:
  o supervisor delega para sub-agentes especializados de forma estruturada,
  com grafo de execução auditável e suporte a times paralelos e sequenciais.
sprint: 5
agente_destino: "@kare-orchestrator"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/hierarchical_agent_teams.ipynb"
tools:
  - Read
  - Grep
  - Write
  - Edit
triggers:
  - "times hierárquicos"
  - "hierarchical agents"
  - "supervisor agent"
  - "multi-agent coordination"
  - "orquestração LangGraph"
  - "delegação estruturada"
---

# Orchestrator LangGraph — Times Hierárquicos de Agentes

> **Sprint 5 — Orchestrator Core** | Framework: LangGraph | Agente: `@kare-orchestrator`

## Propósito

Substituir a orquestração implícita do `@kare-orchestrator` por um grafo LangGraph
explícito com supervisor e sub-times — tornando cada delegação rastreável,
reversível e auditável via AgentOps (#7).

---

## Arquitetura de Times

```
                    @kare-orchestrator (Supervisor)
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         DISCOVERY      BACKLOG       QUALITY
           TIME           TIME          TIME
              │            │            │
    ┌─────────┤  ┌─────────┤  ┌─────────┤
    │         │  │         │  │         │
@product   @prd  @backlog @risk @quality @test
-discovery  -rev  -arch   -analyst -guard  -eng
```

---

## Grafo do Supervisor

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Literal

AGENTES_DISPONÍVEIS = [
    "discovery", "backlog", "quality", "development", "risk"
]

class SupervisorState(TypedDict):
    pedido: str
    agente_ativo: str
    outputs: dict
    proximo: Literal["discovery", "backlog", "quality", "development", "risk", "FINISH"]

def supervisor_decide(state: SupervisorState) -> SupervisorState:
    """Supervisor LLM decide qual agente invocar ou se encerrar."""
    proximo = llm_supervisor.invoke(f"""
    Pedido: {state['pedido']}
    Outputs já coletados: {list(state['outputs'].keys())}
    Agentes disponíveis: {AGENTES_DISPONÍVEIS}

    Qual agente deve atuar agora? Ou responder 'FINISH' se completo.
    """)
    return {**state, "proximo": proximo, "agente_ativo": proximo}

def roteador(state: SupervisorState) -> str:
    return END if state["proximo"] == "FINISH" else state["proximo"]

# Construir grafo com times
grafo = StateGraph(SupervisorState)
grafo.add_node("supervisor", supervisor_decide)

for agente in AGENTES_DISPONÍVEIS:
    grafo.add_node(agente, criar_sub_agente(agente))
    grafo.add_edge(agente, "supervisor")  # Sempre retorna ao supervisor

grafo.set_entry_point("supervisor")
grafo.add_conditional_edges("supervisor", roteador)
```

---

## Sub-Times e Responsabilidades

### Discovery Time
- `@product-discovery` — Gera Brief + PRD
- `@prd-reviewer` — Revisa PRD com critérios do projeto

### Backlog Time
- `@backlog-architect` — Prioriza e planeja sprint
- `@risk-analyst` — RAID e mitigações

### Quality Time
- `@quality-guardian` — DoR/DoD + AgentEval
- `@test-engineer` — Casos de teste BDD

---

## Rastreabilidade no ORCHESTRATION_REPORT

```markdown
## LangGraph Supervisor Trace

| Step | Agente | Input | Output | Latência |
|------|--------|-------|--------|---------|
| 1 | supervisor | pedido original | → discovery | 0.3s |
| 2 | discovery | canvas | PRD rascunho | 4.2s |
| 3 | supervisor | PRD rascunho | → quality | 0.2s |
| 4 | quality | PRD | PRD score 82/100 | 1.1s |
| 5 | supervisor | score 82 | → backlog | 0.2s |
| 6 | backlog | PRD + stories | SPRINT_1_PLAN.md | 3.8s |
| 7 | supervisor | sprint plan | FINISH | 0.1s |

**Total:** 9.9s | 3 agentes | 0 falhas
```

---

## Critérios de Aceite

- [ ] Grafo de supervisor exportável como Mermaid diagram
- [ ] Delegação registrada via AgentOps (skill #7)
- [ ] Sub-times paralelos quando não há dependência
- [ ] Loop Guard verificado em todas as delegações
- [ ] Compatível com protocolo ORCHESTRATION_REPORT existente

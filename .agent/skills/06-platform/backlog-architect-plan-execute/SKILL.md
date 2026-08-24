---
name: backlog-architect-plan-execute
description: >
  Planejamento ágil via Plan-and-Execute no LangGraph: primeiro cria um plano
  de sprint completo (tarefas, sequência, dependências), depois executa cada
  etapa monitorando progresso. Replanning automático quando bloqueios são
  detectados. Agente: @backlog-architect.
sprint: 4
agente_destino: "@backlog-architect"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/plan-and-execute/plan-and-execute.ipynb"
tools:
  - Read
  - Grep
  - Write
triggers:
  - "plan and execute"
  - "planejar sprint"
  - "replanning"
  - "planejamento adaptativo"
  - "backlog architect"
  - "sprint planning inteligente"
---

# Backlog Architect Plan-and-Execute — Sprint Planning Adaptativo

> **Sprint 4 — Agentes de Planejamento** | Framework: LangGraph | Agente: `@backlog-architect`

## Propósito

Substituir o planejamento linear por um loop plan-and-execute que permite ao
`@backlog-architect` replanificar automaticamente quando encontra bloqueios
(stories mal definidas, dependências circulares, capacidade insuficiente).

---

## Ciclo Plan-and-Execute

```
ENTRADA: Backlog + capacidade do time
       │
       ▼
[PLAN] — Criar plano de sprint completo
  ├── Sprint Goal
  ├── Stories priorizadas (MOSCOW)
  ├── Capacidade distribuída
  └── Dependências mapeadas
       │
       ▼
[EXECUTE — passo a passo]
  ├── Validar DoR de cada story
  ├── Estimar story points
  ├── Resolver dependências
  └── Atualizar Jira via MCP
       │
       ▼
[MONITOR] — Detectar bloqueios durante execução
  ├── Story sem ACs → solicitar clarificação
  ├── Capacidade estouro → remover story da sprint
  └── Dependência circular → reestruturar
       │
       ▼ bloqueio detectado
[REPLAN] — Replanejar com contexto atualizado
       │
       ▼
SPRINT PLAN FINAL (SPRINT_N_PLAN.md)
```

---

## Implementação LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class SprintPlanState(TypedDict):
    backlog: list[dict]
    capacidade: int
    plano: dict
    passo_atual: int
    bloqueios: list[str]
    sprint_plan_final: str

def no_plan(state: SprintPlanState) -> SprintPlanState:
    """Cria o plano inicial de sprint."""
    plano = llm_criar_sprint_plan(state["backlog"], state["capacidade"])
    return {**state, "plano": plano, "passo_atual": 0}

def no_execute(state: SprintPlanState) -> SprintPlanState:
    """Executa o passo atual do plano."""
    tarefa = state["plano"]["tarefas"][state["passo_atual"]]
    bloqueio = executar_tarefa(tarefa)
    if bloqueio:
        return {**state, "bloqueios": state["bloqueios"] + [bloqueio]}
    return {**state, "passo_atual": state["passo_atual"] + 1}

def no_replan(state: SprintPlanState) -> SprintPlanState:
    """Replanejar removendo bloqueios."""
    plano_atualizado = llm_replanificar(state["plano"], state["bloqueios"])
    return {**state, "plano": plano_atualizado, "bloqueios": []}

def decidir_proximo(state: SprintPlanState) -> str:
    if state["bloqueios"]:
        return "replan"
    if state["passo_atual"] >= len(state["plano"]["tarefas"]):
        return "finalizar"
    return "execute"
```

---

## Atualização Automática no Jira

```python
# Cada story do sprint plan é criada/atualizada via MCP
for story in sprint_plan["stories"]:
    mcp_jira_update_issue(
        issue_key=story["jira_key"],
        sprint_id=sprint_plan["sprint_id"],
        story_points=story["pontos"],
        assignee=story["responsavel"]
    )
```

---

## Critérios de Aceite

- [ ] Sprint Goal gerado e aprovado antes da execução do plano
- [ ] Replanning acionado automaticamente quando DoR < 80%
- [ ] SPRINT_N_PLAN.md gerado com rastreabilidade completa
- [ ] Jira atualizado via MCP (issues + sprint assignment)
- [ ] Capacidade nunca excedida (overflow removido automaticamente)

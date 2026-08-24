---
name: code-author-langgraph
description: >
  Agente de código com grafo de estados auditável via LangGraph: gerar →
  validar → corrigir → revisar. Cada transição é rastreável e compatível com
  ORCHESTRATION_REPORT.md. Suporte multi-linguagem para toda a stack do projeto.
sprint: 2
agente_destino: "@code-author"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/code_assistant/langgraph_code_assistant.ipynb"
tools:
  - Read
  - Grep
  - Write
  - Edit
  - Bash
triggers:
  - "langgraph código"
  - "grafo de estados"
  - "geração multi-linguagem"
  - "código auditável"
  - "state machine código"
  - "rastreabilidade de geração"
---

# Code Author LangGraph — Geração com Grafo de Estados Auditável

> **Sprint 2 — Desenvolvimento Core** | Framework: LangGraph | Agente: `@code-author`

## Propósito

Implementar geração de código como um grafo de estados explícito onde cada nó
é rastreável, reversível e auditável — alinhado ao ORCHESTRATION_REPORT.md.

---

## Grafo de Estados

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  GERAR   │───►│ VALIDAR  │───►│ CORRIGIR │───►│ REVISAR  │
│          │    │(lint+    │    │(máx 3x)  │    │(quality  │
│ LLM gen  │    │ tests)   │    │          │    │ score)   │
└──────────┘    └─────┬────┘    └──────────┘    └────┬─────┘
                      │ OK                            │
                      └───────────────────────────────┘
                                   DONE
```

### Nós do Grafo

| Nó | Entrada | Saída | Tool Guard |
|---|---|---|---|
| `gerar` | Requisito + linguagem + contexto | Código gerado | Read, Write |
| `validar` | Código gerado | Score lint + resultado de testes | Bash (read-only) |
| `corrigir` | Código + erros | Código corrigido | Read, Write, Edit |
| `revisar` | Código final | Score de qualidade (AgentEval) | Read |

---

## Implementação LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class CodeState(TypedDict):
    requisito: str
    linguagem: str
    codigo: str
    erros: list[str]
    score: int
    iteracoes: int
    estado: str  # "gerando" | "validando" | "corrigindo" | "revisando" | "done"

def no_gerar(state: CodeState) -> CodeState:
    codigo = llm_gerar(state["requisito"], state["linguagem"])
    return {**state, "codigo": codigo, "estado": "validando"}

def no_validar(state: CodeState) -> CodeState:
    erros = executar_lint_e_testes(state["codigo"], state["linguagem"])
    if not erros:
        return {**state, "erros": [], "estado": "revisando"}
    return {**state, "erros": erros, "estado": "corrigindo"}

def no_corrigir(state: CodeState) -> CodeState:
    if state["iteracoes"] >= 3:
        return {**state, "estado": "hitl"}  # Loop Guard
    codigo_corrigido = llm_corrigir(state["codigo"], state["erros"])
    return {**state, "codigo": codigo_corrigido, "iteracoes": state["iteracoes"] + 1, "estado": "validando"}

def no_revisar(state: CodeState) -> CodeState:
    score = agenteval_score(state["codigo"], "codigo")
    return {**state, "score": score, "estado": "done"}

# Construir o grafo
grafo = StateGraph(CodeState)
grafo.add_node("gerar", no_gerar)
grafo.add_node("validar", no_validar)
grafo.add_node("corrigir", no_corrigir)
grafo.add_node("revisar", no_revisar)

grafo.set_entry_point("gerar")
grafo.add_conditional_edges("validar", lambda s: s["estado"], {
    "corrigindo": "corrigir",
    "revisando": "revisar",
})
grafo.add_edge("corrigir", "validar")
grafo.add_edge("revisar", END)
```

---

## Rastreabilidade no ORCHESTRATION_REPORT

Cada transição de estado é logada:

```markdown
## Code Author LangGraph — Trace de Estados

| Step | Estado | Duração | Resultado |
|------|--------|---------|-----------|
| 1 | gerar | 2.3s | 45 linhas TypeScript geradas |
| 2 | validar | 1.1s | ❌ 2 erros de lint (null check) |
| 3 | corrigir (it.1) | 1.8s | Null checks adicionados |
| 4 | validar | 0.9s | ✅ Lint OK, testes passando |
| 5 | revisar | 0.8s | Score 84/100 — APROVADO |

**Total:** 6.9s | 1 iteração de correção | Score final: 84/100
```

---

## Critérios de Aceite

- [ ] Grafo de estados exportável e legível por humanos (Mermaid)
- [ ] Cada nó do grafo registrado no ORCHESTRATION_REPORT
- [ ] Suporte confirmado para >= 3 linguagens do projeto
- [ ] Transições de estado auditáveis via AgentOps (#7)
- [ ] Máximo 3 iterações de correção (Loop Guard integrado)

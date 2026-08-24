---
name: agent-simulation-testing
description: >
  Simula usuários reais interagindo com agentes KARE para testar robustez,
  cobertura de edge cases e comportamento antes do deploy em produção.
  Equivalente a CI/CD E2E para o ecossistema de agentes. Framework: LangGraph.
sprint: 3
agente_destino: "Pipeline de validação de novos agentes"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/chatbot-simulation-evaluation/agent-simulation-evaluation.ipynb"
tools:
  - Read
  - Grep
  - Write
triggers:
  - "simulação de agente"
  - "testar agente"
  - "edge cases"
  - "validar antes do deploy"
  - "chatbot simulation"
  - "suite de testes de agente"
  - "CI/CD de agentes"
---

# Agent Simulation Testing — Pipeline de Validação de Agentes KARE

> **Sprint 3 — QA de Agentes** | Framework: LangGraph | Deploy gate obrigatório

## Propósito

Validar novos agentes KARE com simulações realistas de usuários antes que sejam
ativados em produção. Nenhum agente é ativado sem passar nesta suite com >= 80%.

---

## Cenários de Simulação por Agente

### @story-crafter — Suite Mínima

| Cenário | Entrada Simulada | Saída Esperada |
|---|---|---|
| Happy path | "Crie story para login OAuth B2B" | Story com ACs em Gherkin, DoR >= 80% |
| Requisito vago | "Melhore o sistema" | Perguntas de clarificação (não gera direto) |
| Requisito muito grande | Epic completo em linguagem natural | Sugestão de divisão em múltiplas stories |
| Conflito de requisitos | ACs contraditórios | Identificação explícita do conflito |
| Idioma misto | Mistura PT/EN | Story normalizada em PT-BR |

### @code-author — Suite Mínima

| Cenário | Entrada Simulada | Saída Esperada |
|---|---|---|
| TDD TypeScript | Story com ACs | Testes primeiro, código depois |
| Código inseguro | Requisito com SQL concatenado | Parameterized queries geradas |
| Loop de debug | Erro de compilação irresolvível | HITL após 3 tentativas |
| Multi-linguagem | "Implemente em Python e Java" | Ambas as versões geradas |

---

## Arquitetura do Simulador

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class SimulationState(TypedDict):
    agente: str
    cenario: str
    entrada: str
    saida_real: str
    saida_esperada: str
    passou: bool
    score: float

def simular_usuario(state: SimulationState) -> SimulationState:
    """Gera input de usuário simulado para o cenário."""
    prompt_usuario = gerar_prompt_usuario(state["cenario"])
    return {**state, "entrada": prompt_usuario}

def executar_agente(state: SimulationState) -> SimulationState:
    """Executa o agente alvo com o input simulado."""
    saida = invocar_agente(state["agente"], state["entrada"])
    return {**state, "saida_real": saida}

def avaliar_saida(state: SimulationState) -> SimulationState:
    """Avalia se a saída atende ao comportamento esperado."""
    score = llm_avaliar_conformidade(state["saida_real"], state["saida_esperada"])
    passou = score >= 0.80
    return {**state, "score": score, "passou": passou}
```

---

## Relatório de Cobertura

```markdown
## Simulation Report — @story-crafter v2.1.0

| Cenário | Status | Score | Observação |
|---------|--------|-------|------------|
| Happy path | ✅ PASS | 0.94 | — |
| Requisito vago | ✅ PASS | 0.87 | Fez 3 perguntas corretas |
| Requisito grande | ✅ PASS | 0.82 | Sugeriu 3 stories |
| Conflito AC | ❌ FAIL | 0.61 | Não detectou o conflito |
| Idioma misto | ✅ PASS | 0.91 | Normalizou corretamente |

**Cobertura:** 4/5 cenários (80%) — LIMIAR ATINGIDO para deploy
**Cenário reprovado:** Conflito de ACs → Issue criada no Jira via MCP
```

---

## Gate de Deploy

```python
THRESHOLD_DEPLOY = 0.80

def aprovar_deploy(relatorio: dict) -> bool:
    taxa_aprovacao = sum(c["passou"] for c in relatorio["cenarios"]) / len(relatorio["cenarios"])
    if taxa_aprovacao < THRESHOLD_DEPLOY:
        # Criar issue no Jira com falhas
        criar_issue_jira_mcp(relatorio)
        return False
    return True
```

---

## Critérios de Aceite

- [ ] Suite de cenários de simulação por agente (mínimo 5 cenários)
- [ ] Relatório de cobertura comportamental gerado automaticamente
- [ ] Falhas documentadas como issues no Jira via MCP
- [ ] Gate de deploy: aprovação exige >= 80% de cenários passando
- [ ] Integração com pipeline CI/CD do repositório KARE

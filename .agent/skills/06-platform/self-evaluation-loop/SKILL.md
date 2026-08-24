---
name: self-evaluation-loop
description: >
  Loop de auto-avaliação contínua que compara outputs de agentes com critérios
  de qualidade KARE (INVEST, DoR, DoD, padrões do projeto). Gera score 0-100 e
  aciona Corrective RAG quando lacunas de contexto são detectadas como causa
  de baixa qualidade. Framework: CrewAI.
sprint: 3
agente_destino: "@quality-guardian"
framework: CrewAI
referencia: "https://github.com/crewAIInc/crewAI/blob/main/docs/concepts/crews.mdx"
tools:
  - Read
  - Grep
  - Write
triggers:
  - "auto-avaliação"
  - "self-evaluation"
  - "quality score"
  - "INVEST check"
  - "DoR validação"
  - "qualidade contínua"
  - "feedback loop"
---

# Self Evaluation Loop — Qualidade Contínua via CrewAI

> **Sprint 3 — QA de Agentes** | Framework: CrewAI | Agente: `@quality-guardian`

## Propósito

Implementar um crew de avaliação que analisa outputs de qualquer agente KARE
contra critérios configuráveis (INVEST, DoR, DoD, padrões do projeto) e aciona
remediações automáticas quando o score cai abaixo do threshold.

---

## Crew de Avaliação

```python
from crewai import Agent, Task, Crew

# Agente 1: Avaliador INVEST
avaliador_invest = Agent(
    role="Avaliador INVEST",
    goal="Verificar se cada User Story atende os critérios INVEST",
    backstory="Especialista em qualidade de backlog e refinamento ágil",
    verbose=True,
)

# Agente 2: Avaliador Técnico
avaliador_tecnico = Agent(
    role="Avaliador Técnico",
    goal="Verificar se código e arquitetura seguem os padrões do projeto (SOLID, testes, segurança)",
    backstory="Tech Lead sênior com expertise em systems design",
    verbose=True,
)

# Agente 3: Score Aggregator
score_aggregator = Agent(
    role="Score Aggregator",
    goal="Consolidar avaliações e recomendar ações corretivas",
    backstory="QA Manager focado em melhoria contínua",
    verbose=True,
)
```

---

## Critérios de Avaliação KARE

### User Story (peso 100)

| Critério | Peso | Checklist |
|---|---|---|
| **I**ndependente | 20 | Pode ser implementada sem outra story? |
| **N**egociável | 10 | Aberta a soluções alternativas? |
| **V**aliosa | 20 | Valor claro para usuário/negócio? |
| **E**stimável | 15 | Pode ser estimada em story points? |
| **S**mall (pequena) | 20 | Cabe em 1 sprint? |
| **T**estável | 15 | ACs verificáveis por automação? |

### Código (peso 100)

| Critério | Peso | Checklist |
|---|---|---|
| Cobertura de testes | 30 | >= 80% de coverage? |
| Segurança OWASP | 25 | Nenhuma vulnerabilidade Top 10? |
| SOLID | 20 | Princípios aplicados? |
| Documentação | 15 | Docstrings e README atualizados? |
| Performance | 10 | Sem N+1 queries, loops desnecessários? |

---

## Fluxo de Remediação

```
Score < 70 → Acionar Corrective RAG (#13)
             ↓
        Identificar contexto faltando
             ↓
        Re-recuperar contexto correto
             ↓
        Re-gerar artefato
             ↓
        Re-avaliar (máx 2 ciclos extras)
```

---

## Integração com ORCHESTRATION_REPORT

```markdown
## Quality Guardian — Self Evaluation Results

| Artefato | Tipo | Score | Status | Ação |
|---------|------|-------|--------|------|
| US-042 Login OAuth | User Story | 87/100 | ✅ PASS | — |
| auth.service.ts | Código | 62/100 | ❌ FAIL | Corrective RAG acionado |
| PRD INI-001 v2 | PRD | 75/100 | ⚠️ WARNING | Revisar seção de riscos |

**Limiar de aprovação:** 70/100  
**Ações corretivas iniciadas:** 1
```

---

## Critérios de Aceite

- [ ] Score calculado para user stories (INVEST) e código (SOLID+testes+segurança)
- [ ] Corrective RAG acionado automaticamente quando score < 70
- [ ] Histórico de scores por artefato persistido no RAG
- [ ] Relatório integrado ao ORCHESTRATION_REPORT.md
- [ ] Critérios configuráveis por projeto sem modificar código base

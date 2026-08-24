---
description: "Orquestra múltiplos agentes KARE para tarefas complexas multi-domínio que requerem expertise simultânea"
command: /orchestrate
category: Orchestration
orchestrator: kare-orchestrator
orchestrator-mode: conditional
agents-required:
   - primary: "@kare-orchestrator"
      secondary: ["@product-discovery", "@story-crafter", "@backlog-architect", "@test-engineer", "@review-master", "@quality-guardian", "@risk-analyst", "@tech-decision-maker", "@delivery-observer"]
context-required:
   - PROJECT_CONTEXT.md
---

# /orchestrate Workflow

## O que faz
Meta-workflow que coordena múltiplos agentes KARE em paralelo ou sequência
para tarefas complexas que cruzam múltiplos domínios.

## Passos

1. Analisar o escopo da tarefa e identificar todos os domínios envolvidos

2. Mapear domínio ? agente:
   - Discovery/PRD ? `@product-discovery` + `@prd-reviewer`
   - Stories/Backlog ? `@story-crafter` + `@backlog-architect`
   - Código ? `@code-author`
   - Testes ? `@test-engineer`
   - Review ? `@review-master` + `@quality-guardian`
   - Riscos ? `@risk-analyst`
   - Decisões ? `@tech-decision-maker`
   - Métricas ? `@delivery-observer`

3. Construir DAG de dependências entre agentes:
   - Identificar o que pode rodar em paralelo
   - Identificar o que precisa de output de outro agente

4. Disparar agentes independentes em paralelo (fan-out)

5. Coletar outputs e detectar conflitos (fan-in)

6. Resolver conflitos e gerar `ORCHESTRATION_REPORT.md`

## Uso

```
/orchestrate [descrição da tarefa complexa]
/orchestrate --scope epic EP-05
/orchestrate --agents classifier,discovery,crafter,risk
/orchestrate --mode parallel | sequential | auto
```

## Exemplos de Uso

```
/orchestrate gere story, testes, risk register e ADR para a feature de autenticação OAuth
/orchestrate faça o planejamento completo do sprint 15 incluindo riscos e DoR
/orchestrate revise essa feature: review de código + risk + quality gate
```

## Saídas Esperadas

- Outputs individuais de cada agente ativado (em suas respectivas pastas)
- `ORCHESTRATION_REPORT.md` com:
  - Agentes ativados e seus outputs
  - Conflitos detectados e resoluções
  - Próximas ações recomendadas

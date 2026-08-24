---
description: "Gera plano de sprint, sprint goal e organiza backlog para o próximo ciclo"
command: /sprint
category: Planning
orchestrator: kare-orchestrator
orchestrator-mode: parallel
agents-required:
   - primary: "@backlog-architect"
      secondary: ["@quality-guardian", "@risk-analyst"]
context-required:
   - PROJECT_CONTEXT.md
   - BACKLOG.md
disclaimer: "?? Planeja sprint completa com priorização e validação de DoR. Requer backlog existente e capacidade do time. Tempo: 5-8 min. Saídas: SPRINT_N_PLAN.md, Sprint Goal"
---

# /sprint Workflow

## O que faz
Planeja o próximo sprint: prioriza backlog, monta sprint goal, valida DoR
das stories e distribui capacidade do time.

## Passos

// turbo
1. Ler `BACKLOG.md` atual e `PROJECT_CONTEXT.md`

2. Invocar `@backlog-architect` para priorização da sprint:
   - Input: capacidade do time (em pontos ou dias)
   - Output: sprint backlog candidato + Sprint Goal Canvas

3. Disparar em paralelo (fan-out), após concluir o passo 2:
   - `@quality-guardian` para validar DoR de cada story candidata
   - `@risk-analyst` para riscos do sprint
   - Output: lista de stories ready vs not-ready + seção de riscos

4. Gerar `SPRINT_PLAN.md` consolidado (fan-in)

5. Atualizar `BACKLOG.md` com status corrente

## Uso

```
/sprint --capacity [pontos ou dias]
/sprint --team-size N
/sprint --goal "[texto do objetivo]"
/sprint --velocity [pontos por sprint]
```

## Saídas Esperadas

- `demandas_processadas/<context_slug>/sprints/SPRINT_N_PLAN.md` com:
  - Sprint Goal
  - Stories comprometidas (somente DoR=?)
  - Capacidade vs comprometimento
  - Riscos do sprint
  - Critério de sucesso do sprint
- `demandas_processadas/<context_slug>/upstream/BACKLOG.md` atualizado com status

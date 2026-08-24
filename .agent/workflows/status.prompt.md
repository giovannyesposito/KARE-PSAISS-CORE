---
description: "Mostra status do projeto: backlog, DORA metrics, riscos ativos e saúde geral da entrega"
---

# /status Workflow

## O que faz
Snapshot consolidado da saúde do projeto: backlog (throughput, WIP, bloqueios),
DORA metrics, riscos ativos e próximas ações recomendadas.

## Passos

// turbo
1. Ler todos os artefatos relevantes:
   - `PROJECT_CONTEXT.md`, `demandas_processadas/<context_slug>/upstream/BACKLOG.md`, `demandas_processadas/<context_slug>/upstream/RAID.md`
   - Sprints em `demandas_processadas/<context_slug>/sprints/`, releases em `demandas_processadas/<context_slug>/releases/`

// turbo
2. Invocar `@delivery-observer` para métricas de entrega:
   - DORA Metrics (deploy freq, lead time, MTTR, CFR)
   - Flow Metrics (throughput, cycle time, WIP)

3. Invocar `@risk-analyst` para riscos ativos com score HIGH+:
   - Output: top-5 riscos críticos com ação recomendada

4. Invocar `@backlog-architect` para snapshot do backlog:
   - Stories por status (todo/in-progress/done/blocked)
   - Capacidade restante no sprint atual

5. Consolidar e renderizar `STATUS_REPORT.md`

## Uso

```
/status
/status --sprint N
/status --release v2.1.0
/status --verbose
```

## Saídas Esperadas

```
## ?? KARE Project Status — 2025-XX-XX

### Backlog
- Total: N stories | Ready: N | In Progress: N | Done: N | Blocked: N

### Sprint Atual
- Goal: [...]
- Burndown: N/N pontos completados
- Riscos ativos: N (HIGH: N)

### DORA Metrics (últimos 30d)
- Deploy Frequency: X/semana (?? Medium)
- Lead Time: Xh (?? High)
- MTTR: Xh (?? Elite)
- CFR: X% (?? Medium)

### Top Riscos
1. [R-5] Dependência do serviço X ? Impacto: ALTO
```

- `STATUS_REPORT.md` gerado

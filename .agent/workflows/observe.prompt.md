---
description: "Gera SLOs, runbooks e relatórios de observabilidade. Monitora saúde de serviços e métricas de entrega."
---

# /observe Workflow

## O que faz
Configura e monitora observabilidade: define SLOs, gera runbooks, calcula
DORA metrics e emite relatórios de saúde de serviços e entrega.

## Passos

// turbo
1. Ler serviços e arquitetura do projeto (de ADRs e `PROJECT_CONTEXT.md`)

2. Invocar `@delivery-observer` para o escopo dado:
   - Se `--slo`: gerar SLO.md por serviço
   - Se `--runbook`: gerar RUNBOOK.md por cenário de incidente
   - Se `--dora`: calcular e reportar DORA metrics
   - Se `--dashboard`: gerar spec de dashboard (Grafana/Datadog)

3. Invocar `@risk-analyst` para riscos de observabilidade:
   - Serviços sem SLO definido = risco
   - Ausência de alertas P1/P2 = risco

4. Consolidar em `OBSERVABILITY_REPORT.md`

## Uso

```
/observe --slo [serviço]
/observe --runbook [serviço ou cenário]
/observe --dora [últimos 30 dias]
/observe --dashboard [serviço]
/observe --all
```

## Saídas Esperadas

- `demandas_processadas/<context_slug>/observabilidade/SLO_[servico].md`
- `demandas_processadas/<context_slug>/observabilidade/RUNBOOK_[cenario].md`
- `demandas_processadas/<context_slug>/observabilidade/DORA_REPORT.md`
- `demandas_processadas/<context_slug>/observabilidade/DASHBOARD_SPEC.md` (Grafana-as-code ou Datadog spec)
- `demandas_processadas/<context_slug>/observabilidade/OBSERVABILITY_REPORT.md` consolidado

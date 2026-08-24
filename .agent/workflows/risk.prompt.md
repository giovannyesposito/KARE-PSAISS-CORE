---
description: "Identifica e registra riscos para um escopo (story, sprint, release, feature). Gera RAID Log e planos de mitigação."
command: /risk
category: Risk
disclaimer: "⚠️ Monta análise de risco COMPLETA (RAID). Matriz impacto × probabilidade. Planos de mitigação recomendados. Tempo: 3-5 min. Saídas: RAID.md, Matriz, Planos"
---

# /risk Workflow

## O que faz
Análise completa de riscos para o escopo dado. Gera RAID Log, Risk Register
atualizado e Risk-Adjusted Backlog com priorização por risco.

## Passos

// turbo
1. Ler `RAID.md` existente (se houver) para contexto histórico

// turbo
2. Ler artefatos do escopo: story/sprint/PRD/release alvo

3. Invocar `@risk-analyst` para análise completa:
   - Identificar Risks, Assumptions, Issues, Dependencies
   - Qualificar por probabilidade × impacto
   - Propor estratégia de resposta para cada risco

4. Atualizar `RAID.md` com novos itens

5. Invocar `@backlog-architect` para Risk-Adjusted Backlog:
   - Reordenar stories considerando risco dos itens

6. Se riscos CRITICAL detectados: alert imediato com plano de mitigação

## Uso

```
/risk --story US-42
/risk --sprint N
/risk --release v2.1.0
/risk --all [scopo amplo]
/risk --update [adicionar novo risco ao RAID]
```

## Saídas Esperadas

- `demandas_processadas/<context_slug>/upstream/RAID.md` atualizado
- `demandas_processadas/<context_slug>/upstream/RISK_REGISTER.md` atualizado
- Risk-Adjusted Backlog
- Alertas de riscos CRITICAL com plano de ação imediata

---
name: backlog-management
description: >
  Gestão e manutenção do Product Backlog. Priorização com frameworks (WSJF,
  MoSCoW, RICE), refinamento de stories, épicos e features, sprint planning
  e gestão de dívida técnica no backlog. Gera BACKLOG.md versionado.
triggers:
  - "backlog"
  - "priorização"
  - "refinamento"
  - "sprint planning"
  - "WSJF"
  - "MoSCoW"
  - "RICE"
  - "/refine"
  - "/sprint-plan"
---

# Backlog Management Skill

## Protocolo de Priorização

### WSJF — Weighted Shortest Job First (SAFe)

```
WSJF = (Valor de Negócio + Criticidade Temporal + Redução de Risco/Oportunidade)
       ─────────────────────────────────────────────────────────────────────────
                              Tamanho do Job (Esforço)

Escala: 1, 2, 3, 5, 8, 13, 20 (Fibonacci)
```

| Item | Valor | Criticidade | Risco/Oportunidade | Esforço | WSJF |
|------|-------|-------------|-------------------|---------|------|
| | | | | | |

### MoSCoW

| Nível | Critério |
|-------|---------|
| **Must** | Sem isso o produto não funciona / compliance |
| **Should** | Alto valor, sem bloqueante se não entrar |
| **Could** | Nice-to-have, entra se sobrar capacidade |
| **Won't** | Explicitamente fora deste ciclo |

### RICE

```
Score = (Reach × Impact × Confidence) / Effort

Reach: usuários por período
Impact: 0.25/0.5/1/2/3
Confidence: % certainty
Effort: pessoa-semanas
```

---

## Estrutura Obrigatória do Backlog KARE

> **REGRA:** Todo `BACKLOG.md` gerado por esta skill DEVE seguir a hierarquia de 3 níveis: Épicos → Features → Stories/Enablers. A estrutura MoSCoW é complementar (usada na priorização), mas não substitui a hierarquia.

```markdown
# BACKLOG — [INI-XXX - Nome da Iniciativa]
<!-- Gerado por KARE | DRAFT v1 -->
Status: ⏳ PENDENTE APROVAÇÃO

## Épicos
| ID | Épico | Prioridade | Sprints |
|----|-------|-----------|---------|
| EP-01 | ... | P1 | 1-2 |

## Features por Épico

### EP-01 — [Nome do Épico]
| ID | Feature | Stories | Sprint | Prioridade |
|----|---------|---------|--------|-----------|
| FT-01 | ... | US-01, US-02 | 1 | P1 |

## Sprint 0 — Enablers
| ID | Enabler | Feature/Épico Habilitado | Critérios Resumidos |
|----|---------|------------------------|---------------------|
| EN-01 | ... | FT-01 | ... |

## Stories por Feature

### FT-01 — [Nome da Feature]
*Épico pai: EP-01 | Sprint X*
| ID | Story | SP | Prioridade |
|----|-------|----|-----------|
| US-01 | Como [persona], quero [ação], para [valor] | 5 | P1 |

## Resumo por Sprint
| Sprint | Features | SP |
|--------|----------|----|
```


| ID | Story | WSJF | | |

## 🟢 Could (Backlog)
| ID | Story | WSJF | | |

## ⚫ Won't (Descartado ou congelado)
| ID | Story | Motivo |

## 🔧 Dívida Técnica
| ID | Item | Impacto | Custo de Atraso |
|----|------|---------|----------------|
| TECH-001 | | | |

## Métricas do Backlog
- **Velocity média**: [pontos/sprint]
- **Total de items**: [n]
- **Dívida técnica %**: [%]
- **Age médio (backlog antigo)**: [dias]
```

---

## Refinamento de Stories

Checklist automático aplicado em cada story do backlog:

```
✅ Tem "Como / Quero / Para que"?
✅ ACs definidos e testáveis?
✅ Unhappy path coberto?
✅ INVEST passando?
✅ Sem dependências não resolvidas?
✅ Estimada em pontos ou T-shirt size?
✅ DoR atendida?
```

Resultado por story: `PRONTO` | `PRECISA_REFINAR: [motivo]` | `BLOQUEAR: [motivo]`

---

## Sprint Planning

### Input necessário
- Backlog priorizado (BACKLOG.md)
- Velocity histórica do time
- Capacidade do sprint (pessoas × dias × % focus)
- Stories com DoR = PRONTO

### Saída — SPRINT_PLAN.md

```markdown
# Sprint [N] — Plan

**Período**: [data início] → [data fim]
**Objetivo do Sprint**: [sprint goal — 1 frase]
**Capacidade**: [total story points disponíveis]

## Itens Comprometidos
| Story | Points | Responsável |
|-------|--------|-------------|

## Capacidade vs Carga
- Capacidade: [X pts]
- Carga comprometida: [Y pts]
- Buffer técnico: [Z pts]

## Itens em Stand-by (se sobrar capacidade)
| Story | Points |

## Riscos do Sprint
- [Dependências externas, férias, tech risks]
```

---

## Gestão de Dívida Técnica

Regra de equilíbrio recomendada: **20% da capacidade do sprint para dívida técnica**.

Categorias:
- `DEBT-CODE` — code smell, duplicação, complexidade ciclomática
- `DEBT-ARCH` — coupling alto, violação de SOLID, layering quebrado
- `DEBT-TEST` — gaps de cobertura, testes frágeis
- `DEBT-OPS` — observability, runbooks ausentes
- `DEBT-DOCS` — documentação desatualizada

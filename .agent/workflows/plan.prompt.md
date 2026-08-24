---
description: "Cria o plano técnico (plan.md) a partir da spec aprovada — segunda etapa do fluxo SDD Downstream. Não escreve código."
command: /plan
category: Development
disclaimer: "🚫 IMPORTANTE: Este comando APENAS planeja — NÃO escreve código. Requer SPEC-<slug>.md existente (rode /speckit-specify antes). Tempo: 5-10 min. Saída: _outputs/<slug>/outputs_downstream/plans/PLAN-<slug>.md"
---

# /plan — Etapa Plan (SDD Downstream)

$ARGUMENTS

---

## 🔴 Regras Críticas

1. **SEM CÓDIGO** — este comando gera apenas o plano técnico
2. **Use o agente `@spec-writer`** (Etapa 2 — Plan)
3. **Requer spec aprovada** — se `SPEC-<slug>.md` não existir, rode `/speckit-specify` primeiro
4. **Aprovação prévia** — apresentar a estrutura do plano antes de gerar o arquivo

---

## Passos

1. Ler `SPEC-<slug>.md` em `_outputs/<slug>/outputs_downstream/specs/`
2. Buscar ADRs e decisões técnicas anteriores relevantes no RAG
3. Invocar `@spec-writer` (Etapa 2 — Plan) com a spec como entrada
4. Se surgir decisão técnica relevante: invocar `@tech-decision-maker` para novo ADR
5. **[APROVAÇÃO PRÉVIA]** Apresentar arquitetura/decisões propostas → aguardar "de acordo"
6. Gerar `PLAN-<slug>.md` em `_outputs/<slug>/outputs_downstream/plans/`

---

## Saída Esperada

| Deliverable | Location |
|---|---|
| Plano técnico | `_outputs/<slug>/outputs_downstream/plans/PLAN-<slug>.md` |
| ADR novo (se aplicável) | `_outputs/<slug>/outputs_upstream/ADR-XXX.md` |

---

## Uso

```
/plan --slug checkout-pix
```

## Próximo passo

Após aprovação do plano, rode `/speckit-tasks --slug <slug>` para decompor em tarefas.

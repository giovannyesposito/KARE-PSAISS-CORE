---
description: "Decompõe spec.md + plan.md em tasks.md — terceira etapa do fluxo SDD Downstream, última antes de codificar"
command: /speckit-tasks
category: Development
disclaimer: "🧩 DISCLAIMER: Este comando NÃO escreve código — apenas decompõe a spec/plano aprovados em tarefas pequenas e verificáveis. Use @spec-writer. Requer SPEC-<slug>.md e PLAN-<slug>.md existentes. Tempo: 5-10 min. Saída: _outputs/<slug>/outputs_downstream/tasks/TASKS-<slug>.md"
---

# /speckit-tasks — Etapa Tasks (SDD Downstream)

$ARGUMENTS

---

## O que faz

Terceira etapa do fluxo SDD Downstream. Lê a spec e o plano já aprovados e
decompõe o trabalho em tarefas pequenas, ordenadas e verificáveis — a lista
que `/implement` vai executar.

## Passos

1. Ler `SPEC-<slug>.md` e `PLAN-<slug>.md` em `_outputs/<slug>/outputs_downstream/`
2. Verificar se há ADRs relevantes gerados na etapa de Plan
3. Invocar `@spec-writer` (Etapa 3 — Tasks)
4. **[APROVAÇÃO PRÉVIA]** Apresentar a lista de tasks proposta → aguardar "de acordo"
5. Gerar `TASKS-<slug>.md` em `_outputs/<slug>/outputs_downstream/tasks/`

## Uso

```
/speckit-tasks --slug checkout-pix
```

## Saída Esperada

| Deliverable | Location |
|---|---|
| Lista de tarefas rastreáveis | `_outputs/<slug>/outputs_downstream/tasks/TASKS-<slug>.md` |

## Próximo passo

Rode `/implement --tasks TASKS-<slug>.md` (ou `--story US-XX`) para codificar.

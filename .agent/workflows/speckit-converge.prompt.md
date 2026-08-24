---
description: "Valida a implementação contra a spec original e fecha o ciclo SDD Downstream — última etapa, após /implement"
command: /speckit-converge
category: Development
disclaimer: "✅ DISCLAIMER: Este comando NÃO escreve código novo — valida se o que foi implementado atende à SPEC-<slug>.md original e registra divergências. Requer /implement já executado. Tempo: 5-10 min. Saída: _outputs/<slug>/outputs_downstream/convergence/CONVERGE-<slug>.md"
---

# /speckit-converge — Etapa Converge (SDD Downstream)

$ARGUMENTS

---

## O que faz

Última etapa do fluxo SDD Downstream. Fecha o ciclo `Specify → Plan → Tasks → Implement → Converge`
comparando a implementação entregue contra a especificação original, registrando
qualquer divergência intencional ou pendência.

## Passos

1. Ler `SPEC-<slug>.md`, `PLAN-<slug>.md` e `TASKS-<slug>.md`
2. Ler o gate report do `@quality-guardian` gerado em `/implement`
3. Invocar `@quality-guardian` para o checklist de convergência:
   - Todo requisito da spec tem task correspondente concluída?
   - Todo AC tem teste passando?
   - Alguma decisão tomada durante `/implement` não está documentada em ADR?
4. Se houver divergência não intencional: reportar como BLOCKER, não fechar o ciclo
5. Se houver divergência intencional (ex: escopo reduzido combinado com o usuário): registrar como "Divergência Aceita" com justificativa
6. Gerar `CONVERGE-<slug>.md` em `_outputs/<slug>/outputs_downstream/convergence/`
7. Ingerir o resultado no RAG: `kare_rag.py history ingest --type artifact --title "CONVERGE-<slug>"`

## Uso

```
/speckit-converge --slug checkout-pix
```

## Saída Esperada

| Deliverable | Location |
|---|---|
| Relatório de convergência | `_outputs/<slug>/outputs_downstream/convergence/CONVERGE-<slug>.md` |
| Status | ✅ CONVERGIU / ⚠️ DIVERGÊNCIA ACEITA / ❌ BLOCKER |

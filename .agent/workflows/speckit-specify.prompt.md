---
description: "Formaliza uma User Story/PRD em especificação técnica (spec.md) — primeira etapa do fluxo SDD Downstream, antes de qualquer plano ou código"
command: /speckit-specify
category: Development
disclaimer: "📐 DISCLAIMER: Este comando NÃO escreve plano técnico nem código — apenas formaliza requisitos, ACs, fora-de-escopo e contratos. Use @spec-writer. Tempo: 5-10 min. Saída: _outputs/<slug>/outputs_downstream/specs/SPEC-<slug>.md"
---

# /speckit-specify — Etapa Specify (SDD Downstream)

$ARGUMENTS

---

## O que faz

Primeira etapa do fluxo SDD Downstream (`Specify → Plan → Tasks → Implement → Converge`).
Traduz uma User Story ou trecho de PRD/Backlog aprovado no Upstream em uma
especificação técnica formal, sem tomar nenhuma decisão de arquitetura ainda
(isso é papel do `/plan`) e sem escrever código.

## Passos

1. Ler a User Story alvo (ou descrição técnica) com todos os ACs — de
   `_outputs/<slug>/outputs_upstream/` ou input direto do usuário
2. Buscar decisões e specs anteriores no RAG: `kare_rag.py history search "<contexto>" --type artifact`
3. Invocar `@spec-writer` (Etapa 1 — Specify) com o contexto coletado
4. **[APROVAÇÃO PRÉVIA]** Apresentar a estrutura da spec proposta → aguardar "de acordo"
5. Gerar `SPEC-<slug>.md` em `_outputs/<slug>/outputs_downstream/specs/`
6. Ingerir a spec no RAG: `kare_rag.py history ingest --type artifact --title "SPEC-<slug>"`

## Uso

```
/speckit-specify --story US-42
/speckit-specify --story US-42 --slug checkout-pix
```

## Saída Esperada

| Deliverable | Location |
|---|---|
| Especificação técnica | `_outputs/<slug>/outputs_downstream/specs/SPEC-<slug>.md` |

## Próximo passo

Após aprovação da spec, rode `/plan --slug <slug>` para a etapa de arquitetura/plano técnico.

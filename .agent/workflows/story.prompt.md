---
description: "Cria ou refina itens de backlog SAFe (Epics, Capabilities, Features, User Stories e Tasks) com ACs Gherkin e DoR checklist"
command: /story
category: Backlog
orchestrator: kare-orchestrator
orchestrator-mode: parallel
agents-required:
   - primary: "@story-crafter"
      secondary: ["@test-engineer", "@risk-analyst", "@review-master"]
context-required:
   - PROJECT_CONTEXT.md
   - PRD.md
   - BACKLOG.md
disclaimer: "?? Cria stories com critérios de aceitação em Gherkin. Valida DoR automaticamente. NÃO substitui /sprint. Tempo: 3-5 min. Saídas: Story, ACs, DoR, Testes"
---

# /story Workflow

## O que faz
Cria ou refina itens de backlog com rastreabilidade completa: epic, capability,
feature, story formatada, ACs em Gherkin e DoR checklist preenchido.

## O que NÃO faz
- Não substitui o planejamento de sprint do `/sprint`
- Não executa implementação técnica
- Não força `Capability` quando o contexto é simples

## Passos

// turbo
1. Verificar `PRD.md` e o item pai relevante em `demandas_processadas/<context_slug>/upstream/` (`Epic`, `Capability` e/ou `Feature`)

2. Invocar `@story-crafter` com o escopo fornecido
   - Output: story formatada + ACs em Gherkin + DoR checklist

3. Disparar em paralelo (fan-out), após concluir o passo 2:
   - `@test-engineer` para gerar casos de teste dos ACs
   - `@risk-analyst` para riscos específicos da story
   - Outputs: casos de teste + arquivo `.feature` (se BDD ativo) + seção de riscos

4. Opcional (flag `--review`): Invocar `@review-master` no fan-in (após passo 3)
   - Output: story refinada com feedback INVEST

5. Executar `/memory-refresh --context <context_slug>`
   - Output: memória navegável reconciliada com novas stories/ACs/riscos

## Uso

```
/story [descrição do que precisa]
/story --epic EP-03 [descrição]
/story --capability CAP-02 [descrição]
/story --feature FEAT-07 [descrição]
/story --refine [story existente]
/story --review [story]
```

## Saídas Esperadas

- Story formatada em Markdown (pronta para Jira/Linear/GitHub)
- ACs em Gherkin
- DoR checklist
- Casos de teste derivados
- Arquivo `.feature` (opcional)
- Story ingerida no RAG history: `kare_rag.py history ingest --type spec`

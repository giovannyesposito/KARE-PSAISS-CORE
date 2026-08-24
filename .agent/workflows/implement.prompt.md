---
description: "Implementa uma User Story com todo o contexto ágil — código rastreável a ACs, testes e ADRs"
command: /implement
category: Development
disclaimer: "💻 Este comando ESCREVE CÓDIGO REAL! Segue TDD (testes primeiro). Requer story ID ou descrição técnica clara. Tempo: 10-30 min. Saídas: Código, Testes, Docs, PR draft"
---

# /implement Workflow

## O que faz
Implementação completa de uma story com rastreabilidade ágil: código alinhado
aos ACs, testes BDD, e documentação de decisões técnicas.

## Passos

// turbo
1. Ler `TASKS-<slug>.md` em `_outputs/<slug>/outputs_downstream/tasks/` (gerado por `/speckit-tasks`) — se não existir, ler a story alvo com todos os ACs (de `backlog/` ou input do usuário) e avisar que o fluxo SDD completo não foi seguido

// turbo
2. Ler `SPEC-<slug>.md` e ADRs relevantes para tecnologias e padrões aplicáveis

// turbo
3. Verificar `PROJECT_CONTEXT.md` (BF → compatibilidade; GF → TDD-first)

4. Invocar `@test-engineer` para gerar testes (TDD Red):
   - Testes de unidade e integração para cada AC
   - Output: testes falhando (Red fase)

5. Invocar `@code-author` para implementar (TDD Green):
   - Código rastreado a ACs e ADRs
   - Output: implementação mínima para passar os testes

6. Invocar `@quality-guardian` para validar DoD de story:
   - Output: Gate report

7. Se BLOCKERs no gate: corrigir antes de prosseguir

8. Invocar `@tech-decision-maker` se decisão técnica relevante for tomada:
   - Output: ADR novo se aplicável

## Próximo passo

Após o gate de qualidade passar, rode `/speckit-converge --slug <slug>` para validar
a implementação contra a spec original e fechar o ciclo SDD Downstream.

## Uso

```
/implement --story US-42
/implement --story US-42 --tdd
/implement --story US-42 --no-tests
/implement --ac "AC específico"
```

## Saídas Esperadas

- Arquivos de código com rastreabilidade (comentários AC/Story/ADR)
- Testes cobrindo todos os ACs da story
- Gate report do DoD
- ADR novo (se decisão técnica relevante)
- `IMPL_NOTES.md` com changelog de implementação

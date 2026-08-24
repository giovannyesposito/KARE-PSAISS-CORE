---
description: "Gera plano de testes, casos de teste BDD/Gherkin e Test Coverage Matrix para uma story ou feature"
command: /test
category: Quality
disclaimer: "🧪 Gera testes completos (unit, integração, E2E) com cobertura. Calcula relatório. Requer código-fonte ou story ID. Tempo: 5-10 min. Saídas: Testes, Cobertura, Scripts CI/CD"
---

# /test Workflow

## O que faz
Cria artefatos de teste completos: Test Plan, casos de teste BDD (.feature),
Test Coverage Matrix e relatório de gaps de cobertura.

## Passos

// turbo
1. Ler story + ACs alvo (de `demandas_processadas/<context_slug>/upstream/` ou input do usuário)

// turbo
2. Verificar testes existentes no codebase para evitar duplicações

3. Invocar `@test-engineer` para gerar:
   - `TEST_PLAN.md` para o escopo
   - Arquivos `.feature` (Gherkin) para cada AC
   - Test Coverage Matrix (Story × AC × Tipo × Status)

4. Verificar gaps de cobertura e reportar ACs sem teste

5. Se flag `--generate-code`: Invocar `@code-author` em modo TDD-Red
   - Output: esqueletos de teste prontos para implementação

6. Invocar `@quality-guardian` na coverage matrix:
   - Output: validação se coverage atinge threshold do DoD

## Uso

```
/test --story US-42
/test --feature [nome da feature]
/test --release v2.1.0
/test --generate-code
/test --bdd
```

## Saídas Esperadas

- `demandas_processadas/<context_slug>/testes/TEST_PLAN.md`
- `demandas_processadas/<context_slug>/testes/features/[feature].feature`
- `demandas_processadas/<context_slug>/testes/COVERAGE_MATRIX.md`
- Relatório de gaps de cobertura
- Esqueletos de teste (se `--generate-code`)

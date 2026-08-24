---
description: "Registra decisões técnicas como ADRs ou RFCs. Detecta decisões implícitas no código e proativamente sugere documentação."
---

# /decision Workflow

## O que faz
Cria ADRs (Architecture Decision Records) e RFCs estruturados. Também escaneia
o codebase por decisões implícitas sem documentação.

## Passos

// turbo
1. Verificar ADRs existentes em `_outputs/<context_slug>/arq/` para evitar duplicações
   - Verificar índice `_outputs/<context_slug>/arq/ADR_INDEX.md` se existir

2. Invocar `@tech-decision-maker` com o contexto da decisão
   - Input: contexto fornecido pelo usuário (ou código a escanear)
   - Output: ADR-NNN.md ou RFC-NNN.md formatado

3. Atualizar `_outputs/<context_slug>/arq/ADR_INDEX.md` com o novo registro

4. Invocar `@risk-analyst` para documentar riscos da decisão
   - Output: seção de riscos adicionada ao ADR

5. Se flag `--scan`: escanear codebase por padrões sem ADR
   - Output: lista de decisões implícitas detectadas

## Uso

```
/decision [descrição da decisão a documentar]
/decision --adr [título]
/decision --rfc [título]
/decision --scan [módulo ou pasta]
/decision --supersede ADR-005 [nova decisão]
```

## Saídas Esperadas

- `_outputs/<context_slug>/arq/ADR-NNN.md` versionado
- `_outputs/<context_slug>/arq/RFC-NNN.md` (se RFC)
- `_outputs/<context_slug>/arq/ADR_INDEX.md` atualizado
- Lista de decisões implícitas detectadas (se `--scan`)

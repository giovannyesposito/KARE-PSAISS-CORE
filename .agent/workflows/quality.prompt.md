---
description: "Valida quality gates e Definition of Done para story, sprint ou release. Bloqueia avanço se BLOCKERs encontrados."
---

# /quality Workflow

## O que faz
Gate de qualidade explícito: valida DoD por nível (story/sprint/release),
emite relatório estruturado e bloqueia avanço quando necessário.

## Passos

// turbo
1. Determinar nível do gate: Story | Sprint | Release
   - Default: Story (nível mais restritivo)

// turbo
2. Ler story + ACs + DoD configurado para o projeto

3. Invocar `@quality-guardian` para validação completa:
   - AC Validation Matrix (story × AC × status)
   - DoD checklist preenchido por item
   - Gate report: ✅ PASS | ⚠️ WARNING | ❌ BLOCKER

4. Se BLOCKERs encontrados:
   - Listar exatamente o que está faltando com localização
   - Sugerir ação corretiva específica para cada BLOCKER
   - NÃO emitir PASS

5. Se WARNING: listar com severidade e deixar ao usuário decidir

6. Se flag `--fix`: Invocar `@code-author` para corrigir BLOCKERs automaticamente

## Uso

```
/quality --story US-42
/quality --sprint N
/quality --release v2.1.0
/quality --fix [blocker específico]
/quality --dod-level strict | standard | minimal
```

## Saídas Esperadas

- `QA_REPORT.md` com:
  - Gate status: ✅ PASS | ⚠️ WARNING | ❌ BLOCKER
  - AC Validation Matrix
  - DoD checklist itemizado
  - Lista de BLOCKERs com ação recomendada
  - Lista de WARNINGs

---
description: "Executa code review contextualizado com story, ACs e ADRs do projeto. Gera relatório estruturado por severidade."
command: /review
category: Quality
disclaimer: "?? Revisa código contra checklist KARE (testes, documentação, INVEST/SOLID). NÃO aprova — gera relatório com sugestões. Tempo: 3-5 min/arquivo. Saída: Relatório + Score"
---

# /review Workflow

## O que faz
Code review que vai além do estilo: valida que o código implementa os ACs
da story, respeita os ADRs e não introduz vulnerabilidades.

## Passos

// turbo
1. Verificar story associada ao PR/branch atual
   - Buscar em `demandas_processadas/<context_slug>/upstream/` ou solicitar ao usuário o ID da story

// turbo
2. Verificar ADRs relevantes em `demandas_processadas/<context_slug>/arq/`

3. Invocar `@review-master` com contexto completo:
   - Código/diff + story + ACs + ADRs
   - Output: Review report por severidade (BLOCKER/MAJOR/MINOR/NIT)

4. Invocar `@quality-guardian` para validar DoD:
   - Output: Gate report (?/??/?)

5. Se flag `--security`: Invocar scanner de vulnerabilidades (skill `vulnerability-scanner`)
   - Output: Relatório de segurança adicional

6. Gerar PR description se ausente

7. Executar `/memory-refresh --context <context_slug>` para atualizar memória de decisões e riscos após o review

## Uso

```
/review [PR number ou diff]
/review --story US-42
/review --security [PR]
/review --arch [módulo]
```

## Saídas Esperadas

- `REVIEW_REPORT.md` com BLOCKERs, MAJOR, MINOR, NIT
- DoD Gate report (?/??/?)
- PR description gerada (se ausente)
- Relatório de segurança (se `--security`)
- ADRs identificados no review ingeridos no RAG history: `kare_rag.py history ingest --type adr`

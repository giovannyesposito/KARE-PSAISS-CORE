---
description: "Valida DoD, gera release notes, runbook e checklist de release antes do deploy"
command: /release
category: Release
disclaimer: "📦 Gerencia release END-TO-END: versão, release notes, tags Git, notificações. Integra Jira/GitHub. Requer versão alvo (X.Y.Z). Tempo: 5-10 min. Saídas: Release notes, Tags"
---

# /release Workflow

## O que faz
Prepara e valida tudo que é necessário para um release seguro: DoD de release,
release notes, runbook e smoke test checklist.

## Passos

// turbo
1. Identificar escopo do release: sprints incluídas, versão, data alvo

// turbo
2. Invocar `@quality-guardian` para validar DoD de Release:
   - Verificar DoD de todas as stories do escopo
   - Output: Gate report de release (✅/⚠️/❌)

3. Invocar `@risk-analyst` para Risk Assessment de release:
   - Output: riscos identificados + plano de rollback

4. Invocar `@delivery-observer` para gerar:
   - Release notes versionadas
   - `RUNBOOK.md` de rollback
   - Smoke test checklist pós-deploy

5. Invocar `@review-master` para arch review das mudanças incluídas
   - Output: impacto em componentes existentes

6. Se DoD Gate tiver BLOCKERs: listar e interromper release

## Uso

```
/release --version v2.1.0
/release --scope sprint-14,sprint-15
/release --dry-run
/release --hotfix v2.0.1
```

## Saídas Esperadas

- `demandas_processadas/<context_slug>/releases/v2.1.0/RELEASE_NOTES.md`
- `demandas_processadas/<context_slug>/releases/v2.1.0/RELEASE_DOD_GATE.md`
- `demandas_processadas/<context_slug>/releases/v2.1.0/RUNBOOK.md`
- `demandas_processadas/<context_slug>/releases/v2.1.0/SMOKE_TEST_CHECKLIST.md`
- `demandas_processadas/<context_slug>/releases/v2.1.0/RISK_REPORT.md`

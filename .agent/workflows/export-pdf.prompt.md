---
description: "Exporta artefatos das demandas processadas para PDF sob demanda, preservando a estrutura por iniciativa."
command: /export-pdf
category: Operacao
orchestrator: kare-orchestrator
orchestrator-mode: sequential
agents-required:
   - primary: "@kare-orchestrator"
      secondary: ["@delivery-observer"]
context-required:
   - _outputs/
---

# /export-pdf Workflow

## Apresentacao do Comando (Placeholder Obrigatorio)

Toda vez que `/export-pdf` for evocado, exibir imediatamente antes de qualquer acao:

```text
?? Executando: /export-pdf --dest <path> [--source <path>] [--context <filtro>]
?? O que este comando faz: Exporta artefatos .md para .pdf de forma sob demanda, preservando a hierarquia por iniciativa em demandas_processadas.
?? Artefatos gerados: PDFs espelho de PRD, PRD-REVIEW, BACKLOG, USER_STORY_MAP, RAID, ARCHITECTURE, ADRs, PROJECT_BRIEF e ORCHESTRATION_REPORT.
? Aguarde...
```

## O que faz

Executa a exportacao para PDF apenas quando solicitado pelo usuario, sem automacao implicita em outros workflows.

## Regras de Execucao

1. `--dest` e obrigatorio.
2. `--source` e opcional (default: `_outputs/` no repo atual).
3. `--context` e opcional para exportar apenas uma iniciativa/filtro.
4. Nao acionar exportacao automaticamente em `/create`, `/KARE-flow` ou outros comandos.

## Comando de Execucao

```powershell
C:/Program Files/Python313/python.exe .agent/scripts/generators/export_pdf_demands.py --dest "<path>" [--source "<path>"] [--context "INI-001"]
```

## Uso

```text
/export-pdf --dest "C:\Users\...\PDF"
/export-pdf --dest "C:\Users\...\PDF" --context "INI-001"
/export-pdf --dest "C:\Users\...\PDF" --source "C:\repo\_outputs"
```

## Saidas Esperadas

- Estrutura de pastas por iniciativa replicada no destino.
- Arquivos `.pdf` para todos os `.md` encontrados no escopo.
- `EXPORT_REPORT.json` no destino com sumario de sucesso/falhas.

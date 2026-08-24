---
description: "Sincroniza artefatos recentes de _outputs/ com o RAG history (kare_history_rag.db)"
---

# /memory-refresh Workflow

## O que faz

Reconcilia os artefatos oficiais gerados em `_outputs/` com o banco de contexto RAG,
garantindo que decisões, PRDs e análises estejam pesquisáveis para os agentes.

## Quando usar

- Ao final de `/create`, `/story`, `/review` ou `/KARE-flow`
- Sempre que houver novo PRD, ADR, RAID ou análise em `_outputs/`
- Antes de iniciar novo ciclo que dependa de contexto de ciclos anteriores

## Passos

1. Identificar artefatos novos ou alterados em `_outputs/<context_slug>/`:
   - `upstream/PRD.md`, `upstream/BACKLOG.md`, `upstream/RAID.md`
   - `arq/ADR-*.md`
   - `sprints/*.md`, `releases/*.md`

2. Para cada artefato relevante, verificar se já está no RAG:
   ```bash
   python .agent/scripts/ai/kare_rag.py history search "<título>" --limit 3
   ```

3. Ingerir os que não estiverem (ou atualizar os desatualizados):
   ```bash
   python .agent/scripts/ai/kare_rag.py history ingest \
     --title "<título>" \
     --type prd|adr|analysis|spec|initiative \
     --domains "<domínio1,domínio2>" \
     --file <caminho>
   ```

4. Verificar status geral do RAG:
   ```bash
   python .agent/scripts/ai/kare_rag.py status
   ```

5. Se houver inconsistência ou artefato não encontrado, reportar com tag `[RAG_SYNC_REQUIRED]`

## Uso

```
/memory-refresh
/memory-refresh --context <context_slug>
```

## Saídas Esperadas

- RAG history atualizado com todos os artefatos do contexto
- Confirmação de quantos artefatos foram ingeridos/atualizados
- Lista de eventuais inconsistências encontradas

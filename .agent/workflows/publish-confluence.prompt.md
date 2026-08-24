---
description: "Publica artefatos KARE-SPEC no Confluence em estrutura hierárquica por iniciativa (sem Jira no MVP)"
---

# /publish-confluence Workflow

## O que faz

Publica e atualiza artefatos gerados no workspace para o Confluence, mantendo navegacao executiva e rastreabilidade entre PRD, Story Map, Backlog, ADRs, RAID e observabilidade.

## Escopo MVP Atual

- Inclui publicacao e update de paginas Confluence.
- Nao inclui criacao/atualizacao de issues Jira.

## Pagina Pai Padrao (MVP)

- Página pai: configurar conforme ambiente do projeto (ver `.config/.venv/mcp-atlassian.env`)
- Space: conforme configuração do projeto

## Pre-requisitos

1. MCP Atlassian ativo.
2. Credenciais válidas em `.config/.venv/mcp-atlassian.env`.
3. Acesso de escrita na página pai configurada.

## Passos

1. Validar se o MCP Atlassian esta configurado.
   - Se nao estiver, orientar execucao de `python .agent/scripts/infra/kare_credentials.py setup` e encerrar.

2. Resolver contexto alvo:
   - Identificar `context_slug` e iniciativa (`INI-XXX` quando houver).
   - Localizar artefatos em `demandas_processadas/<context_slug>/`.

3. Garantir estrutura no Confluence:
   - Página pai: conforme configuração do projeto
   - Iniciativa <INI-XXX - Nome>
   - Artefatos

4. Publicar/atualizar artefatos prioritarios:
   - `_outputs/<context_slug>/outputs_upstream/PRD.md`
   - `_outputs/<context_slug>/outputs_upstream/USER_STORY_MAP.md`
   - `_outputs/<context_slug>/outputs_upstream/BACKLOG.md`
   - `_outputs/<context_slug>/outputs_upstream/RAID.md`
   - `_outputs/<context_slug>/outputs_upstream/ADR-*.md`
   - `_outputs/<context_slug>/outputs_upstream/ARCHITECTURE.md`
   - `_outputs/<context_slug>/outputs_upstream/observabilidade/*.md` (quando aplicável)

5. Criar links cruzados obrigatorios:
   - PRD -> Story Map -> Backlog
   - PRD -> ADRs
   - RAID -> PRD e Backlog

6. Emitir relatorio de publicacao:
   - Paginas criadas
   - Paginas atualizadas
   - Pendencias/falhas

## Uso

```text
/publish-confluence --context <context_slug>
/publish-confluence --initiative INI-XXX
/publish-confluence --all
```

## Saidas Esperadas

- URLs de paginas publicadas/atualizadas no Confluence
- Estrutura da iniciativa consistente no Confluence
- Rastreabilidade navegavel entre artefatos

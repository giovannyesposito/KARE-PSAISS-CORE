---
description: "Cria issues no Jira a partir de backlog/stories KARE usando o MCP Atlassian, com rastreabilidade e relatório de sincronização."
---

# /create-issues-jira Workflow

## O que faz
Converte itens de backlog do KARE em issues no Jira por meio do servidor MCP Atlassian (`mcp-atlassian`), preservando rastreabilidade com Story, AC e contexto.

## Pré-condições

1. MCP `mcp-atlassian` configurado e autenticado.
2. Contexto da demanda existente em `uploads/<context_slug>/`.
3. Backlog disponível em `_outputs/<context_slug>/upstream/BACKLOG.md` ou `_outputs/projetos_KARE/<context_slug>/upstream/BACKLOG.md`.

Se alguma pré-condição falhar:
- interromper criação em massa
- retornar instruções objetivas para correção

## Passos

// turbo
1. Validar conectividade com Jira via MCP Atlassian
   - Confirmar que ferramentas Jira estão disponíveis (`jira_search`, `jira_create_issue`, `jira_get_issue`)

// turbo
2. Ler fonte dos itens a criar
   - padrão: `_outputs/<context_slug>/upstream/BACKLOG.md`
   - alternativa (KARE): `_outputs/projetos_KARE/<context_slug>/upstream/BACKLOG.md`
   - opcional: arquivo informado pelo usuário (stories/epics)

// turbo
3. Normalizar itens para payload Jira
   - mapear título, descrição, prioridade, labels
    - quando o item for Story e existir épico pai já criado, incluir o vínculo hierárquico no payload de criação
    - detectar o modelo do projeto Jira antes de montar o payload:
       - projeto simplificado / team-managed: usar `fields.parent.key=<EPIC_KEY>`
       - projeto clássico / company-managed: usar o campo de Epic Link configurado no projeto
   - incluir rastreabilidade obrigatória no corpo:
     - Story: `US-XX` (quando existir)
     - AC: `AC-X` (quando existir)
     - Contexto: `uploads/<context_slug>`
     - Origem: caminho do artefato KARE (`_outputs/<context_slug>/` ou `_outputs/projetos_KARE/<context_slug>/`)

4. Criar estrutura hierárquica no Jira
   - criar épicos antes das stories (quando aplicável)
   - ao criar stories, já persistir o vínculo com o épico no payload inicial; não deixar para etapa manual posterior
   - criar subtarefas somente quando explicitamente solicitado
   - evitar duplicados consultando por chave/título/label

5. Criar issues via MCP
   - usar `jira_create_issue`
   - após criação, validar com `jira_get_issue`
   - para stories, validar que o campo hierárquico retornado aponta para o épico esperado (`parent` ou Epic Link, conforme o projeto)
   - registrar key, url, tipo e status inicial

6. Pós-processamento
   - somente se o vínculo hierárquico não puder ser enviado na criação, executar atualização imediata da story para amarrá-la ao épico
   - opcional: transicionar status inicial via `jira_transition_issue`
   - opcional: adicionar comentário técnico padrão via `jira_add_comment`

7. Gerar relatório de sincronização
   - salvar em `_outputs/<context_slug>/upstream/JIRA_ISSUES_SYNC_REPORT.md`
     (ou `_outputs/projetos_KARE/<context_slug>/upstream/JIRA_ISSUES_SYNC_REPORT.md` se KARE)
   - incluir:
     - total solicitado
     - total criado
     - itens pulados (duplicados)
     - itens com erro
     - tabela `Item KARE -> Jira Key -> URL`

## Regras de mapeamento (padrão)

- Tipo:
  - Epic KARE -> Epic Jira
  - Story KARE -> Story Jira
  - Task técnica -> Task Jira

- Hierarquia Epic -> Story:
   - em projetos Jira simplificados (`simplified: true`), usar `fields.parent.key`
   - em projetos Jira clássicos, usar o campo de Epic Link exposto pelo `editmeta` / metadata do projeto
   - após criar a story, validar que ela nasceu vinculada ao épico correto

- Prioridade:
  - Must -> High
  - Should -> Medium
  - Could -> Low

- Labels sugeridas:
  - `kare`
  - `<context_slug>`
  - `source-backlog`

## Uso

```text
/create-issues-jira --context diagnostico-internet --project ABC
/create-issues-jira --context diagnostico-internet --project ABC --dry-run
/create-issues-jira --context diagnostico-internet --project ABC --only US-01,US-02
/create-issues-jira --context diagnostico-internet --project ABC --issue-type Story
```

## Flags recomendadas

- `--context <context_slug>`: contexto alvo
- `--project <JIRA_KEY>`: chave do projeto Jira
- `--dry-run`: valida e mostra payload sem criar issues
- `--only <lista>`: restringe IDs de story/epic
- `--issue-type <tipo>`: força tipo único
- `--transition <status>`: transição pós-criação

## Saídas esperadas

- Issues criadas/atualizadas no Jira via MCP
- `demandas_processadas/<context_slug>/upstream/JIRA_ISSUES_SYNC_REPORT.md`
- Resumo final com sucessos, duplicados e erros

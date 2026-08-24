---
description: "Ingesta base de conhecimento no cofre Obsidian por domínio (arquitetura, sistemas, integrações, APIs, observabilidade, stakeholders, projetos)"
---

# /novo-contexto-brain Workflow

## O que faz

Permite inserir conhecimento no cofre Obsidian de forma estruturada por domínio,
com suporte a anexos e vínculo opcional a contexto de projeto.

## Perguntas Obrigatórias

1. O conteúdo está ligado a qual domínio?
   - Arquitetura
   - Sistemas
   - Integrações
   - APIs
   - Observabilidade
   - Stakeholders
   - Projetos/Iniciativas

2. Esse conhecimento está relacionado a um contexto/projeto existente?
   - Se sim, informar `context_slug`

3. Qual a fonte de entrada?
   - arquivo único
   - pasta com múltiplos arquivos

## Tipos de Arquivo Suportados

- `.pdf`, `.txt`, `.md`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.csv`, `.json`, `.yaml`, `.yml`
- Outros formatos são aceitos como anexo bruto, com metadado de extensão.

## Passos

1. Validar domínio selecionado
2. Executar ingestão:
   - `python .agent/scripts/ai/brain_ingest.py . --input <path> --domain <domain_key> --context <context_slug>`
3. Ingerir no RAG history se houver artefatos de projeto:
   - `python .agent/scripts/ai/kare_rag.py history ingest --title "..." --type analysis --domains "..." --file <path>`
4. Buscar interdependências no RAG: `kare_rag.py search "<contexto>" --limit 5`

## Uso

```
/novo-contexto-brain
/novo-contexto-brain --domain integracoes --input docs/
/novo-contexto-brain --domain arquitetura --input material/diagrama.pdf --context <context_slug>
```

## Saídas Esperadas

- Nota de conhecimento criada no domínio selecionado
- Nota de conhecimento criada em `_outputs/brain-knowledge/<domain>/`
- Anexos registrados em `_outputs/brain-knowledge/base-conhecimento/<domain>/`
- Artefatos relevantes ingeridos no RAG history: `kare_rag.py history ingest`

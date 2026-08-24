---
description: "Inicia fluxo completo de discovery — classifica o projeto, gera Brief + PRD e popula o backlog inicial"
command: /create
category: Discovery
orchestrator: kare-orchestrator
orchestrator-mode: conditional
agents-required:
   - primary: "@project-classifier"
      secondary: ["@product-discovery", "@prd-reviewer", "@backlog-architect", "@risk-analyst", "@story-crafter"]
context-required:
   - PROJECT_CONTEXT.md
   - RAG perene: `kare_rag.py search "<contexto>" --db perene`
---

# /create Workflow

## O que faz
Orquestra o fluxo completo de criação de produto: classificação do projeto →
brief → PRD → revisão → backlog inicial.

## Estrutura em `uploads/` para nova demanda

A pasta `uploads/` é a **zona de entrada** — armazena apenas arquivos brutos fornecidos pelo usuário e a conversão quando necessária:

```text
uploads/<context_slug>/
├── <arquivo-original>.pptx      ← canvas bruto (raiz do slug)
└── Conversão/                   ← .md gerado pelo ppt_to_kare.py (só se houver PPT)
```

Regras:
- O arquivo bruto (.pptx, .pdf, etc.) fica diretamente na raiz de `uploads/<context_slug>/`
- A pasta `Conversão/` só é criada quando houver conversão de PPT — caso contrário não existe
- Nenhum artefato gerado pelos agentes vai para `uploads/` — todos os outputs vão para `_outputs/<slug>/outputs_upstream/`

## Entrada com PowerPoint

Se o argumento do usuário for um arquivo `.ppt` ou `.pptx`, o workflow deve:

1. Derivar `context_slug` e garantir que `uploads/<context_slug>/` existe
2. Manter o `.ppt/.pptx` na raiz de `uploads/<context_slug>/` (não mover para subpasta)
3. Criar `uploads/<context_slug>/Conversão/` e executar `python .agent/scripts/generators/ppt_to_kare.py <arquivo> --output uploads/<context_slug>/Conversão/<UPPER_SNAKE_CASE>.md --kare-context`
4. Usar o arquivo gerado em `uploads/<context_slug>/Conversão/` como fonte oficial do discovery
5. Ler `canvas_type` no frontmatter/metadata do `.md` gerado
6. Prosseguir no `/create` com base nesse contexto convertido e no tipo detectado

## Roteamento por `canvas_type`

### Quando `canvas_type = initiative`

Use a trilha completa de discovery:

- `@project-classifier`
- `@product-discovery` para Brief + PRD completos
- `@prd-reviewer`
- `@backlog-architect`
- `@risk-analyst`

### Quando `canvas_type = feature`

Use discovery enxuto, orientado a backlog:

- `@project-classifier`
- `@product-discovery` em escopo de feature/epic, evitando brief amplo de produto quando já houver contexto suficiente
- `@story-crafter` para transformar a feature em épico + stories iniciais
- `@backlog-architect` para priorização do backlog derivado
- `@risk-analyst` para riscos específicos da feature
- `@prd-reviewer` apenas se houver PRD/feature spec suficientemente completo para revisão formal

### Quando `canvas_type = unknown`

Assumir trilha conservadora:

- tratar como `initiative` por padrão
- marcar no discovery que o tipo do canvas precisa de validação (`[PRECISA_VALIDAR]`)

## Contexto Base — Consultar Antes de Iniciar

Antes de qualquer ação, buscar contexto relevante do projeto via RAG:

```bash
python .agent/scripts/ai/kare_rag.py search "<contexto do projeto>" --limit 5
python .agent/scripts/ai/kare_rag.py search "<termos>" --db perene --limit 5
```

---

## Passos

// turbo
1. Se a entrada for `.ppt`/`.pptx`, converter para Markdown com `ppt_to_kare.py`

// turbo
1.1. Garantir que `uploads/<context_slug>/` existe

// turbo
1.1b. Criar estrutura obrigatória em `_outputs/<context_slug>/`:
```
_outputs/<context_slug>/
├── outputs_upstream/
│   ├── (PRD, Brief, Backlog, RAID, Story Map, ADRs)
│   ├── sprints/
│   ├── testes/
│   └── releases/
└── outputs_downstream/
    ├── specs/
    ├── plans/
    ├── tasks/
    ├── implementations/
    └── convergence/
```
Registrar no RAG:
```bash
python .agent/scripts/ai/kare_rag.py ingest \
  --title "Estrutura Demanda <context_slug>" \
  --type context \
  --context <context_slug> \
  --content "Estrutura canonica criada em _outputs/<context_slug>/: outputs_upstream/ outputs_downstream/"
```

// turbo
1.2. Se houver PPT, criar `uploads/<context_slug>/Conversão/` e salvar o `.md` convertido nela

// turbo
2. Se houve conversão, ler o `canvas_type` do arquivo gerado em `uploads/<context_slug>/Conversão/`

// turbo
3. Verificar se `PROJECT_CONTEXT.md` existe em `_outputs/<context_slug>/upstream/`

// turbo
4. Invocar `@project-classifier` para classificar o projeto (GF/BF/Híbrido)
   - Output: `_outputs/<context_slug>/outputs_upstream/PROJECT_CONTEXT.md` criado/atualizado

5. Seguir o branch abaixo conforme `canvas_type`:

#### Branch A — `initiative`

6A. Invocar `@product-discovery` com o contexto classificado
   - Input: ideia/escopo fornecido pelo usuário + `_outputs/<context_slug>/upstream/PROJECT_CONTEXT.md`
   - Se houve conversão de PPT, incluir também o `.md` gerado em `uploads/<context_slug>/Conversão/`
   - Output: `PROJECT_BRIEF.md` + `PRD.md`

7A. Invocar `@prd-reviewer` no PRD gerado
   - Output: `PRD_REVIEW_REPORT.md`

8A. Se PRD_REVIEW_REPORT tiver BLOCKERs:
   - Mostrar BLOCKERs ao usuário e aguardar correção
   - Caso contrário: prosseguir

9A. Disparar em paralelo (fan-out), após concluir o passo 8A:
   - `@backlog-architect` para backlog inicial do PRD
   - `@risk-analyst` para RAID inicial
   - Outputs: `BACKLOG.md` + `RAID.md` com `Status: ⏳ PENDENTE APROVAÇÃO`

#### Branch B — `feature`

6B. Invocar `@product-discovery` em modo escopo `feature/epic`
   - Input: canvas de feature + `_outputs/<context_slug>/upstream/PROJECT_CONTEXT.md`
   - Output esperado: especificação enxuta da feature, podendo reutilizar o contexto/produto existente
   - Se o contexto já for suficiente, não expandir para um `PROJECT_BRIEF.md` amplo de produto

7B. Invocar `@story-crafter` para gerar épico e stories iniciais a partir da feature
   - Output: backlog inicial da feature com ACs e DoR

8B. Disparar em paralelo (fan-out), após concluir o passo 7B:
   - `@backlog-architect` para priorização do backlog da feature
   - `@risk-analyst` para riscos específicos da feature
   - Outputs: `BACKLOG.md` + `RAID.md` focados na feature

9B. Se a especificação da feature estiver robusta o suficiente, invocar `@prd-reviewer`
   - Caso contrário, registrar `[PRECISA_VALIDAR]` e seguir com backlog draft

10. Ao final de qualquer branch, executar `/memory-refresh --context <context_slug>`
   - Objetivo: ingerir artefatos gerados em `_outputs/<context_slug>/` no RAG history

## Uso

```
/create [descrição da ideia ou feature]
/create [caminho/arquivo.pptx]
/create [caminho/arquivo.ppt]
/create --scope epic [nome do épico]
/create --mode gf | bf | hybrid
```

## Saídas Esperadas

- `uploads/<context_slug>/<arquivo-origem>.pptx` (arquivo bruto)
- `uploads/<context_slug>/Conversão/<CANVAS_CONVERTIDO>.md` (somente se houver PPT)
- `_outputs/<context_slug>/outputs_upstream/PROJECT_CONTEXT.md`
- `_outputs/<context_slug>/outputs_upstream/PROJECT_BRIEF.md`
- `_outputs/<context_slug>/outputs_upstream/PRD.md`
- `_outputs/<context_slug>/outputs_upstream/PRD_REVIEW_REPORT.md`
- `_outputs/<context_slug>/outputs_upstream/BACKLOG.md`
- `_outputs/<context_slug>/outputs_upstream/RAID.md`
- Artefatos ingeridos no RAG history: `kare_rag.py history ingest --title "..." --type prd|analysis --domains "<slug>"`

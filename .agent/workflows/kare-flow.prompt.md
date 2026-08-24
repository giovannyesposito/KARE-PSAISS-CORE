---
description: "Executa o KARE Flow ponta a ponta a partir de um Canvas ou ideia, gerando PRD, Story Map, Backlog SAFe, ADRs e RAID. Publicação no Confluence é opcional e acionada separadamente via /publish-confluence."
command: /kare-flow
category: Discovery
orchestrator: kare-orchestrator
orchestrator-mode: conditional
agents-required:
   - primary: "@kare-orchestrator"
     secondary: ["@project-classifier", "@product-discovery", "@prd-reviewer", "@backlog-architect", "@tech-decision-maker", "@risk-analyst", "@quality-guardian"]
context-required:
   - PROJECT_CONTEXT.md
   - RAG: `kare_rag.py search "<contexto>" --db perene`
---

# /kare-flow Workflow

## ⚠️ Protocolo de Aprovação Prévia

Antes de qualquer geração de artefatos, o `@kare-orchestrator` DEVE:

1. Exibir na janela de conversa o plano completo:
   - Lista de artefatos a serem gerados
   - Estrutura de cada documento (seções)
   - Paths de destino
   - Agentes envolvidos e modo de execução
   - Prévia visual do Story Map e fatiamento de demandas (ASCII ou Mermaid)

2. Aguardar aprovação explícita do usuário

3. Somente após "de acordo" iniciar a geração

## O que faz

Orquestra o fluxo E2E de produto/software — da ideia ou canvas até artefatos prontos para execução. A publicação no Confluence **não** faz parte deste fluxo — deve ser acionada via `/publish-confluence --context <context_slug>`.

## Escopo

- **Inclui:** Canvas → PRD → PRD Review → Arquitetura (diagramas) → Story Map → Backlog SAFe → ADRs → RAID → Jornada HTML (condicional)
- **Opcional:** publicação no Confluence via `/publish-confluence --context <context_slug>`
- **Não inclui:** estruturação Jira automática

## Apresentação do Plano (Exibir antes de gerar)

```
⚙️ Executando: /kare-flow [argumentos]

📋 O que este comando faz:
   Orquestra o fluxo completo de produto/software — da ideia ao artefato pronto para execução.
   Classifica o projeto, gera PRD, faz review, produz Backlog SAFe, User Story Map,
   ADRs, Architecture e RAID.

🎯 Artefatos que serão gerados:
  ├─ PROJECT_CONTEXT.md   → _outputs/<slug>/outputs_upstream/
  ├─ PROJECT_BRIEF.md     → _outputs/<slug>/outputs_upstream/
  ├─ PRD.md               → _outputs/<slug>/outputs_upstream/
  ├─ PRD-REVIEW.md        → _outputs/<slug>/outputs_upstream/
  ├─ BACKLOG.md           → _outputs/<slug>/outputs_upstream/ [⏳ PENDENTE APROVAÇÃO]
  ├─ USER_STORY_MAP.md    → _outputs/<slug>/outputs_upstream/ [⏳ PENDENTE APROVAÇÃO]
  ├─ RAID.md              → _outputs/<slug>/outputs_upstream/ [⏳ PENDENTE APROVAÇÃO]
  ├─ ADR-XXX.md           → _outputs/<slug>/outputs_upstream/ [⏳ PENDENTE APROVAÇÃO]
  ├─ ARCHITECTURE.md      → _outputs/<slug>/outputs_upstream/ [⏳ PENDENTE APROVAÇÃO]
  └─ JORNADA-<slug>.html  → _outputs/<slug>/outputs_downstream/ [condicional: UI interativa]

🔍 Prévia do Story Map (estrutura esperada):
  Iniciativa
   └── Épico (EP-001)
        └── Feature (FEAT-001)
             ├── US-001 (MVP)
             ├── US-002 (MVP)
             └── US-003 (Fase 2)

✋ Aguardando seu "de acordo" para iniciar...
```

## Contexto Base — Consultar Antes de Iniciar

```bash
python .agent/scripts/ai/kare_rag.py search "<contexto do projeto>" --db perene --limit 5
python .agent/scripts/ai/kare_rag.py search "<domínio>" --limit 5
```

## Passos (executar após aprovação)

1. Identificar ou criar `uploads/<context_slug>/`:
   - Arquivo bruto (.pptx, .pdf) fica na raiz de `uploads/<context_slug>/`
   - Se houver conversão PPT, criar `uploads/<context_slug>/Conversão/`

   Criar estrutura de outputs:
   ```
   _outputs/<context_slug>/
   ├── outputs_upstream/
   │   ├── (PRD, Brief, Backlog, RAID, Story Map, ADRs, Architecture)
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

2. Se a entrada for `.ppt`/`.pptx`, converter com `ppt_to_kare.py`.

3. Verificar contexto: ler `PROJECT_CONTEXT.md` se existir, senão invocar `@project-classifier`.

4. Executar discovery:
   - `@product-discovery` → `PROJECT_BRIEF.md` + `PRD.md`
   - `@prd-reviewer` → bloquear se BLOCKER

5. Executar backlog e mapeamento:
   - `@backlog-architect` → `BACKLOG.md` (hierarquia: Iniciativa → EP → FEAT → US/EN)
   - Skill `user-story-mapping` → `USER_STORY_MAP.md`
   - Ambos com `Status: ⏳ PENDENTE APROVAÇÃO`

6. Executar arquitetura e risco (paralelo):
   - `@tech-decision-maker` → ADRs + `ARCHITECTURE.md` (diagramas Mermaid)
   - `@risk-analyst` → `RAID.md`
   - Todos com `Status: ⏳ PENDENTE APROVAÇÃO`

6a. Gerar Jornada HTML (condicional):
   - Ativar se: iniciativa com UI interativa (web, mobile, etc.)
   - Output: `JORNADA-<slug>.html` em `_outputs/<slug>/outputs_downstream/`

7. Validar qualidade: `@quality-guardian` → gate do pacote de artefatos.

8. Atualizar memória: `/memory-refresh --context <context_slug>`

## Uso

```
/kare-flow [descrição da iniciativa]
/kare-flow [caminho/arquivo.pptx]
/kare-flow --context <context_slug>
/kare-flow --canvas <caminho_canvas>
```

## Saídas Esperadas

| Artefato | Localização | Obrigatório |
|---|---|---|
| `PROJECT_CONTEXT.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `PROJECT_BRIEF.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `PRD.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `PRD-REVIEW-<slug>.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `USER_STORY_MAP.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `BACKLOG.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `RAID.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `ADR-XXX.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `ARCHITECTURE.md` | `_outputs/<slug>/outputs_upstream/` | Sim |
| `JORNADA-<slug>.html` | `_outputs/<slug>/outputs_downstream/` | Condicional (UI interativa) |

## Protocolo de Aprovação de Artefatos

ADRs, BACKLOG, RAID, ARCHITECTURE e USER_STORY_MAP são gerados com `Status: ⏳ PENDENTE APROVAÇÃO`.

Aprovação durante a sessão: usuário diz `"aprovo [artefato]"` → atualizar Status para `✅ Aprovado` + ingerir no RAG.

## Critérios de Conclusão

- PRD sem BLOCKER após review
- Estrutura de pastas criada em `_outputs/<slug>/outputs_upstream/` e `outputs_downstream/`
- Story Map cobrindo MVP e releases
- BACKLOG, RAID, ADRs e ARCHITECTURE com `Status: ⏳ PENDENTE APROVAÇÃO`
- Artefatos ingeridos no RAG history
- Artefatos prontos para publicação

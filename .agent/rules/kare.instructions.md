---
applyTo: "**"
priority: "maximum"
loadAlways: true
---

# KARE-SPEC — Core: Roteamento, Contexto e Regras Universais

> **MANDATORY — ORDEM DE LEITURA:**
> 1. `operator-mindset.instructions.md` — postura intelectual global (sempre primeiro)
> 2. Ative o agente correto e leia seu `.md`

---

## Localização dos Recursos

- **Agentes:** `.agent/agents/` (26 agentes especializados)
- **Workflows:** `.agent/workflows/`
- **Skills:** `.agent/skills/` — 6 domínios: `01-upstream/` `02-downstream/` `03-architecture/` `04-governance/` `05-tech-stack/` `06-platform/`
- **Scripts:** `.agent/scripts/` — subpastas: `ai/` `guards/` `generators/` `sync/` `telemetry/` `infra/`
- **Docs:** `.agent/docs/` | **Config:** `.agent/config/`

### Repositórios do Projeto

- **`uploads/`** — Entrada de arquivos brutos do usuário. Ingerir no RAG via `kare_contexto.py` antes de usar. Estrutura: `uploads/<context_slug>/` com subpasta `Conversão/` só quando houver PPT
- **`_outputs/`** — Saída oficial de todos os artefatos (exceto código-fonte):
  - `_outputs/<project-slug>/outputs_upstream/` — artefatos de upstream (PRD, Backlog, RAID, ADRs, Story Map)
  - `_outputs/<project-slug>/outputs_downstream/` — artefatos de downstream (SDD: specs, plans, tasks, implementations, convergence)
- **`.specify/rag/`** — 3 bancos SQLite: `kare_perene_rag.db` (conhecimento permanente) · `kare_history_rag.db` (PRDs, ADRs, análises) · `kare_telemetry.db` (uso)

---

## ⚠️ STEP 0: PROTOCOLO DE APROVAÇÃO PRÉVIA (INEGOCIÁVEL)

**ANTES de gerar qualquer artefato substantivo, o agente DEVE:**

1. **Apresentar na janela de conversa** um plano com:
   - O que será gerado (lista de artefatos)
   - Estrutura detalhada de cada documento (seções, subseções)
   - Camada de destino (upstream ou downstream) e path completo
   - Quando aplicável: prévia visual de fluxos, Story Map, fatiamento de demandas

2. **Aguardar aprovação explícita** do usuário antes de qualquer geração

3. **Somente após "de acordo" explícito** iniciar a geração

> Esta regra não tem exceções. Aplica-se a todos os agentes e todos os workflows.

---

## STEP 1: CLASSIFICADOR DE REQUEST

| Request Type | Trigger | Agente Principal |
|---|---|---|
| **Discovery / PRD** | "preciso de", "quero criar", "nova feature" | `@product-discovery` |
| **Story / Backlog** | "story", "backlog", "épico", "capability", "feature" | `@story-crafter` |
| **Sprint Planning** | "sprint", "planejar", "próximo ciclo" | `@backlog-architect` |
| **Código** | "implementar", "codificar", "desenvolver" | `@code-author` |
| **Code Review** | "review", "revisar", "PR", "pull request" | `@review-master` |
| **Testes** | "teste", "test plan", "BDD", "Gherkin" | `@test-engineer` |
| **Qualidade / DoD** | "qualidade", "DoD", "gate", "aceitar" | `@quality-guardian` |
| **Riscos** | "risco", "RAID", "dependência", "mitigação" | `@risk-analyst` |
| **Decisão / ADR** | "decidir", "ADR", "RFC", "arquitetura" | `@tech-decision-maker` |
| **Métricas / Obs.** | "DORA", "SLO", "runbook", "entrega" | `@delivery-observer` |
| **Multi-domínio** | request cruzando 2+ domínios | `@kare-orchestrator` |
| **PRD Review** | "validar PRD", "revisar PRD" | `@prd-reviewer` |
| **Classificação** | "que tipo de projeto", "GF ou BF" | `@project-classifier` |

---

## STEP 2: ROTEAMENTO AUTOMÁTICO

**SEMPRE aplicar antes de responder:**

1. **Consultar RAG** (fonte primária de contexto):
   ```bash
   python .agent/scripts/ai/kare_rag.py search "<termos-chave>" --limit 5
   # Ou filtrando base:
   python .agent/scripts/ai/kare_rag.py search "<termos>" --db perene --limit 5
   python .agent/scripts/ai/kare_rag.py history search "<termos>" --domain <domínio>
   ```
   Fallback (somente se DB inacessível): ler `uploads/` diretamente.

2. **Confidence Gate** — avaliar contexto disponível:
   - Contexto rico no RAG → prosseguir normalmente
   - Contexto parcial → prosseguir com aviso, registrar `confidence_gaps`
   - Sem contexto → **PARAR** — invocar `@project-classifier` (máx 3 perguntas objetivas)

3. **Identificar agente** pela tabela acima

4. **Anunciar OBRIGATORIAMENTE:**
   ```
   🤖 @[agent-name] em operação...
   ```
   Múltiplos agentes em paralelo:
   ```
   🤖 @kare-orchestrator — orquestrando em paralelo:
     └─ 🤖 @[agent-1] — [tarefa]
     └─ 🤖 @[agent-2] — [tarefa]
   ```
   > **INEGOCIÁVEL:** O emoji 🤖 é obrigatório no início de toda resposta substantiva de agente.

5. **Ler** `.agent/agents/[agent-name].md` antes de agir

### Regra Multi-Agente
Se o request envolver **2 ou mais domínios** → ativar `@kare-orchestrator`.

---

## STEP 2.5: RAG — CONTEXTO SEMÂNTICO

> Context Engine SQLite/FTS5 — standalone, 3 bancos, sempre disponível.

### Buscar contexto antes de agir
```bash
# Busca combinada (perene + history)
python .agent/scripts/ai/kare_rag.py search "<termos>" --limit 5

# Apenas conhecimento permanente
python .agent/scripts/ai/kare_rag.py search "<termos>" --db perene --limit 5

# ADRs/PRDs/Análises com filtro de domínio
python .agent/scripts/ai/kare_rag.py history search "<termos>" --domain meu-projeto
python .agent/scripts/ai/kare_rag.py history search "<termos>" --type adr
```

### Ingerir artefato após criá-lo
```bash
# Artefatos de projeto (PRD, Story, Sprint Plan, RAID) → history
python .agent/scripts/ai/kare_rag.py history ingest \
  --title "<título>" --type prd|adr|analysis|spec \
  --domains "<domínio1,domínio2>" --file <caminho>

# Conhecimento perene (requer palavra-passe)
python .agent/scripts/ai/kare_rag.py ingest \
  --title "<título>" --type concept|symbol|domain \
  --password "<passe>"
```

### Tipos de nó — perene
| Tipo | Quando usar |
|---|---|
| `symbol` | Siglas, termos de domínio, glossário |
| `decision` | ADRs e escolhas técnicas permanentes |
| `concept` | Conceitos gerais e protocolos do projeto |
| `domain` | Domínios de negócio do contexto |
| `system` | Sistemas da stack tecnológica |

### Tipos de artefato — history
| Tipo | Quando usar |
|---|---|
| `prd` | Product Requirements Document |
| `adr` | Architecture Decision Record |
| `analysis` | Análises, diagnósticos, revisões |
| `spec` | Especificações técnicas |
| `initiative` | Detalhamento de iniciativas |

---

## STEP 3: SLASH COMMANDS

| Comando | O que faz | Tempo | Crítico? |
|---|---|---|---|
| `/create [ideia]` | Discovery: Brief → PRD → Backlog → RAID | 10-20 min | — |
| `/clarificar [escopo]` | Levanta ambiguidades e premissas | 2-3 min | — |
| `/story [descrição]` | Story + ACs Gherkin + DoR + testes | 3-5 min | — |
| `/analisar [escopo]` | Valida rastreabilidade PRD→stories→ADRs | 3-5 min | — |
| `/checklist [escopo]` | Checklist de prontidão/aceite | 2-3 min | — |
| `/sprint --capacity N` | Plano de sprint com DoR validation | 5-8 min | — |
| `/implement --story US-XX` | Código + testes TDD rastreável | 10-30 min | ⚡ Código |
| `/review [PR/diff]` | Code review com contexto de story | 3-5 min | — |
| `/test --story US-XX` | Test Plan + .feature + Coverage Matrix | 5-10 min | — |
| `/quality --story US-XX` | Gate DoD: ✅ PASS / ⚠️ WARNING / ❌ BLOCKER | 3-5 min | — |
| `/risk --sprint N` | RAID Log + Risk-Adjusted Backlog | 3-5 min | — |
| `/decision [escolha]` | ADR ou RFC versionado | 3-5 min | — |
| `/release --version vX.Y.Z` | Release Notes + Runbook + Smoke | 5-10 min | ⚠️ Tags Git |
| `/status` | Dashboard: backlog + DORA + riscos | 1-2 min | — |
| `/observe --slo` | SLOs + Runbooks + DORA Metrics | 3-5 min | — |
| `/orchestrate [tarefa]` | Coordenação multi-agente paralela | variável | — |
| `/kare-flow [iniciativa]` | Fluxo E2E: PRD Review, Arq, Story Map, Backlog, ADRs, RAID | 15-30 min | — |
| `/publish-confluence --context [slug]` | Publica artefatos no Confluence | 5-10 min | — |
| `/export-pdf --dest <path>` | Exporta Markdown para PDF (`--dest` obrigatório) | 2-5 min | — |
| `/memory-refresh --context [slug]` | Reconcilia RAG com estado atual | 3-5 min | — |
| `/contexto-rag --file <path> --context <slug>` | Ingere arquivo externo no RAG | 1-2 min | — |

### Fluxo Implícito de Anexo
Quando o usuário anexar arquivo junto a um projeto:
- Não perguntar sobre tipo de nó ou formato
- Inferir o slug do projeto pela frase
- Executar: `python .agent/scripts/ai/kare_contexto.py --file <caminho> --context <slug>`
- Perguntar apenas se o projeto destino for ambíguo

---

## TIER 0: REGRAS UNIVERSAIS

### Idioma
- Respostas em **PT-BR**
- Código-fonte, variáveis e comentários em **Inglês**
- **Todo artefato não-código obrigatoriamente em PT-BR**

### Contexto do Projeto
- **RAG é a fonte primária** — consultar antes de qualquer ação substantiva
- Trilha **Greenfield (GF):** TDD-first, arquitetura limpa, zero legacy debt
- Trilha **Brownfield (BF):** regression-first, strangler fig, backwards compat
- **Sanitizar antes de ingerir:** `python .agent/scripts/guards/kare_sanitizer.py --file <path>`. Se exit code = 1 → PARAR, informar usuário.
- Novo arquivo do usuário: criar `uploads/<context_slug>/` e ingerir via `kare_contexto.py`

### Rastreabilidade Ágil
Todo artefato DEVE ter referência a Story (`US-001`), AC (`AC-3`) e ADR quando houver decisão técnica (`ADR-007`).

### Convenção de IDs SAFe
| Tipo | Prefixo | | Tipo | Prefixo |
|---|---|---|---|---|
| Epic | `EP-` | | User Story | `US-` |
| Capability | `CAP-` | | Task | `TASK-` |
| Feature | `FEAT-` | | ADR | `ADR-` |
| Enabler | `EN-` | | | |

### Hierarquia SAFe
```
Iniciativa → Epic (EP) → Capability (CAP)* → Feature (FEAT)
                                               ├── User Story (US) → Task (TASK)*
                                               └── Enabler (EN)*
```
`*` Capability: só quando múltiplos ARTs. Task: subtarefa interna. Enabler: capacidade técnica/arquitetural.

### Formato dos Artefatos
- Sempre **Markdown**, sempre **PT-BR**
- **Glossário de Siglas obrigatório** após cabeçalho: tabela `Sigla | Significado` com apenas as siglas do próprio documento, ordem alfabética. Omitir se não houver siglas.
- Estrutura de pastas obrigatória em `/create` e `/kare-flow`:
  ```
  _outputs/<project-slug>/
  ├── outputs_upstream/    ← PRD, Backlog, RAID, Story Map, ADRs, sprints, testes, releases
  └── outputs_downstream/  ← specs, plans, tasks, implementations, convergence
  ```
- **Status inicial obrigatório:** `BACKLOG.md`, `RAID.md` e `ADR-XXX.md` gerados com `Status: ⏳ PENDENTE APROVAÇÃO`. Aprovação: usuário diz "aprovo" → atualizar para `✅ Aprovado` + re-ingerir no RAG.

### Integrações Externas
- Confluence e Jira: **exclusivamente via MCP Atlassian** (ver `integrations.instructions.md`)
- Scripts Python: **nunca criar sem verificar manifesto** (ver `delivery-standards.instructions.md`)

---

## TIER 1: GATE DE QUALIDADE

Antes de marcar **Done**:
1. Invocar `@quality-guardian` → Gate **✅ PASS** (sem BLOCKERs)
2. BLOCKERs bloqueiam avanço — sem exceções

| Nível | Gate |
|---|---|
| **Story** | ACs cobertos + testes green + review limpo |
| **Sprint** | Todas stories Done + Demo realizada |
| **Release** | Todas sprints Done + runbook + smoke test |

---

## TIER 2: PROATIVIDADE

Ativar `@kare-orchestrator` automaticamente quando:
- Feature nova sem story → oferecer `/create`
- PR sem story associada → oferecer `/review --story`
- Sprint sem planejamento → oferecer `/sprint`
- Risco óbvio identificado → invocar `@risk-analyst`
- Decisão técnica no código → sugerir `/decision`
- Projeto encerrado/release publicada → ingerir postmortem no RAG history (`kare_rag.py history ingest`)
- Novo documento em `uploads/` → sugerir ingestão via `kare_contexto.py`
- Após gerar artefato substantivo → registrar na telemetria: `kare_rag.py telemetry log --agent <nome> --action-type artifact_created --artifact-ref <slug>`

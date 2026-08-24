---
name: kare-operating-model
description: >
  Modelo operacional genérico do KARE-SPEC. Define protocolos de atuação dos agentes,
  estrutura de camadas upstream/downstream, fluxo de aprovação, rastreabilidade e
  integração com RAG. Usado pelo @kare-orchestrator como referência de operação.
triggers:
  - "modelo operacional"
  - "como funciona o kare"
  - "protocolo de operação"
  - "camadas upstream downstream"
---

# KARE Operating Model

## Visão Geral

O **KARE-SPEC** opera como plataforma de desenvolvimento assistido por IA, cobrindo o ciclo completo de produtos e software:

```
Ideia/Demanda
      ↓
┌─────────────────────────────────────┐
│           CAMADA UPSTREAM           │
│  Discovery → PRD → Backlog → RAID   │
│  Agentes: product-discovery,        │
│  story-crafter, backlog-architect,  │
│  risk-analyst, prd-reviewer,        │
│  project-classifier, tech-decision- │
│  maker, delivery-observer           │
└─────────────────────────────────────┘
      ↓ (aprovação do usuário)
┌─────────────────────────────────────┐
│          CAMADA DOWNSTREAM          │
│  SDD: Spec → Plan → Tasks →         │
│  Implement → Converge               │
│  Agentes: code-author,              │
│  review-master, test-engineer,      │
│  quality-guardian, devops-engineer  │
└─────────────────────────────────────┘
      ↓
    PR para Produção
```

## Estrutura de Outputs

```
_outputs/<project-slug>/
├── outputs_upstream/          ← Artefatos de descoberta e planejamento
│   ├── PROJECT_CONTEXT.md
│   ├── PROJECT_BRIEF.md
│   ├── PRD.md
│   ├── BACKLOG.md
│   ├── USER_STORY_MAP.md
│   ├── RAID.md
│   ├── ADR-XXX.md
│   ├── ARCHITECTURE.md
│   ├── sprints/
│   ├── testes/
│   └── releases/
└── outputs_downstream/        ← Artefatos de especificação e implementação (SDD)
    ├── specs/                 ← O que construir
    ├── plans/                 ← Como construir
    ├── tasks/                 ← Tarefas acionáveis
    ├── implementations/       ← Código e entregas
    └── convergence/           ← Relatório spec vs entrega
```

## Protocolo de Aprovação Prévia

**REGRA INEGOCIÁVEL:** Nenhum artefato é gerado sem:

1. Apresentação do plano de execução ao usuário
2. Aprovação explícita ("de acordo", "ok", "pode gerar")

O plano deve incluir:
- Lista de artefatos
- Estrutura de cada documento
- Paths de destino
- Agentes envolvidos
- Prévia visual (quando aplicável)

## Camada Upstream — Protocolo

### Fluxo Padrão
```
/create ou /kare-flow
  → @project-classifier (GF/BF)
  → @product-discovery (Brief + PRD)
  → @prd-reviewer (gate de qualidade)
  → @backlog-architect + @risk-analyst (paralelo)
  → @tech-decision-maker (ADRs)
  → @quality-guardian (gate final)
```

### Status dos Artefatos
- Criados: `Status: ⏳ PENDENTE APROVAÇÃO`
- Aprovados: `Status: ✅ Aprovado`
- Aprovação: usuário diz "aprovo [artefato]" → atualizar + ingerir no RAG

## Camada Downstream — Modelo SDD

Baseado no **Spec-Driven Development** (github/spec-kit):

| Passo | Comando | Output |
|---|---|---|
| Especificar | `/speckit-specify` | `specs/<slug>.md` |
| Planejar | `/speckit-plan` | `plans/<slug>.md` |
| Quebrar em tasks | `/speckit-tasks` | `tasks/<slug>.md` |
| Implementar | `/speckit-implement` | `implementations/` |
| Convergir | `/speckit-converge` | `convergence/<slug>.md` |

## Memória Persistente (RAG)

O KARE-SPEC mantém 3 bancos SQLite em `.specify/rag/`:

| Banco | Conteúdo | TTL |
|---|---|---|
| `kare_perene_rag.db` | Conhecimento permanente (conceitos, sistemas, decisões) | ∞ |
| `kare_history_rag.db` | Artefatos de projeto (PRDs, ADRs, análises) | Por projeto |
| `kare_telemetry.db` | Telemetria de uso | 90 dias |

## Integração MCP

- **Jira Datacenter**: via MCP Atlassian com OAuth (quando disponível)
- **Confluence**: publicação de artefatos via `/publish-confluence`
- **Configura**: `.agent/scripts/infra/configure_mcp_atlassian.ps1`

## Governança de Agentes

| Componente | Função |
|---|---|
| Tool Guard | Restringe ferramentas por tipo de agente |
| Loop Guard | Detecta loops (max 3 retries → HITL) |
| Guardrail Gate | Autorização HITL para skills CRITICAL/HIGH |
| SQL Guard | SELECT-only para queries de dados |
| Confidence Gate | Score mínimo 0.70 para prosseguir |

## Convenções de IDs SAFe

| Tipo | Prefixo | Exemplo |
|---|---|---|
| Epic | `EP-` | `EP-001` |
| Feature | `FEAT-` | `FEAT-001` |
| Enabler | `EN-` | `EN-001` |
| User Story | `US-` | `US-001` |
| Task | `TASK-` | `TASK-001` |
| ADR | `ADR-` | `ADR-007` |

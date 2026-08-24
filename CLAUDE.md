# KARE-SPEC (KARE-PSAISS-CORE)

Solução de apoio ao desenvolvimento de produtos e software para projetos complexos — da ideia ao PR para produção.

## Agentes disponíveis

Os agentes estão em `.agent/agents/` (26 especialistas). Principais:

| Agente | Uso |
|---|---|
| `kare-orchestrator` | **Entrada obrigatória** — analisa e delega para os especialistas |
| `story-crafter` | User Stories com ACs e DoR/DoD |
| `backlog-architect` | Organização e priorização de backlog |
| `product-discovery` | PRD e discovery de produto |
| `code-author` | Implementação com TDD |
| `review-master` | Code review com quality score |
| `test-engineer` | Geração de testes automatizados |
| `risk-analyst` | Análise RAID |
| `quality-guardian` | Quality gates 0–100 |

## Regras (carregadas automaticamente)

As instruções always-on estão em `.agent/rules/`. As principais:
- `kare.instructions.md` — orquestração e protocolo de 4 fases
- `orchestration.instructions.md` — protocolo de delegação multi-agente
- `delivery-standards.instructions.md` — padrões de entrega e scripts

## Slash commands

Os workflows estão em `.agent/workflows/` e funcionam como slash commands:

```
/create       → Discovery completo (PRD + Backlog + ADRs)
/story        → User Story com ACs
/sprint       → Sprint Planning
/plan         → Project Planning
/implement    → Código com TDD
/review       → Code Review
/test         → Testes automatizados
/risk         → Análise RAID
/status       → Status Report
/kare-flow    → Fluxo E2E Produto/Software (idea → PR)
```

## Context Engine (RAG)

O KARE-SPEC tem uma base de conhecimento semântica (SQLite + BM25):

```bash
# Buscar contexto
python .agent/scripts/ai/kare_rag.py search "sua busca"

# Ingerir documento
python .agent/scripts/ai/kare_rag.py ingest --title "PRD X" --type artifact --context meu-projeto --file path/to/doc.md
```

## Modelo de atuação

O KARE-SPEC opera em duas camadas:

- **Upstream** → Discovery, PRD, Backlog, RAID, Story Map, ADRs
  - Artefatos em: `_outputs/<slug>/outputs_upstream/`
- **Downstream** → Especificação SDD, Plano, Tasks, Implementação, Convergência
  - Artefatos em: `_outputs/<slug>/outputs_downstream/`

> **Regra**: Nenhum artefato é gerado sem apresentação prévia do plano e aprovação explícita do usuário.

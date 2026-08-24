---
name: orchestration-patterns
description: >
  Meta-skill de orquestração do ecossistema KARE. Determina qual agente e skill
  ativar com base no contexto da solicitação. Roteamento automático multi-agente
  com handoff de contexto.
triggers:
  - sempre ativo como meta-roteador do ecossistema KARE
  - "/orchestrate"
---

# Orchestration Patterns Skill

## Mapa de Roteamento KARE

```
Solicitação do usuário
        │
        ▼
[1] Ler PROJECT_CONTEXT.md
        │
        ├── Não existe → [project-context] → Gera PROJECT_CONTEXT.md
        │
        ▼
[2] Classificar a solicitação
        │
        ├── Diagnóstico/Classificação → [project-classifier]
        ├── Brief/PRD → [product-discovery]
        ├── Story/AC → [story-crafter]
        ├── Backlog/Priorização → [backlog-architect]
        ├── ADR/RFC → [tech-decision-maker]
        ├── Risk → [risk-analyst]
        ├── Quality Gate → [quality-guardian]
        ├── Código → [code-author] + [test-engineer]
        ├── Review → [review-master]
        └── Monitoramento → [delivery-observer]
```

---

## Decisão de Roteamento

Para cada solicitação, o orquestrador:

1. **Detecta intent** (o que o usuário realmente precisa)
2. **Verifica pré-requisitos** (qual artefato precisa existir antes)
3. **Ativa agente(s)** primário(s) e secundário(s)
4. **Passa contexto** estruturado para cada agente
5. **Recebe output** e verifica consistência com artefatos existentes

### Intent Detection Matrix

| Palavras-chave | Intent | Agente primário | Skill(s) |
|---------------|--------|----------------|---------|
| "brief", "problema", "objetivo" | discovery | product-discovery | project-discovery |
| "PRD", "requisitos", "features" | discovery | product-discovery | project-discovery |
| "story", "como usuário", "AC" | story | story-crafter | user-story-craft |
| "backlog", "priorizar", "refinamento" | planning | backlog-architect | backlog-management |
| "ADR", "decisão técnica", "alternativas" | decision | tech-decision-maker | adr-patterns |
| "risco", "ameaça", "mitigação" | risk | risk-analyst | risk-management |
| "quality gate", "DoD", "release check" | quality | quality-guardian | quality-gates |
| "código", "implementar", "TDD" | code | code-author | code-generation-agile |
| "teste", "test plan", "cobertura" | test | test-engineer | test-artifact-generation |
| "review", "PR", "revisão" | review | review-master | review-patterns |
| "log", "métrica", "SLO", "alerta" | observability | delivery-observer | observability-patterns |
| "lean inception", "visão do produto", "mvp canvas", "sequenciador", "é não é faz não faz" | discovery | product-discovery | lean-inception |
| "design sprint", "crazy 8s", "hmw", "como poderíamos", "storyboard sprint", "sprint week" | discovery | product-discovery | design-sprint |

---

## Handoff de Contexto — Formato Padrão

Ao passar contexto de um agente para outro:

```json
{
  "session_id": "[uuid]",
  "project_type": "greenfield | brownfield | hybrid",
  "current_phase": "discovery | planning | execution | review",
  "artifacts_available": [
    "PROJECT_CONTEXT.md",
    "PROJECT_BRIEF.md",
    "PRD.md"
  ],
  "active_story": "STORY-XXX",
  "active_sprint": "Sprint N",
  "constraints": {
    "stack": "[linguagem/framework]",
    "adrs_blocking": ["ADR-001", "ADR-003"],
    "risks_open": ["RISCO-001"]
  },
  "user_intent": "[texto do pedido original]",
  "previous_agent_output": "[resumo do que o agente anterior gerou]"
}
```

---

## Multi-Agent Workflows Automáticos

Alguns workflows disparam múltiplos agentes automaticamente:

### `/gen-story` → Pipeline completo
```
1. [story-crafter] → gera story com ACs
2. [risk-analyst] → avalia riscos da story
3. [test-engineer] → gera test plan para os ACs
4. [quality-guardian] → valida DoR
```

### `/review` → Pipeline de review
```
1. [review-master] → code review completo
2. [test-engineer] → valida cobertura de testes
3. [quality-guardian] → verifica quality gate
```

### `/gen-adr` → Pipeline de decisão
```
1. [tech-decision-maker] → gera ADR com alternativas
2. [risk-analyst] → avalia riscos de cada opção
3. Atualiza ADR_INDEX.md
```

---

## Fallback de Roteamento

Se a intent não for detectada claramente:

```
1. Apresenta as 3 intenções mais prováveis com sua classificação
2. Aguarda confirmação do usuário (1 pergunta única)
3. Executa após resposta
```

Exemplo:
```
Detectei seu pedido pode ser:
a) Gerar uma nova user story (STORY-XXX)
b) Refinar a story STORY-XXX existente
c) Gerar critérios de aceite para feature F-XX do PRD

Qual é o objetivo?
```

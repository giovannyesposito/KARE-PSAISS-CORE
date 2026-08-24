---
description: "Gera checklist estruturado de prontidão, qualidade ou aceite para discovery, feature, story, sprint, release ou governança"
---

# /checklist Workflow

## O que faz
Cria checklists objetivos para validar se um escopo está pronto para avançar
em discovery, refinamento, planejamento, implementação, teste, release ou aceite.

## Quando usar
- Para validar se uma story está pronta para sprint
- Para revisar se uma feature atende critérios mínimos de qualidade
- Para preparar sprint review, release ou handoff
- Para auditorias rápidas de completude e conformidade

## O que NÃO faz
- Não substitui o `/quality` quando houver gate formal de DoD
- Não decide prioridade de backlog sozinho

## Passos

// turbo
1. Identificar o tipo de checklist solicitado

// turbo
2. Montar checklist com base no escopo:
   - discovery
   - epic / capability / feature
   - story
   - sprint
   - release
   - governança

3. Validar evidências mínimas existentes

4. Sinalizar itens em:
   - `[x]` Atendido
   - `[ ]` Pendente
   - `⚠️` Atenção

5. Recomendar próximos passos para fechar pendências

## Uso

```text
/checklist [escopo]
/checklist --story US-42
/checklist --feature FEAT-07
/checklist --sprint 3
/checklist --release v2.0.0
```

## Saídas Esperadas
- Checklist em Markdown
- Pendências e evidências faltantes
- Critérios mínimos para avanço
- Recomendação de próximos comandos (`/quality`, `/risk`, `/review`, `/release`)

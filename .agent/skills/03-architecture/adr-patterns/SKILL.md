---
name: adr-patterns
description: >
  Geração e manutenção de Architecture Decision Records (ADRs) e RFCs.
  Detecta decisões implícitas no código ou conversas, gera ADR preenchido
  proativamente, mantém índice e rastreia status.
triggers:
  - "ADR"
  - "architecture decision"
  - "decisão técnica"
  - "RFC"
  - "/gen-adr"
---

# ADR Patterns Skill

## Protocolo de Geração (Proativo)

Antes de criar um ADR:
1. Scan de ADRs existentes → verifica se decisão já foi documentada
2. Scan de `PROJECT_CONTEXT.md` e `PRD.md` → infere contexto técnico
3. Detecta dependências com outros ADRs
4. Gera ADR completo com alternativas e consequências

---

## Template ADR — ADR_NNN_titulo.md

```markdown
# ADR-NNN — [Título descritivo da decisão]

**Status**: [Aguardando aprovação] | Accepted | Deprecated | Superseded by ADR-XXX
**Data**: [YYYY-MM-DD]
**Autores**: [times/pessoas envolvidas]
**Revisores**: [quem deve aprovar]

---

## Contexto

[Situação que motivou a necessidade de decisão. Forças em jogo.
Por que precisamos decidir isso agora? Qual é o problema a resolver?]

## Problema

[Enunciado claro e objetivo da decisão a ser tomada, em forma de pergunta ou afirmação]

## Opções Consideradas

### Opção A — [Nome]
**Descrição**: [como funciona]
**Pros**:
- ...
**Cons**:
- ...
**Custo estimado de implementação**: Baixo | Médio | Alto

### Opção B — [Nome]
[mesmo formato]

### Opção C — Não fazer nada
**Descrição**: Manter o status atual
**Pros**: zero custo imediato
**Cons**: [problemas que continuarão existindo]

---

## Sugestão Mais Assertiva

**Escolhemos a Opção [X]** porque [justificativa baseada nos critérios mais importantes].

Critérios de decisão que pesaram:
1. [Critério 1 — por que foi decisivo]
2. [Critério 2]

---

## Consequências

### Positivas
- [Benefício técnico ou de negócio]

### Negativas / Trade-offs
- [O que abrimos mão]

### Ações de mitigação
- [Como endereçar os trade-offs]

---

## Rastreabilidade
- **PRD relacionado**: [seção]
- **Stories impactadas**: STORY-XXX, STORY-XXX
- **ADRs relacionados**: ADR-XXX (depende de), ADR-XXX (supera)
- **Revisão prevista**: [quando revisitar — sprint, data ou gatilho]

---
⚠️ Itens para Validação
[PRECISA_VALIDAR: ...]
```

---

## Índice de ADRs — ADR_INDEX.md

```markdown
# ADR Index

| # | Título | Status | Data | Área |
|---|--------|--------|------|------|
| ADR-001 | Escolha de banco de dados | Accepted | 2024-01 | Data |
| ADR-002 | Estratégia de autenticação | Accepted | 2024-02 | Auth |
| ADR-003 | Padrão de mensageria | Proposed | 2024-03 | Infra |
```

---

## Status dos ADRs

| Status | Significado |
|--------|------------|
| `Proposed` | Em discussão, aguardando aprovação |
| `Accepted` | Decisão tomada e em vigor |
| `Deprecated` | Ainda vigente, mas considerar substituição |
| `Superseded` | Substituído por ADR-NNN |

---

## Detecção Proativa de Decisões Implícitas

O agente deve identificar e propor ADRs quando detectar:

```
→ Novo framework ou biblioteca sendo adicionado
→ Pattern arquitetural novo sendo introduzido
→ Mudança de banco, mensageria ou infra
→ Trade-off técnico sendo discutido sem estar documentado
→ Story com notas técnicas que implica decisão de design
```

Em cada caso: "Detectei uma decisão técnica implícita. Devo criar ADR-NNN para documentar?"

---

## RFC Template (Request for Comments)

Para decisões que precisam de discussão ampla antes de virar ADR:

```markdown
# RFC-NNN — [Título]

**Autor**: [nome]
**Data de abertura**: [data]
**Prazo de comentários**: [data]
**Status**: Open | In-Review | Closed

## Motivação
[Por que estamos propondo isso]

## Proposta Detalhada
[O que exatamente está sendo proposto, com exemplos]

## Alternativas Descartadas
[O que foi considerado e por que não]

## Perguntas Abertas
- [Dúvida atual que precisa de input]

## Comentários
[Seção viva — atualizada durante o processo de revisão]
```

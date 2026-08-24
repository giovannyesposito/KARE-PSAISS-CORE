---
name: user-story-craft
description: >
  Geração de User Stories, Epics e Features nos formatos corretos.
  Suporta Gherkin AC, INVEST checklist, DoR/DoD validação e detecção
  de stories vazias ou ambíguas. Protocolo proativo: lê PRD e gera rascunho sem esperar.
triggers:
  - "user story"
  - "story"
  - "épico"
  - "epic"
  - "gherkin"
  - "critério de aceite"
  - "AC"
  - "DoR"
  - "DoD"
  - "/gen-story"
---

# User Story Craft Skill

## Protocolo de Geração (Proativo)

Antes de gerar qualquer story:
1. Lê `PRD.md` → extrai feature e persona relevantes
2. Lê stories existentes → evita duplicação, mantém numeração sequencial
3. Lê `PROJECT_CONTEXT.md` → ajusta complexidade para BF ou GF
4. Gera story completa com todos os campos preenchidos
5. Valida INVEST e DoR automaticamente

---

## Formatos Suportados

### Standard User Story

```markdown
# [STORY-XXX] — [Título curto e descritivo]

**Como** [persona],
**Quero** [ação/objetivo],
**Para que** [valor/benefício].

<!-- Feature: F-XX | Epic: EPIC-XX | Sprint: [atual] -->

## Critérios de Aceite (Gherkin)

### Cenário 1 — Happy Path
**Dado que** [pré-condição]
**Quando** [ação do usuário]
**Então** [resultado esperado]
**E** [resultado adicional se necessário]

### Cenário 2 — Unhappy Path / Edge Case
**Dado que** [condição de falha]
**Quando** [ação]
**Então** [comportamento esperado de erro]

## Notas Técnicas
- [Decisões de implementação relevantes]
- [Integrações com outros sistemas]
- [ADRs aplicáveis: ADR-XXX]

## Definition of Ready (DoR) ✅
- [ ] Story escrita no formato correto
- [ ] Critérios de aceite definidos e testáveis
- [ ] Dependências identificadas
- [ ] Estimada pelo time
- [ ] Sem ambiguidades bloqueantes

## Definition of Done (DoD) ✅
- [ ] Código implementado e revisado
- [ ] Testes unitários e de integração passando
- [ ] Critérios de aceite validados (incluindo unhappy paths)
- [ ] Documentação atualizada
- [ ] Deploy em staging testado

## INVEST Checklist
- **I**ndependent: [ ] — pode ser entregue isoladamente?
- **N**egotiable: [ ] — escopo pode ser ajustado?
- **V**aluable: [ ] — entrega valor ao usuário/negócio?
- **E**stimable: [ ] — pode ser estimada?
- **S**mall: [ ] — cabe em 1 sprint?
- **T**estable: [ ] — tem ACs verificáveis?

---
⚠️ Itens para Validação
[PRECISA_VALIDAR: ...]
```

---

## Tipos de Story

| Tipo | Quando usar | Marcação |
|------|-------------|---------|
| **Funcional** | Feature de produto padrão | `[STORY-XXX]` |
| **Técnica** | Refactor, infra, dívida técnica | `[TECH-XXX]` |
| **Spike** | Investigação, PoC, pesquisa | `[SPIKE-XXX]` |
| **Bug** | Correção de defeito | `[BUG-XXX]` |

---

## Detecção de Problemas (Automática)

O agente DEVE detectar e sinalizar:

```
⚠️ Story sem unhappy path → adiciona cenário de erro como [PRECISA_VALIDAR]
⚠️ Story sem notas técnicas → adiciona seção com [PRECISA_VALIDAR]
⚠️ INVEST falhou em "S" (muito grande) → sugere split com proposta de sub-stories
⚠️ AC não testável → reescreve com critério mensurável e sinaliza diferença
⚠️ Duplicação com story existente → aponta STORY-XXX existente
```

---

## Epic Template

```markdown
# [EPIC-XX] — [Título]

**Objetivo**: [problema de negócio que resolve]
**Persona principal**: [persona do PRD]
**Feature derivada**: [F-XX do PRD]
**Critério de conclusão**: [quando o épico está feito]

## Stories
- [ ] STORY-001 — [título]
- [ ] STORY-002 — [título]
- [ ] TECH-001 — [título]

## Métricas de Sucesso
| Métrica | Before | Target |
|---------|--------|--------|
| | | |
```

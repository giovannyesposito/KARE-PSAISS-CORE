---
name: risk-management
description: >
  Identificação, avaliação e mitigação de riscos de produto, técnicos
  e de negócio. Gera RISK_REGISTER.md versionado, aplica matriz de
  probabilidade × impacto e monitora status dos riscos por sprint.
triggers:
  - "risco"
  - "risk"
  - "risk register"
  - "matriz de risco"
  - "mitigação"
  - "/gen-risk"
---

# Risk Management Skill

## Protocolo de Identificação (Proativo)

Ao ser ativado, o agente escaneia:
1. `PRD.md` — dependências externas, integrações, requisitos de compliance
2. Stories abertas — complexidade técnica, novidade de tecnologia
3. `PROJECT_CONTEXT.md` — score de dívida técnica, tipo BF/GF
4. Histórico de ADRs — decisões com trade-offs negativos explícitos
5. Calendário do sprint — feriados, férias, datas de release

---

## Categorias de Risco

| Categoria | Exemplos |
|-----------|---------|
| **TECH** | dívida técnica, novidade de tecnologia, performance |
| **DEP** | dependências externas, APIs de terceiros, times |
| **SCOPE** | creep de escopo, requisitos ambíguos, gold plating |
| **PEOPLE** | turnover, single point of knowledge, disponibilidade |
| **MARKET** | mudança de prioridade, concorrência, feedback de usuário |
| **COMPLIANCE** | LGPD, GDPR, regulatório, auditoria |
| **INFRA** | cloud, capacidade, segurança, SLA de providers |

---

## Matriz de Avaliação

```
Impacto  │  Baixo (1)  │  Médio (2)  │  Alto (3)  │  Crítico (4)
─────────┼─────────────┼─────────────┼────────────┼─────────────
Provável │     2       │      4      │     6      │      8
(2)      │   Monitor   │   Planejar  │  Mitigar   │  URGENTE
─────────┼─────────────┼─────────────┼────────────┼─────────────
Possível │     1.5     │      3      │     4.5    │      6
(1.5)    │   Aceitar   │   Monitor   │  Planejar  │  Mitigar
─────────┼─────────────┼─────────────┼────────────┼─────────────
Improvável│    1       │      2      │     3      │      4
(1)      │   Aceitar   │   Aceitar   │  Monitor   │  Planejar
```

**Score = Probabilidade × Impacto**
- 6+: Mitigar proativamente (bloqueante de release)
- 3-5: Planejar mitigação (previsto no sprint)
- 1-2: Monitorar ou aceitar

---

## Template — RISK_REGISTER.md

```markdown
# Risk Register — [Produto]
<!-- DRAFT v1 | Atualizado: [data] -->

## Visão Geral
- **Riscos críticos**: [n]
- **Itens sem dono**: [n]
- **Revisão pendente**: [data próxima revisão]

---

## RISCO-001 — [Título curto]

| Campo | Valor |
|-------|-------|
| **ID** | RISCO-001 |
| **Categoria** | TECH / DEP / SCOPE / ... |
| **Score** | [probabilidade × impacto] |
| **Probabilidade** | Improvável / Possível / Provável |
| **Impacto** | Baixo / Médio / Alto / Crítico |
| **Status** | Open / Mitigating / Closed / Accepted |
| **Dono** | [nome ou papel] |
| **Detectado em** | [sprint ou data] |

**Descrição**:
[O que pode acontecer de errado e por que]

**Gatilhos** (early warning):
- [Sinal de que o risco está se materializando]

**Plano de mitigação**:
- [Ação preventiva 1]
- [Ação preventiva 2]

**Plano de contingência** (se materializar):
- [O que fazer se acontecer]

**Rastreabilidade**:
- Stories impactadas: STORY-XXX
- ADR relacionado: ADR-XXX

---
```

---

## Gatilhos de Revisão de Riscos

O risk register DEVE ser revisado:
- [ ] Início de cada sprint (planejamento)
- [ ] Após mudança de escopo no PRD
- [ ] Ao fechar um ADR (novos trade-offs)
- [ ] Ao detectar score de dívida técnica >20
- [ ] Ao integrar com novo sistema externo

---

## Métricas de Risco

```markdown
## Risk Metrics (sprint atual)

| Métrica | Valor |
|---------|-------|
| Riscos abertos | [n] |
| Riscos críticos (score ≥6) | [n] |
| Riscos sem dono | [n] |
| Riscos mitigados este sprint | [n] |
| MTTR de riscos materializados | [dias] |
```

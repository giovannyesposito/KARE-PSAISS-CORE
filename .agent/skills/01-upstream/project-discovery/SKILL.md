---
name: project-discovery
description: >
  Geração de Project Brief e PRD profissionais. Produz artefatos prontos
  para commit com rastreabilidade Brief → PRD → Épicos → Stories.
  Segue protocolo proativo: escaneia contexto e gera rascunho imediatamente.
triggers:
  - "project brief"
  - "PRD"
  - "product requirements"
  - "requisitos de produto"
  - "/gen-brief"
  - "/gen-prd"
---

# Project Discovery Skill

## Project Brief

### Template — PROJECT_BRIEF.md

```markdown
# Project Brief — [Nome do Projeto]
<!-- DRAFT v1 -->

## Problem Statement
[O problema central que este projeto resolve, com dados quantitativos quando possível]

## Contexto
[Situação atual, por que isso é prioritário agora]

## Objetivos (SMART)
- **O1**: [Específico, Mensurável, Atingível, Relevante, Temporal]
- **O2**: ...

## Stakeholders
| Papel | Nome/Grupo | Interesse | Influência |
|-------|-----------|-----------|-----------|
| Sponsor | | | Alta |
| Product Owner | | | Alta |
| Tech Lead | | | Média |
| Usuários finais | | | Média |

## Constraints
- **Técnicas**: [stack, integrações obrigatórias]
- **Negócio**: [budget, prazo, regulatório]
- **Time**: [capacidade, skills disponíveis]

## Success Metrics
| Métrica | Baseline | Target | Prazo |
|---------|----------|--------|-------|
| | | | |

## Out-of-Scope (Explícito)
- [Item 1 — fora do escopo desta iniciativa]

## Riscos Iniciais
| Risco | Probabilidade | Impacto | Mitigação inicial |
|-------|-------------|---------|------------------|
| | | | |

---
⚠️ Itens para Validação
[PRECISA_VALIDAR: ...]
```

---

## PRD

### Template — PRD.md

```markdown
# PRD — [Nome do Produto/Feature]
<!-- DRAFT v1 -->
**Versão**: 1.0 | **Status**: Draft | **Autor**: KARE AI

## Resumo Executivo
[2-3 linhas descrevendo o que será construído e por quê]

## Personas

### [Persona 1 — Nome]
- **Papel**: [cargo/função]
- **Objetivos**: [o que quer alcançar]
- **Dores**: [frustrações atuais]
- **Comportamentos**: [como usa o produto hoje]

## User Journeys
[Descrever os fluxos principais por persona]

## Features Priorizadas
| # | Feature | Valor | Esforço | Prioridade | Persona |
|---|---------|-------|---------|-----------|---------|
| F1 | | Alto/Médio/Baixo | P/M/G | Must/Should/Could | |

## Requisitos Funcionais
- **RF01**: [descrição detalhada]
- **RF02**: ...

## Requisitos Não-Funcionais
- **Performance**: [SLA esperado]
- **Segurança**: [requisitos de autenticação, autorização, dados]
- **Disponibilidade**: [uptime target]
- **Escalabilidade**: [carga esperada]

## Critérios de Aceite de Produto
- [ ] [Critério mensurável de sucesso do produto]

## Out-of-Scope (Explícito)
- [Item claramente fora do escopo]

## Dependências
- **Internas**: [times, sistemas]
- **Externas**: [APIs, fornecedores]

## Rastreabilidade
- Brief: [link/referência]
- Épicos derivados: EPIC_001, EPIC_002

---
⚠️ Itens para Validação
[PRECISA_VALIDAR: ...]

🔍 Inconsistências Detectadas
[INCONSISTÊNCIA_DETECTADA: ...]
```

---

## Regras de Geração

1. **Brief**: scan de contexto → gera em 1 passagem, marca gaps como `[PRECISA_VALIDAR]`
2. **PRD**: lê Brief existente → expande features → nunca contradiz Brief sem sinalizar
3. **Rastreabilidade**: toda seção do PRD referencia o objetivo do Brief que originou
4. **Versionamento**: cada revisão increments `v1 → v2 → ...` no comentário DRAFT
5. **Out-of-Scope explícito**: é mandatório — produto sem out-of-scope é produto sem foco

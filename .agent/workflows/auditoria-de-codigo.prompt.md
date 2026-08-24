---
description: "Auditoria completa de codebase — arqueologia, padrões, convenções, cobertura de testes, tecnologias e métricas."
category: "Quality"
command: "/auditoria-de-codigo"
disclaimer: "🔬 Análise profunda de codebase em 4 dimensões paralelas. Não altera código — apenas lê e reporta. Tempo: 5-15 min dependendo do tamanho do repo."
---

# /auditoria-de-codigo Workflow

## O que faz

Executa um **audit completo de codebase** orquestrando 4 agentes em paralelo,
cada um com uma dimensão de análise distinta. O resultado é um relatório
consolidado (`SLICE_REPORT.md`) com diagnóstico técnico completo.

## Dimensões de Análise

| Dimensão | Agente | Foco |
|---|---|---|
| **Arqueologia** | `@code-archaeologist` | O que é, tecnologias, métricas, padrões legados |
| **Arquitetura & Convenções** | `@review-master` | Padrões arquiteturais, aderência a ADRs, SOLID, clean code |
| **Cobertura de Testes** | `@test-engineer` | Camadas de teste existentes, gaps, coverage estimada |
| **Quality Gate** | `@quality-guardian` | DoD check: lint, documentação, vulnerabilidades críticas |

## Passos

// turbo
1. **Identificar escopo**
   - Alvo: repositório, módulo, pasta ou arquivo informado pelo usuário
   - Se não informado: usar diretório atual do workspace
   - Verificar se há `PROJECT_CONTEXT.md` ou ADRs disponíveis para contextualizar

// turbo
2. **Fase 0 — Context Check** (orchestrator)
   - Ler `PROJECT_CONTEXT.md` (se existir)
   - Ler ADRs em `_outputs/<context_slug>/arq/` (se existir)
   - Determinar trilha: BF (Backend-First) ou GF (Generic/Frontend)

3. **Fase 1 — Execução Paralela** (4 agentes simultâneos)

   ### 3a. `@code-archaeologist` — Relatório Arqueológico
   - Identificar tecnologias e versões envolvidas
   - Estimar "idade" do código (sintaxe, padrões usados)
   - Mapear dependências, entrada/saída, side effects
   - Detectar: estado global mutável, números mágicos, acoplamento forte
   - Quantificar: linhas de código, classes, funções, flags/feature-toggles, TODOs
   - Complexidade ciclomática de funções críticas

   ### 3b. `@review-master` — Análise Arquitetural & Convenções
   - Padrões arquiteturais identificados (MVC, Hexagonal, CQRS, etc.)
   - Aderência a SOLID, DRY, KISS
   - Violações de convenção de código (naming, estrutura de pastas, imports)
   - Acoplamento e coesão entre módulos
   - Se ADRs presentes: checar aderência às decisões registradas

   ### 3c. `@test-engineer` — Mapeamento de Cobertura de Testes
   - Camadas de teste presentes: unitário, integração, E2E, regressão
   - Ferramentas de teste identificadas (Jest, Pytest, Cypress, etc.)
   - Estimativa de coverage atual
   - Gaps críticos: funções/módulos sem nenhum teste
   - Test Coverage Matrix: módulo × tipo de teste × status

   ### 3d. `@quality-guardian` — Quality Gate
   - Verificar presença de lint config (`.eslintrc`, `pyproject.toml`, etc.)
   - Warnings de lint detectáveis estaticamente
   - Documentação: README, JSDoc, docstrings presentes?
   - Secrets ou credenciais hardcoded (flag imediata)
   - DoD parcial: o que estaria aprovado vs. bloqueado hoje

4. **Fase 2 — Consolidação** (orchestrator)
   - Integrar os 4 relatórios
   - Detectar conflitos ou redundâncias
   - Priorizar achados por impacto: CRÍTICO → ALTO → MÉDIO → BAIXO
   - Se `@code-archaeologist` detectar riscos de segurança → acionar `@security-auditor`
   - Se `@code-archaeologist` detectar gargalos de performance → acionar `@performance-optimizer`

5. **Gerar `SLICE_REPORT.md`** com estrutura padronizada (ver abaixo)

## Uso

```
/auditoria-de-codigo
/auditoria-de-codigo src/services/
/auditoria-de-codigo --module pagamentos
/auditoria-de-codigo --security           (inclui @security-auditor)
/auditoria-de-codigo --perf               (inclui @performance-optimizer)
/auditoria-de-codigo --full               (todos os agentes secundários)
```

## Saídas Esperadas

```
SLICE_REPORT.md
  ├── 🏺 Seção 1: Relatório Arqueológico (tecnologias, métricas, padrões)
  ├── 🏗  Seção 2: Arquitetura & Convenções (padrões, violações, ADR check)
  ├── 🧪 Seção 3: Cobertura de Testes (Test Coverage Matrix, gaps)
  ├── ✅ Seção 4: Quality Gate (DoD parcial, lint, docs, secrets)
  └── 📊 Seção 5: Sumário Executivo (priorização de ações)
```

## Formato de Saída — `SLICE_REPORT.md`

```markdown
# SLICE Report — [Alvo/Módulo]
> **Data:** [data] | **Scope:** [diretório/módulo] | **Trilha:** BF/GF

---

## 🏺 1. Relatório Arqueológico

### Tecnologias Identificadas
| Tecnologia | Versão | Uso |
|---|---|---|

### Métricas
| Métrica | Valor |
|---|---|
| Linhas de código | XXX |
| Classes/Módulos | XXX |
| Funções/Métodos | XXX |
| Feature Flags | XXX |
| TODOs/HACKs | XXX |
| Complexidade máxima (McCabe) | XXX |

### Fatores de Risco
- [ ] Estado global mutável
- [ ] Números mágicos
- [ ] Acoplamento forte com [Módulo X]

---

## 🏗 2. Arquitetura & Convenções

### Padrão Arquitetural Detectado
[...]

### Violações Identificadas
| Severidade | Arquivo | Problema |
|---|---|---|
| BLOCKER | ... | ... |

### Aderência a ADRs
[...ou "Nenhum ADR encontrado para comparar"]

---

## 🧪 3. Cobertura de Testes

### Camadas Presentes
- [ ] Unitário — [ferramenta]
- [ ] Integração — [ferramenta]
- [ ] E2E — [ferramenta]
- [ ] Regressão — [ferramenta]

### Test Coverage Matrix
| Módulo | Unit | Integration | E2E | Coverage Est. |
|---|---|---|---|---|

### Gaps Críticos
[Módulos/funções sem nenhum teste]

---

## ✅ 4. Quality Gate

| Check | Status | Detalhe |
|---|---|---|
| Lint config presente | ✅/❌ | |
| README documentado | ✅/❌ | |
| Secrets hardcoded | ✅/❌ | |
| Coverage ≥ 80% | ✅/⚠️/❌ | |

---

## 📊 5. Sumário Executivo

### Ações Prioritárias
1. [CRÍTICO] ...
2. [ALTO] ...
3. [MÉDIO] ...

### Score Geral
| Dimensão | Score |
|---|---|
| Arquitetura | X/10 |
| Testes | X/10 |
| Qualidade | X/10 |
| Documentação | X/10 |
| **TOTAL** | **X/40** |
```

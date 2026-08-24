---
description: "Guia interativo de workflows KARE — Selecione um comando abaixo para ver disclaimer e guia de uso"
---

# 🎯 KARE Workflows — Placeholders de Disclaimer

Quando você seleciona um comando slash (`/`), este guia oferece **disclaimer, descrição e guia de uso** para cada um.

---

## 📋 Tabela de Comandos com Disclaimers

### 🔵 DISCOVERY & PLANNING

#### `/create` — Discovery Completo
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este comando EXECUTA o fluxo completo de descoberta de produto.
Requer entrada inicial (canvas, documento ou PPT).
TEMPO ESTIMADO: 10-20 minutos
SAÍDAS: PROJECT_CONTEXT.md, PRD.md, BACKLOG.md, RAID.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Classifica tipo de projeto
  ✓ Gera Brief executivo
  ✓ Produz PRD detalhado
  ✓ Popula backlog inicial
  ✓ Mapeia riscos (RAID)

📌 Como usar:
  /create [descrição da demanda]
  /create --ppt arquivo.pptx
  /create --context uploads/meu-projeto/

⚠️ Pré-requisitos:
  ✓ Contexto ou canvas inicial disponível
  ✓ Descrição clara da demanda
  ✓ Stakeholders identificados
```

#### `/plan` — Plano de Projeto
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 IMPORTANTE: Este comando APENAS PLANEJA — NÃO ESCREVE CÓDIGO
Gera arquivo PLAN-{task-slug}.md com breakdown de tarefas
Para codificar, use /implement depois
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Questiona escopo via Socratic Gate
  ✓ Quebra projeto em fases
  ✓ Define cronograma
  ✓ Identifica dependências
  ✓ Mapeia pré-requisitos

📌 Como usar:
  /plan [descrição do projeto]
  /plan --complexity high
  /plan --phases 4

⏱️ TEMPO: 2-3 minutos
📁 SAÍDA: docs/PLAN-{task-slug}.md
```

---

### 📝 BACKLOG & STORIES

#### `/story` — Story + ACs + DoR
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cria stories formatadas com critérios de aceitação em Gherkin
Valida Definition of Ready (DoR) automaticamente
Gera casos de teste + análise de risco
NÃO substitui planejamento de sprint — use /sprint para isso
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Cria story formatada (Como... quero... para...)
  ✓ Gera ACs em Gherkin Given/When/Then
  ✓ Preenche DoR checklist
  ✓ Gera casos de teste
  ✓ Mapeia riscos da story

📌 Como usar:
  /story [descrição]
  /story --epic EP-03 [descrição]
  /story --feature FEAT-07 [descrição]
  /story --refine US-XXX
  /story --review [para refinamento INVEST]

⏱️ TEMPO: 3-5 minutos
📁 SAÍDAS: User Story + ACs + DoR + Casos de teste
```

#### `/sprint` — Sprint Planning
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Planeja sprint completa com priorização e validação de DoR
Requer backlog existente e capacidade do time
Analisa riscos e capacidade vs comprometimento
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Prioriza backlog por valor
  ✓ Define Sprint Goal
  ✓ Valida DoR de cada story
  ✓ Distribui capacidade do time
  ✓ Mapeia riscos do sprint

📌 Como usar:
  /sprint --capacity 40
  /sprint --team-size 5
  /sprint --velocity 25
  /sprint --goal "Implementar login OAuth"

⏱️ TEMPO: 5-8 minutos
📁 SAÍDAS: SPRINT_N_PLAN.md + Sprint Goal Canvas
```

---

### 💻 DEVELOPMENT

#### `/implement` — Codificar com TDD
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Este comando ESCREVE CÓDIGO REAL!
Segue abordagem TDD (Testes Primeiro)
Requer story ID válido ou descrição técnica clara
Gera: testes + código + documentação
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Escreve testes unitários primeiro (TDD)
  ✓ Implementa código-fonte
  ✓ Gera documentação técnica
  ✓ Cria pull request draft
  ✓ Valida cobertura de testes

📌 Como usar:
  /implement --story US-XXX
  /implement [descrição técnica]
  /implement --file src/components/Button.tsx

⏱️ TEMPO: 10-30 minutos (complexidade variável)
📁 SAÍDAS: Código + Testes + Documentação + PR draft
```

#### `/test` — Gerar Testes
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cria suíte de testes completa: unitários + integração + E2E
Calcula cobertura esperada
Requer código-fonte ou story ID existente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Gera casos de teste (unit)
  ✓ Cria testes de integração
  ✓ Define testes E2E
  ✓ Calcula relatório de cobertura
  ✓ Gera scripts de CI/CD

📌 Como usar:
  /test [arquivo.ts]
  /test --story US-XXX
  /test --coverage-target 80
  /test --e2e

⏱️ TEMPO: 5-10 minutos
📁 SAÍDAS: Casos de teste + Relatório de cobertura
```

---

### 🔍 QUALITY & REVIEW

#### `/review` — Code Review
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revisa código contra checklist KARE de qualidade
Valida INVEST, SOLID e padrões de projeto
NÃO aprova automaticamente — gera relatório com sugestões
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Valida qualidade de código
  ✓ Verifica cobertura de testes
  ✓ Confirma documentação
  ✓ Valida INVEST e SOLID
  ✓ Retorna score de qualidade

📌 Como usar:
  /review [arquivo ou PR link]
  /review --strict
  /review --coverage-min 80

⏱️ TEMPO: 3-5 minutos por arquivo
📁 SAÍDA: Relatório de review + Sugestões
```

#### `/clarificar` — Refinar Requisitos
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Identifica ambiguidades e lacunas em requisitos
Faz perguntas estruturadas para refinamento
NÃO executa implementação — apenas identifica gaps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Identifica gaps de requisitos
  ✓ Faz perguntas INVEST
  ✓ Valida DoR parcial
  ✓ Mapeia ambiguidades
  ✓ Retorna checklist de refinamento

📌 Como usar:
  /clarificar [requisito ambíguo]
  /clarificar --story US-XXX
  /clarificar --depth deep

⏱️ TEMPO: 2-3 minutos
📁 SAÍDA: Lista de perguntas + Gaps identificados
```

#### `/analisar` — Validar Consistência
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Valida coerência entre documentos: PRD ↔ Backlog ↔ Código ↔ Testes
Identifica inconsistências
NÃO modifica automaticamente — apenas recomenda
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Compara PRD vs Backlog
  ✓ Valida Backlog vs Código
  ✓ Verifica Código vs Testes
  ✓ Identifica inconsistências
  ✓ Retorna recomendações

📌 Como usar:
  /analisar
  /analisar --depth medium
  /analisar --strict

⏱️ TEMPO: 3-5 minutos
📁 SAÍDA: Relatório de consistência
```

---

### ⚠️ RISK & MONITORING

#### `/risk` — Análise de Risco (RAID)
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monta análise de risco completa por slice/sprint/épico
Utiliza matriz impacto × probabilidade
Recomenda planos de mitigação
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Mapeia riscos técnicos + negócio
  ✓ Calcula matriz impacto/prob
  ✓ Prioriza riscos
  ✓ Propõe planos de mitigação
  ✓ Gera RAID completo

📌 Como usar:
  /risk --sprint N
  /risk --release R
  /risk --epic EP-XX
  /risk --severity high

⏱️ TEMPO: 3-5 minutos
📁 SAÍDA: RAID.md + Matriz de risco + Planos de mitigação
```

#### `/status` — Relatório de Status
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Consolida status com dados atuais (Jira, Linear ou memória local)
Requer integração MCP ativa
Retorna burn-down, velocidade e bloqueadores
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Consolida status do projeto
  ✓ Gera burn-down chart
  ✓ Calcula velocidade
  ✓ Lista bloqueadores
  ✓ Retorna relatório executivo

📌 Como usar:
  /status
  /status --sprint N
  /status --detailed
  /status --output PDF

⏱️ TEMPO: 1-2 minutos
📁 SAÍDA: Relatório executivo + Métricas
```

---

### 🚀 DEPLOYMENT & RELEASE

#### `/deploy` — Deploy para Staging/Prod
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Este comando PREPARA E PODE EXECUTAR DEPLOY!
Valida pré-requisitos (testes, documentação)
REQUER CONFIRMAÇÃO EXPLÍCITA para produção
Gera checklist go-live e rollback plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Valida pré-requisitos
  ✓ Executa testes pré-deploy
  ✓ Gera checklist go-live
  ✓ Executa deploy (com confirmação)
  ✓ Gera rollback plan

📌 Como usar:
  /deploy --env staging
  /deploy --env production --confirm
  /deploy --dry-run

⏱️ TEMPO: 5-20 minutos
📁 SAÍDAS: Logs de deploy + Checklist + Rollback plan
```

#### `/release` — Release Management
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerencia release end-to-end: versão, notas, tags, notificações
Integra com Jira/GitHub
Requer versão alvo clara (X.Y.Z)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Atualiza versão (semver)
  ✓ Gera release notes
  ✓ Cria tags Git
  ✓ Notifica stakeholders
  ✓ Integra com Jira/GitHub

📌 Como usar:
  /release --version 1.2.0
  /release --auto-patch
  /release --notify-team

⏱️ TEMPO: 5-10 minutos
📁 SAÍDAS: Release notes + Tags + Notificações
```

---

### 🐛 DEBUG & TROUBLESHOOTING

#### `/debug` — Diagnóstico
```
🎬 DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Executa diagnóstico interativo de problemas
Examina logs, traces, dependências
PODE fazer chamadas remotas a APIs
Requer descrição clara dos sintomas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Coleta logs e traces
  ✓ Valida dependências
  ✓ Executa testes diagnósticos
  ✓ Sugere correções
  ✓ Retorna checklist de correção

📌 Como usar:
  /debug [descrição do problema]
  /debug --file arquivo.ts
  /debug --api endpoint
  /debug --logs

⏱️ TEMPO: 5-15 minutos
📁 SAÍDA: Diagnóstico + Sugestões de correção
```

---

## 🎮 Como Usar Este Guia

1. **Selecione um comando:** Digite `/` no chat para ver a lista
2. **Leia o disclaimer:** Entenda o que o comando faz e pré-requisitos
3. **Copie o exemplo:** Use o formato sugerido em "Como usar"
4. **Acompanhe a execução:** Observe tempo estimado e saídas
5. **Consulte resultados:** Verifique os arquivos gerados na pasta saída

---

## 🔑 Símbolos Utilizados

| Símbolo | Significado |
|---------|------------|
| 🎬 | Seção de disclaimer/aviso importante |
| 📖 | O que o comando faz (capabilities) |
| 📌 | Como usar (exemplos de uso) |
| ⏱️ | Tempo estimado de execução |
| 📁 | Saídas e arquivos gerados |
| ⚡ | Ação crítica ou irreversível |
| 🚫 | Importante negação/restrição |
| ❓ | Requer informação adicional |
| ⚠️ | Aviso importante |

---

## 📚 Referências

- [Índice de workflows em JSON](../.agent/config/workflows-index.json)
- [Documentação de Skills KARE](../.agent/skills/)
- [Guia de UX/UI](../.agent/.shared/ui-ux-pro-max/)

---

**Última atualização:** 2026-04-19 | **Versão:** 1.0.0

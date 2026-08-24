---
applyTo: "**"
priority: "high"
loadAlways: true
---

# WORKFLOW DISCLAIMERS — Guia Interativo de Comandos

## Objetivo

Quando o usuário seleciona um comando slash (`/create`, `/story`, `/plan`, etc.), **SEMPRE** exiba o disclaimer correspondente ANTES de executar o comando. O disclaimer deve ser claro, conciso e destacar:

1. **O que o comando faz**
2. **Tempo estimado de execução**
3. **Pré-requisitos obrigatórios**
4. **Saídas esperadas**
5. **Avisos críticos** (ex: código escrito, deploy executado, etc.)

---

## Padrão de Disclaimer — Formato Visual

Cada disclaimer deve seguir este formato:

```
🎬 DISCLAIMER: [Comando]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Breve descrição do que faz — 1-2 linhas]
[Avisos críticos em ALL CAPS — se houver]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ [Capability 1]
  ✓ [Capability 2]
  ✓ [Capability N]

📌 Como usar:
  [exemplo de uso]

⏱️ TEMPO: [estimativa]
📁 SAÍDAS: [arquivos gerados]

✅ Deseja prosseguir? [Sim/Não]
```

---

## Mapeamento Comando ↔ Disclaimer

### 🔵 DISCOVERY & PLANNING

**`/lean-inception`**
```
🎬 DISCLAIMER: /lean-inception — Workshop Lean Inception Completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conduz e gera artefatos dos 5 dias da Lean Inception (Paulo Caroli).
Os templates são gerados pelo agente — o alinhamento real é feito com o time.
NÃO publica no Confluence automaticamente — use /publish-confluence depois.
⏱️ TEMPO: 15-30 minutos (completo) | 3-5 minutos (por dia/artefato)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Visão do Produto (template preenchido)
  ✓ É / Não É / Faz / Não Faz
  ✓ Objetivos do Produto com métricas
  ✓ Personas e Jornadas
  ✓ Brainstorming de Funcionalidades (clusters)
  ✓ Revisão Técnica/UX/Negócio (matriz de avaliação)
  ✓ Sequenciador em ondas (respeitando regras de Paulo Caroli)
  ✓ MVP Canvas completo (9 blocos)

📌 Como usar:
  /lean-inception [nome/descrição do produto]
  /lean-inception --dia 1 [produto]
  /lean-inception --mvp-canvas
  /lean-inception --sequenciador

📁 SAÍDAS: LEAN_INCEPTION.md, MVP Canvas, Backlog inicial

✅ Tem descrição do produto ou iniciativa? [Sim/Não]
```

**`/design-sprint`**
```
🎬 DISCLAIMER: /design-sprint — Workshop Design Sprint Completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conduz e gera artefatos dos 5 dias do Design Sprint (GV / Jake Knapp).
⚠️ O protótipo e as entrevistas são executados pelo TIME — não pelo agente.
O agente gera: Storyboard, Roteiro de entrevista e templates de síntese.
⏱️ TEMPO: 20-40 minutos (completo) | 3-8 minutos (por dia)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Mapa do Problema + HMW + Sprint Questions (Dia 1)
  ✓ Templates Crazy 8s + Solution Sketches (Dia 2)
  ✓ Dot Voting + Storyboard 8-12 quadros (Dia 3)
  ✓ Checklist de protótipo + Roteiro de entrevista (Dia 4)
  ✓ Note-taking + Síntese + Decisão PERSEVERE/ITERATE/PIVOT (Dia 5)

📌 Como usar:
  /design-sprint [desafio central]
  /design-sprint --dia 3 [desafio]
  /design-sprint --storyboard
  /design-sprint --roteiro-entrevista
  /design-sprint --3-dias [desafio]

📁 SAÍDAS: DESIGN_SPRINT.md, Storyboard, Roteiro de Teste, Síntese

✅ Qual é o desafio central do sprint? [descreva em 1 frase]
```

---

**`/create`**
```
🎬 DISCLAIMER: /create — Discovery Completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Executa fluxo COMPLETO de descoberta de produto.
REQUER entrada inicial (canvas, documento ou PPT).
⏱️ TEMPO: 10-20 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Classifica tipo de projeto
  ✓ Gera Brief executivo
  ✓ Produz PRD completo
  ✓ Popula backlog inicial
  ✓ Mapeia riscos (RAID)

📌 Como usar:
  /create [descrição da demanda]
  /create --ppt arquivo.pptx

📁 SAÍDAS: PROJECT_CONTEXT.md, PRD.md, BACKLOG.md, RAID.md

✅ Tem canvas/documento pronto? [Sim/Não]
```

**`/plan`**
```
🎬 DISCLAIMER: /plan — Project Planning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 IMPORTANTE: Este comando APENAS PLANEJA — NÃO ESCREVE CÓDIGO
Para codificar, use /implement depois.
⏱️ TEMPO: 2-3 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Questiona escopo (Socratic Gate)
  ✓ Quebra em fases
  ✓ Define cronograma
  ✓ Mapeia dependências

📌 Como usar:
  /plan [descrição do projeto]

📁 SAÍDAS: docs/PLAN-{task-slug}.md

✅ Deseja criar plano? [Sim/Não]
```

---

### 📝 BACKLOG & STORIES

**`/story`**
```
🎬 DISCLAIMER: /story — Story + ACs + DoR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cria stories formatadas com ACs em Gherkin.
Valida Definition of Ready (DoR).
NÃO substitui /sprint — use /sprint para planejamento.
⏱️ TEMPO: 3-5 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Formata story (Como... quero... para...)
  ✓ Gera ACs em Gherkin
  ✓ Preenche DoR checklist
  ✓ Gera casos de teste
  ✓ Mapeia riscos

📌 Como usar:
  /story [descrição]
  /story --epic EP-03 [descrição]
  /story --refine US-XXX

📁 SAÍDAS: Story + ACs + DoR + Casos de teste

✅ Deseja criar story? [Sim/Não]
```

**`/sprint`**
```
🎬 DISCLAIMER: /sprint — Sprint Planning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Planeja sprint COMPLETA com priorização e validação de DoR.
REQUER: backlog existente + capacidade do time.
⏱️ TEMPO: 5-8 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Prioriza backlog
  ✓ Define Sprint Goal
  ✓ Valida DoR de stories
  ✓ Distribui capacidade
  ✓ Mapeia riscos

📌 Como usar:
  /sprint --capacity 40
  /sprint --team-size 5
  /sprint --velocity 25

📁 SAÍDAS: SPRINT_N_PLAN.md + Sprint Goal

✅ Tem backlog pronto? [Sim/Não]
```

---

### 💻 DEVELOPMENT

**`/implement`**
```
🎬 DISCLAIMER: /implement — Codificar com TDD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Este comando ESCREVE CÓDIGO REAL!
Segue abordagem TDD (Testes Primeiro).
REQUER: story ID válido ou descrição técnica clara.
⏱️ TEMPO: 10-30 minutos (complexidade variável)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Escreve testes (TDD)
  ✓ Implementa código
  ✓ Gera documentação
  ✓ Cria PR draft
  ✓ Valida cobertura

📌 Como usar:
  /implement --story US-XXX
  /implement [descrição técnica]

📁 SAÍDAS: Código + Testes + Docs + PR draft

✅ Deseja implementar? [Sim/Não]
```

**`/test`**
```
🎬 DISCLAIMER: /test — Gerar Testes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cria suíte COMPLETA: unit + integração + E2E.
Calcula relatório de cobertura.
REQUER: código-fonte ou story ID.
⏱️ TEMPO: 5-10 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Testes unitários
  ✓ Testes integração
  ✓ Testes E2E
  ✓ Relatório cobertura
  ✓ Scripts CI/CD

📌 Como usar:
  /test [arquivo.ts]
  /test --story US-XXX
  /test --coverage-target 80

📁 SAÍDAS: Testes + Relatório de cobertura

✅ Qual arquivo/story? [...]
```

---

### 🔍 QUALITY & REVIEW

**`/review`**
```
🎬 DISCLAIMER: /review — Code Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revisa código contra checklist KARE.
Valida INVEST, SOLID e padrões.
NÃO aprova — gera relatório com sugestões.
⏱️ TEMPO: 3-5 minutos por arquivo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Qualidade de código
  ✓ Cobertura de testes
  ✓ Documentação
  ✓ INVEST + SOLID
  ✓ Score qualidade

📌 Como usar:
  /review [arquivo ou PR]
  /review --strict

📁 SAÍDAS: Relatório + Sugestões

✅ Qual arquivo revisar? [...]
```

**`/clarificar`**
```
🎬 DISCLAIMER: /clarificar — Refinar Requisitos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Identifica ambiguidades e lacunas.
Faz perguntas INVEST estruturadas.
NÃO executa — apenas identifica gaps.
⏱️ TEMPO: 2-3 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Identifica gaps
  ✓ Perguntas INVEST
  ✓ Valida DoR parcial
  ✓ Mapeia ambiguidades
  ✓ Checklist refinamento

📌 Como usar:
  /clarificar [requisito]
  /clarificar --story US-XXX

📁 SAÍDAS: Perguntas + Gaps

✅ Qual requisito? [...]
```

---

### ⚠️ RISK & MONITORING

**`/risk`**
```
🎬 DISCLAIMER: /risk — Análise de Risco (RAID)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monta análise COMPLETA: Risks, Assumptions, Issues, Dependencies.
Matriz impacto × probabilidade.
Planos de mitigação recomendados.
⏱️ TEMPO: 3-5 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Mapeia riscos
  ✓ Matriz impacto/prob
  ✓ Prioriza riscos
  ✓ Planos mitigação
  ✓ RAID completo

📌 Como usar:
  /risk --sprint N
  /risk --epic EP-XX

📁 SAÍDAS: RAID.md + Matriz + Planos

✅ Para qual escopo? [sprint/epic/release]
```

**`/status`**
```
🎬 DISCLAIMER: /status — Relatório de Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Consolida status com dados ATUAIS (Jira/Linear/memória).
REQUER: integração MCP ativa.
⏱️ TEMPO: 1-2 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Status consolidado
  ✓ Burn-down chart
  ✓ Velocidade
  ✓ Bloqueadores
  ✓ Relatório executivo

📌 Como usar:
  /status
  /status --sprint N
  /status --detailed

📁 SAÍDAS: Relatório + Métricas

✅ Deseja status? [Sim/Não]
```

---

### 🚀 DEPLOYMENT

**`/deploy`**
```
🎬 DISCLAIMER: /deploy — Deploy para Staging/Prod
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Este comando PREPARA E EXECUTA DEPLOY!
Valida pré-requisitos ANTES.
🔴 REQUER CONFIRMAÇÃO EXPLÍCITA para produção.
⏱️ TEMPO: 5-20 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Valida pré-requisitos
  ✓ Executa testes
  ✓ Checklist go-live
  ✓ Executa deploy
  ✓ Rollback plan

📌 Como usar:
  /deploy --env staging
  /deploy --env production --confirm
  /deploy --dry-run

📁 SAÍDAS: Logs + Checklist + Rollback

✅ Para qual ambiente? [staging/production]
```

**`/release`**
```
🎬 DISCLAIMER: /release — Release Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerencia release END-TO-END: versão, notas, tags, notificações.
Integra com Jira/GitHub.
REQUER: versão alvo clara (X.Y.Z).
⏱️ TEMPO: 5-10 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 O que faz:
  ✓ Atualiza versão
  ✓ Release notes
  ✓ Tags Git
  ✓ Notificações
  ✓ Integração Jira/GitHub

📌 Como usar:
  /release --version 1.2.0
  /release --auto-patch

📁 SAÍDAS: Release notes + Tags + Notificações

✅ Qual versão? [X.Y.Z]
```

---

## 🎯 Regras de Aplicação

1. **SEMPRE exiba o disclaimer** antes de executar qualquer comando
2. **Confirme intenção** do usuário (pergunta ao final: "Deseja prosseguir? [Sim/Não]")
3. **Se rejeitar**, retorne para sugerir comando alternativo
4. **Se aceitar**, execute normalmente e relatar progresso
5. **AVISOS CRÍTICOS** devem estar em **ALL CAPS** e destacados com `⚡` ou `🔴`

---

## 📚 Referência de Arquivos

- **JSON estruturado:** `.agent/config/workflows-index.json`
- **Guia visual completo:** `.agent/workflows/DISCLAIMERS.md`
- **Este arquivo:** `.agent/workflows/WORKFLOW-DISCLAIMERS.instructions.md`

---

**Versão:** 1.0.0 | **Data:** 2026-04-19 | **Autor:** @kare-orchestrator

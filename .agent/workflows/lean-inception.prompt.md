---
description: "Conduz e gera artefatos completos de uma Lean Inception — Visão, É/Não É, Personas, Jornada, Funcionalidades, Sequenciador e MVP Canvas"
command: /lean-inception
category: Discovery
orchestrator: kare-orchestrator
orchestrator-mode: sequential
agents-required:
   - primary: "@product-discovery"
      secondary: ["@story-crafter", "@risk-analyst", "@backlog-architect"]
context-required:
   - PROJECT_CONTEXT.md
skills-required:
   - lean-inception
disclaimer: "?? Conduz fluxo completo de Lean Inception (5 dias / Paulo Caroli). Gera todos os artefatos do workshop. Tempo: 15-30 min (completo) ou use flags por dia. Saídas: LEAN_INCEPTION.md, MVP Canvas, Backlog inicial"
---

# /lean-inception Workflow

## Apresentação do Comando (Obrigatório)

Toda vez que `/lean-inception` for evocado, exibir **imediatamente** antes de qualquer ação:

```
?? Executando: /lean-inception [argumentos]
?? O que este comando faz: Conduz e gera todos os artefatos da Lean Inception (metodologia Paulo Caroli).
?? Artefatos gerados:
  +- Visão do Produto (template preenchido)
  +- É / Não É / Faz / Não Faz
  +- Objetivos do Produto (com métricas)
  +- Personas (1 por perfil identificado)
  +- Jornadas do Usuário (1 por persona principal)
  +- Funcionalidades (brainstorming estruturado)
  +- Revisão Técnica/UX/Negócio (tabela de avaliação)
  +- Sequenciador (ondas priorizadas)
  +- MVP Canvas (consolidado)
  ? Tudo consolidado em: LEAN_INCEPTION.md
? Aguarde — iniciando orquestração...
```

## O que faz

Executa o fluxo completo da Lean Inception, gerando todos os artefatos do workshop de forma estruturada e rastreável. Pode ser executado em modo completo (todos os dias) ou parcial (um dia por vez via flags).

## O que NÃO faz

- Não substitui a facilitação humana — gera os artefatos e templates, mas o alinhamento real precisa do time
- Não executa o planejamento de sprint — use `/sprint` após ter o MVP Canvas e o Sequenciador
- Não publica no Confluence — use `/publish-confluence` separadamente

## Passos

// turbo
1. Verificar se `PROJECT_CONTEXT.md` existe e carregar contexto do projeto  
   - Se não existir: perguntar ao usuário o nome/descrição do produto antes de continuar

2. **DIA 1 — Alinhamento** (invocar `@product-discovery`)
   - Gerar template de Visão do Produto e solicitar preenchimento
   - Gerar quadrante É / Não É / Faz / Não Faz
   - Gerar Objetivos do Produto com métricas sugeridas (OKRs/KPIs)
   - Output: seção "Dia 1" do `LEAN_INCEPTION.md`

3. **DIA 2 — Pessoas** (invocar `@product-discovery` + `@story-crafter`)
   - Gerar template de Personas (mínimo 2, máximo 5)
   - Gerar template de Jornada do Usuário por persona
   - Output: seção "Dia 2" do `LEAN_INCEPTION.md`

4. **DIA 3 — Funcionalidades** (invocar `@product-discovery` + `@story-crafter`)
   - Estruturar Brainstorming de Funcionalidades em clusters
   - Aplicar tabela de Revisão Técnica/UX/Negócio (esforço × valor)
   - Classificar cada funcionalidade: Fazer / Analisar / Descartar
   - Output: seção "Dia 3" do `LEAN_INCEPTION.md`

5. **DIA 4 — Priorização** (invocar `@backlog-architect`)
   - Montar Sequenciador em ondas respeitando as 5 regras de Paulo Caroli
   - Validar que cada onda tem: =3 funcionalidades, =1 alto valor negócio, =1 alto valor UX
   - Output: seção "Dia 4" do `LEAN_INCEPTION.md`

6. **DIA 5 — MVP** (invocar `@product-discovery` + `@risk-analyst`)
   - Gerar MVP Canvas completo (9 blocos)
   - `@risk-analyst` gera riscos iniciais do MVP (top 5)
   - Output: seção "Dia 5" + MVP Canvas no `LEAN_INCEPTION.md`

7. Consolidar `LEAN_INCEPTION.md` com sumário executivo, decisões críticas e próximos passos
   - Propor próximo comando: `/story` para detalhar funcionalidades da Onda 1

## Uso

```bash
# Fluxo completo (todos os 5 dias)
/lean-inception [nome ou descrição do produto]

# Por dia específico
/lean-inception --dia 1 [produto]     # Visão, É/Não É, Objetivos
/lean-inception --dia 2 [produto]     # Personas e Jornadas
/lean-inception --dia 3 [produto]     # Funcionalidades e Revisão
/lean-inception --dia 4 [produto]     # Sequenciador
/lean-inception --dia 5 [produto]     # MVP Canvas

# Artefato específico
/lean-inception --visao               # Só Visão do Produto
/lean-inception --personas            # Só Personas
/lean-inception --sequenciador        # Só Sequenciador
/lean-inception --mvp-canvas          # Só MVP Canvas

# Com contexto existente
/lean-inception --context INI-XXX     # Usa contexto já existente no workspace
```

## Saídas Esperadas

- `LEAN_INCEPTION.md` consolidado com todos os artefatos
- Templates de cada atividade preenchidos com o contexto do produto
- Sequenciador em ondas pronto para ser usado no `/sprint`
- MVP Canvas com hipóteses de validação e métricas

## Perguntas Feitas ao Usuário (se contexto insuficiente)

- "Qual o nome do produto ou iniciativa?"
- "Quem são os usuários principais? (cargo, contexto de uso)"
- "Qual o problema central que o produto resolve?"
- "Há restrições de prazo, budget ou tecnologia?"

## Dicas de Facilitação Geradas Automaticamente

O comando gera, ao final de cada dia, uma seção `> ?? Dica para o facilitador:` com:
- Como conduzir a atividade com o time físico
- Erros comuns a evitar
- Como desempatar quando o time diverge

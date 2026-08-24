---
description: "Conduz e gera artefatos completos de um Design Sprint (GV/Jake Knapp) — HMW, Mapa, Crazy 8s, Storyboard, Protótipo e Roteiro de Teste com usuários"
command: /design-sprint
category: Discovery
orchestrator: kare-orchestrator
orchestrator-mode: sequential
agents-required:
   - primary: "@product-discovery"
      secondary: ["@ux-designer", "@risk-analyst", "@story-crafter"]
context-required:
   - PROJECT_CONTEXT.md
skills-required:
   - design-sprint
disclaimer: "?? Conduz fluxo completo de Design Sprint (5 dias / Jake Knapp / GV). Gera artefatos por dia. Tempo: 20-40 min (completo) ou use flags por dia. Saídas: DESIGN_SPRINT.md, Storyboard, Roteiro de Teste, Síntese de Aprendizados"
---

# /design-sprint Workflow

## Apresentação do Comando (Obrigatório)

Toda vez que `/design-sprint` for evocado, exibir **imediatamente** antes de qualquer ação:

```
?? Executando: /design-sprint [argumentos]
?? O que este comando faz: Conduz e gera todos os artefatos do Design Sprint (metodologia GV / Jake Knapp).
?? Artefatos gerados por dia:
  +- DIA 1 — Mapa do Problema + HMW + Sprint Questions
  +- DIA 2 — Lightning Demos (capturas) + Crazy 8s + Solution Sketches
  +- DIA 3 — Resultado do Dot Voting + Storyboard (8-12 quadros)
  +- DIA 4 — Checklist de Protótipo + Roteiro de Entrevista
  +- DIA 5 — Note-taking + Síntese + Decisão PERSEVERE/ITERATE/PIVOT
  ? Tudo consolidado em: DESIGN_SPRINT.md
?? Importante: Este comando ORIENTA e GERA TEMPLATES — a construção do protótipo e as entrevistas são executadas pelo time, não pelo agente.
? Aguarde — iniciando orquestração...
```

## O que faz

Executa o fluxo completo do Design Sprint de 5 dias, gerando artefatos estruturados para cada fase: do mapeamento do problema até a síntese dos aprendizados com usuários reais. Pode ser executado em modo completo ou dia a dia.

## O que NÃO faz

- Não constrói o protótipo — gera o Storyboard e checklist; o time constrói no Figma/slides
- Não conduz as entrevistas — gera o roteiro; o Interviewer executa com usuários reais
- Não substitui a tomada de decisão do Decisor (Decider) no Dia 3

## Passos

// turbo
1. Verificar se `PROJECT_CONTEXT.md` existe e carregar contexto  
   - Se não existir: perguntar desafio central, personas disponíveis e Long-term Goal

2. **DIA 1 — ENTENDER** (invocar `@product-discovery`)
   - Gerar template de Mapa do Problema (End-to-End Map) com etapas e atores
   - Gerar lista de HMW (Como Poderíamos) estruturadas por tema
   - Gerar Sprint Questions (principal + secundárias de risco)
   - Definir Ponto Focal (persona + etapa do mapa + HMW principal)
   - Output: seção "Dia 1" do `DESIGN_SPRINT.md`

3. **DIA 2 — ESBOÇAR** (invocar `@product-discovery` + `@ux-designer`)
   - Gerar template de captura de Lightning Demos (referências de mercado)
   - Gerar template de Crazy 8s por participante
   - Gerar template de Solution Sketch (3 telas/etapas com título e notas)
   - Output: seção "Dia 2" do `DESIGN_SPRINT.md`

4. **DIA 3 — DECIDIR** (invocar `@product-discovery` + `@risk-analyst`)
   - Gerar template de Dot Voting / Heatmap
   - Gerar Storyboard completo (8-12 quadros) baseado na solução selecionada
   - Registrar decisões de design tomadas
   - `@risk-analyst` avalia riscos das hipóteses do storyboard
   - Output: seção "Dia 3" + Storyboard no `DESIGN_SPRINT.md`

5. **DIA 4 — PROTOTIPAR** (invocar `@ux-designer`)
   - Gerar divisão de papéis sugerida (Maker, Stitcher, Writer, Asset Collector, Interviewer)
   - Gerar checklist do protótipo (baseado no Storyboard)
   - Gerar roteiro de entrevista completo (4 fases: Aquecimento, Contexto, Teste, Impressões)
   - Recomendar ferramenta de prototipação (Figma, slides, Wizard of Oz, etc.)
   - Output: seção "Dia 4" do `DESIGN_SPRINT.md`

6. **DIA 5 — TESTAR** (invocar `@product-discovery` + `@risk-analyst`)
   - Gerar template de note-taking por entrevista (5 colunas)
   - Gerar tabela de padrões consolidados (5 entrevistas × observações)
   - Gerar template de síntese com validação das Sprint Questions
   - Gerar seção de decisão: PERSEVERE / ITERATE / PIVOT com justificativa
   - Output: seção "Dia 5" + Síntese Final no `DESIGN_SPRINT.md`

7. Consolidar `DESIGN_SPRINT.md` completo com sumário, aprendizados e próximos passos
   - Se PERSEVERE: propor `/story` para criar stories a partir das funcionalidades validadas
   - Se ITERATE: propor novo `/design-sprint --dia 2` com foco ajustado
   - Se PIVOT: propor `/lean-inception` para reavaliar visão do produto

## Uso

```bash
# Fluxo completo (todos os 5 dias)
/design-sprint [descrição do desafio]

# Por dia específico
/design-sprint --dia 1 [desafio]     # Mapa + HMW + Sprint Questions
/design-sprint --dia 2 [desafio]     # Crazy 8s + Solution Sketches
/design-sprint --dia 3 [desafio]     # Voting + Storyboard
/design-sprint --dia 4 [desafio]     # Checklist + Roteiro de entrevista
/design-sprint --dia 5 [desafio]     # Note-taking + Síntese + Decisão

# Artefato específico
/design-sprint --hmw                 # Só gerar HMW a partir de um problema
/design-sprint --storyboard          # Só gerar Storyboard
/design-sprint --roteiro-entrevista  # Só gerar roteiro de teste com usuários
/design-sprint --sintese             # Só gerar template de síntese de aprendizados

# Versão comprimida (3 dias)
/design-sprint --3-dias [desafio]    # Dia1+2 comprimido ? Dia3+4 ? Dia5

# Com contexto existente
/design-sprint --context INI-XXX     # Usa contexto já existente no workspace
```

## Saídas Esperadas

- `DESIGN_SPRINT.md` consolidado com artefatos de todos os dias
- Mapa do Problema + HMWs priorizadas
- Storyboard (8-12 quadros) pronto para guiar o time no Dia 4
- Roteiro de entrevista completo (60 min por participante)
- Template de note-taking para painel de observação
- Síntese de aprendizados com tabela de padrões
- Decisão documentada: PERSEVERE / ITERATE / PIVOT

## Perguntas Feitas ao Usuário (se contexto insuficiente)

- "Qual o desafio central do sprint? (1 frase)"
- "Quem são as personas envolvidas?"
- "Qual é o Long-term Goal (visão em 2-3 anos)?"
- "Há Sprint Questions de risco já identificadas?"
- "Quem é o Decisor (Decider) do time?"

## Integração com Outros Comandos

| Resultado do Dia 5 | Próximo comando sugerido |
|-------------------|-------------------------|
| PERSEVERE | `/story` — criar stories das funcionalidades validadas |
| ITERATE | `/design-sprint --dia 2` — nova rodada de esboços |
| PIVOT | `/lean-inception --visao` — reavaliar visão do produto |
| Qualquer | `/risk` — aprofundar análise de riscos das hipóteses |

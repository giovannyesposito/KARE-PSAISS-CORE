---
name: design-sprint
description: >
  Apoio completo à condução e geração de artefatos de um Design Sprint (metodologia Google Ventures / Jake Knapp).
  Cobre as 5 fases do sprint: Entender, Esboçar, Decidir, Prototipar e Testar.
  Protocolo proativo: orienta facilitação dia a dia, gera templates de artefatos (HMW, Mapa, Storyboard,
  Plano de Teste), consolida aprendizados e recomenda próximos passos.
triggers:
  - "design sprint"
  - "design thinking"
  - "sprint de design"
  - "hmw"
  - "how might we"
  - "como poderíamos"
  - "crazy 8s"
  - "lightning demo"
  - "storyboard"
  - "mapa do problema"
  - "entrevista de usuário"
  - "protótipo de baixa fidelidade"
  - "sprint week"
  - "/design-sprint"
  - "/gen-sprint"
activation: on-demand
---

# Design Sprint Skill

> **Referência:** Design Sprint — Jake Knapp (Google Ventures), livro "Sprint"  
> **Duração típica:** 5 dias (Seg-Sex) | Pode ser adaptado para 3 dias  
> **Time ideal:** 5-7 pessoas + 1 Facilitador (Sprinter)  
> **Output final:** Protótipo testado + Aprendizados validados com usuários reais

---

## Protocolo de Atuação (Proativo)

Ao ser ativado, o agente:

1. Identifica em qual dia/fase do Design Sprint o usuário está
2. Verifica se existe `DESIGN_SPRINT.md` com contexto do desafio
3. Gera o template ou artefato solicitado para a fase atual
4. Registra decisões e aprendizados em `DESIGN_SPRINT.md`
5. Orienta o facilitador sobre a atividade seguinte

---

## Estrutura dos 5 Dias

```
DIA 1 (SEGUNDA) — ENTENDER
  └─ Lightning Talks (especialistas)
  └─ Mapa do Problema (End-to-End)
  └─ HMW (How Might We / Como Poderíamos)
  └─ Sprint Question (pergunta-alvo do sprint)

DIA 2 (TERÇA) — ESBOÇAR
  └─ Lightning Demos (referências de mercado)
  └─ Crazy 8s (8 ideias em 8 minutos)
  └─ Solution Sketch (esboço detalhado da solução)

DIA 3 (QUARTA) — DECIDIR
  └─ Art Museum (exposição dos esboços)
  └─ Dot Voting / Heatmap
  └─ Superstar Vote (decisor)
  └─ Storyboard (roteiro do protótipo)

DIA 4 (QUINTA) — PROTOTIPAR
  └─ Divisão de papéis (Makers, Stitcher, Writer, Asset Collector, Interviewer)
  └─ Construção do protótipo (fidelidade suficiente para testar)
  └─ Roteiro de entrevista

DIA 5 (SEXTA) — TESTAR
  └─ 5 entrevistas com usuários (1:1)
  └─ Painel de observação (note-taking)
  └─ Debriefing e síntese de aprendizados
  └─ Decisão: pivot, persevere, iterate
```

---

## Dia 1 — ENTENDER

### Atividade: Mapa do Problema (End-to-End Map)

> **Objetivo:** Criar um mapa visual de como o usuário experimenta o problema do início ao fim.

#### Template

```markdown
## Mapa do Problema — [Nome do Desafio]

### Atores (quem está no mapa)
- [Ator 1]: [Papel no processo]
- [Ator 2]: [Papel no processo]

### Etapas da Jornada
| Etapa | O que acontece | Ator Principal | Dor/Oportunidade |
|-------|---------------|----------------|-----------------|
| 1. [Nome] | [Descrição] | [Ator] | [Dor ou oportunidade] |
| 2. [Nome] | | | |
| 3. [Nome] | | | |

### Ponto Focal Escolhido
**Onde focaremos:** Etapa [N] — [Nome da etapa]  
**Por quê:** [Justificativa — maior dor, maior oportunidade, mais factível]
```

---

### Atividade: HMW — How Might We (Como Poderíamos)

> **Objetivo:** Transformar problemas e insights em oportunidades de design.

#### Protocolo

1. Cada participante escreve perguntas HMW em post-its durante as lightning talks
2. Formato obrigatório: **"Como poderíamos [ação] para [benefício/resultado]?"**
3. Agrupamento por temas
4. Dot voting: cada pessoa tem 2 votos
5. Top 3-5 HMWs são fixadas no mapa na etapa correspondente

#### Template de Saída

```markdown
## HMW — Como Poderíamos

### Cluster: [Tema]
- HMW-01: Como poderíamos [ação] para [resultado]?
- HMW-02: Como poderíamos [ação] para [resultado]?

### Cluster: [Tema]
- HMW-03: ...

### Top HMWs Selecionados (após voting)
1. HMW-XX — [texto] — [n] votos
2. HMW-XX — [texto] — [n] votos
3. HMW-XX — [texto] — [n] votos
```

---

### Atividade: Sprint Question

> **A pergunta central que o sprint precisa responder.**

#### Template

```markdown
## Sprint Questions

**Sprint Question Principal:**
> Conseguimos [comportamento do usuário] para [resultado de negócio] até [data/métrica]?

**Sprint Questions secundárias:**
1. [Hipótese de risco que precisa ser validada]
2. [Hipótese de risco que precisa ser validada]
3. [Hipótese de risco que precisa ser validada]

**Long-term Goal:**
> Em 2 anos, [visão de futuro do produto/serviço]

**Ponto Focal do Sprint:**
> Etapa: [X] do mapa | Persona: [nome] | HMW principal: [HMW-XX]
```

---

## Dia 2 — ESBOÇAR

### Atividade: Lightning Demos

> **Objetivo:** Coletar referências do mercado (não necessariamente do mesmo setor) para inspirar soluções.

#### Template de Captura

```markdown
## Lightning Demos — Referências Coletadas

| Referência | Empresa/Produto | O que funciona bem | Como poderíamos adaptar |
|-----------|----------------|-------------------|------------------------|
| [Demo 1] | [Empresa] | [Insight específico] | [Ideia de adaptação] |
| [Demo 2] | | | |

### Big Ideas capturadas
- [Ideia 1 — de qual demo veio]
- [Ideia 2 — de qual demo veio]
```

---

### Atividade: Crazy 8s

> **Regra:** 8 esboços de soluções em 8 minutos (1 por minuto). Quantidade > qualidade.

#### Protocolo para o Facilitador

1. Dobrar uma folha A4 em 8 quadrantes
2. Cada quadrante = 1 ideia/tela/conceito
3. Timer: 1 minuto por quadrante
4. Sem julgamentos — o objetivo é velocidade e quantidade
5. Após 8 minutos: cada participante apresenta seus Crazy 8s (3 min max por pessoa)

#### Template de Captura Digital

```markdown
## Crazy 8s — [Participante] — [Data]

| Q1 | Q2 | Q3 | Q4 |
|----|----|----|----|
| [Ideia 1] | [Ideia 2] | [Ideia 3] | [Ideia 4] |

| Q5 | Q6 | Q7 | Q8 |
|----|----|----|----|
| [Ideia 5] | [Ideia 6] | [Ideia 7] | [Ideia 8] |

**Minha favorita:** Q[n] — [Por quê]
```

---

### Atividade: Solution Sketch (Esboço de Solução)

> **Objetivo:** Detalhar a melhor ideia em 3 telas/etapas com título e explicação.

#### Template

```markdown
## Solution Sketch — [Autor]

**Título da solução:** [Nome curto e memorável]
**Sprint Question endereçada:** [HMW ou Sprint Question]

### Tela 1 — [Nome/Etapa]
[Descrição ou esboço da interface/interação]
- O que o usuário vê: [...]
- O que o usuário pode fazer: [...]

### Tela 2 — [Nome/Etapa]
[Descrição ou esboço]

### Tela 3 — [Nome/Etapa]
[Descrição ou esboço]

**Notas para o votador:**
[Explica aspectos não óbvios da solução]
```

---

## Dia 3 — DECIDIR

### Atividade: Art Museum + Dot Voting

> **Protocolo:** Soluções são coladas na parede. Todos andam em silêncio e votam com dots adesivos.

#### Template de Registro

```markdown
## Voting — Resultado do Dot Voting

| Solução | Autor | Votos Time | Voto Decisor | Status |
|---------|-------|:----------:|:------------:|--------|
| [Título] | [Nome] | [n] | ✅/❌ | Selecionado / Descartado |

### Solução(ões) Selecionada(s)
1. [Título] — [Autor] — [n] votos + voto do decisor
   **Por que ganhou:** [justificativa]

### Soluções para referência futura (não usadas agora)
- [Título] — [Boa ideia para outra rodada]
```

---

### Atividade: Storyboard

> **Objetivo:** Roteiro quadro-a-quadro do protótipo (8-12 quadros). É o script que os makers seguirão no Dia 4.

#### Template

```markdown
## Storyboard — [Nome do Protótipo]

**Abrindo cena:** [Como o usuário chega ao produto — contexto inicial]

| Quadro | Título | O que acontece | Tela/Interface | Decisão de design |
|--------|--------|---------------|----------------|-------------------|
| 1 | [Nome] | [Ação do usuário] | [Descrição da tela] | [Decisão crítica] |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |

**Fechando cena:** [Como termina a experiência — o que o usuário conquista]

### Decisões de Design Tomadas
1. [Decisão] — [Por quê] — [Descartamos o quê?]
2. [Decisão] — [Por quê]
```

---

## Dia 4 — PROTOTIPAR

### Divisão de Papéis

| Papel | Responsabilidade | Quem assume |
|-------|-----------------|-------------|
| **Maker(s)** | Constroem os componentes (telas, slides, etc.) | 2-3 pessoas |
| **Stitcher** | Junta todas as partes em um fluxo coeso | 1 pessoa |
| **Writer** | Escreve todos os textos, botões, labels | 1 pessoa |
| **Asset Collector** | Imagens, ícones, fontes, dados fictícios | 1 pessoa |
| **Interviewer** | Prepara roteiro e pratica entrevistas | 1 pessoa |

### Ferramentas Recomendadas

| Tipo de Protótipo | Ferramenta |
|------------------|------------|
| App / Web UI | Figma, Marvel, InVision |
| Serviço / Processo | Storyboard em slides (PowerPoint/Keynote) |
| Hardware / Físico | Fotos + narração em vídeo |
| Conversação / IA | Script em documento + facilitador humano |
| Landing page | Carrd, Notion público, Webflow |

### Checklist do Protótipo

```markdown
## Checklist — Protótipo Dia 4

- [ ] O protótipo segue o Storyboard (8-12 quadros)?
- [ ] Existe um "ponto de entrada" claro para o usuário?
- [ ] Os textos foram revisados pelo Writer?
- [ ] O Stitcher validou o fluxo completo sem quebras?
- [ ] O protótipo é "goldilocks" — real o suficiente para testar, rápido o suficiente para construir?
- [ ] O Interviewer tem o roteiro de teste pronto?
- [ ] 5 participantes de teste confirmados para amanhã?
```

---

## Dia 5 — TESTAR

### Roteiro de Entrevista (Template)

```markdown
## Roteiro de Entrevista — Design Sprint

**Duração:** 60 minutos por participante
**Formato:** 1:1, facilitador + observadores (via câmera ou sala espelho)

---

### FASE 1 — Aquecimento (5 min)
"Olá, muito obrigado por participar. Meu nome é [nome]. Vou fazer algumas perguntas e mostrar algo para você interagir."

**Perguntas de aquecimento:**
- Me conta um pouco sobre como você [contexto do problema — ex: gerencia times, contrata serviços, etc.]
- Quais ferramentas você usa hoje para [tarefa relacionada ao sprint]?
- Qual é a maior dificuldade que você enfrenta com [problema central]?

---

### FASE 2 — Contexto (10 min)
[Perguntas específicas sobre o comportamento atual — antes de mostrar o protótipo]
- [Pergunta exploratória 1]
- [Pergunta exploratória 2]
- [Pergunta sobre o ponto focal do sprint]

---

### FASE 3 — Teste do Protótipo (35 min)
"Agora vou te mostrar algo que estamos trabalhando. Não é um produto final — é uma ideia. Quero que você pense em voz alta enquanto explora."

**Tarefas de teste:**
1. [Tarefa 1 — ex: "Você recebeu um email sobre X. O que você faria agora?"]
2. [Tarefa 2]
3. [Tarefa 3 — se der tempo]

**Perguntas de acompanhamento:**
- "O que você acha que aconteceria se você clicasse aqui?"
- "O que passaria pela sua cabeça nesse momento?"
- "O que você esperaria ver depois disso?"

---

### FASE 4 — Impressões gerais (10 min)
- "O que você achou no geral?"
- "O que mais te chamou atenção — positivo ou negativo?"
- "Se este produto existisse, você usaria? Por quê?"
- "O que deixaria você inseguro em adotá-lo?"
- "Tem algo que você sentiu falta?"

---

**Não fazer:**
- ❌ Defender o protótipo
- ❌ Fazer perguntas que induzem resposta ("Você gostou de X, né?")
- ❌ Explicar como funciona antes de deixar o usuário explorar
```

---

### Template de Note-Taking (Painel de Observação)

```markdown
## Note-Taking — Entrevista [n] — Participante: [Código/Nome]

**Perfil:** [Cargo/Contexto]
**Data/Hora:** [...]

| Quadro do Storyboard | Observação | Tipo | Citação direta |
|---------------------|-----------|------|----------------|
| Q1 | [O que aconteceu] | 😊 Positivo / 😐 Neutro / 😤 Negativo | "[fala do usuário]" |
| Q2 | | | |
| ...| | | |

### Momentos Críticos
- [Momento onde o usuário travou ou ficou confuso]
- [Momento de deleite ou surpresa positiva]

### Sprint Questions Respondidas
- [Sprint Question]: [Evidência — o usuário confirmou ou refutou?]
```

---

### Síntese de Aprendizados — Debriefing

```markdown
## Síntese do Design Sprint — [Nome do Desafio]

**Data:** [período do sprint]
**Time:** [lista de participantes + papéis]

---

### Padrões Identificados (5 entrevistas)

| Observação | Entrevista 1 | 2 | 3 | 4 | 5 | Padrão? |
|-----------|:------------:|:-:|:-:|:-:|:-:|:-------:|
| [Comportamento/reação] | ✅ | ✅ | ❌ | ✅ | ✅ | **SIM (4/5)** |
| [Comportamento/reação] | | | | | | |

> **Regra:** Padrão = acontece em 3+ de 5 entrevistas.

---

### Sprint Questions — Respostas

| Sprint Question | Respondida? | Evidência |
|----------------|:-----------:|-----------|
| [Pergunta] | ✅ Sim / ❌ Não / ⚠️ Parcial | [Resumo da evidência] |

---

### Decisão do Time

- [ ] **PERSEVERE** — A solução funcionou. Próximo passo: desenvolver.
- [ ] **ITERATE** — A direção é boa mas há ajustes necessários. Próximo passo: refinar e re-testar.
- [ ] **PIVOT** — A solução não funcionou. Voltar para HMWs e tentar abordagem diferente.

**Decisão:** [PERSEVERE / ITERATE / PIVOT]  
**Justificativa:** [Por que o time tomou essa decisão]

---

### Próximos Passos

- [ ] [Ação 1 — responsável — prazo]
- [ ] [Ação 2 — responsável — prazo]
- [ ] [Backlog criado a partir das funcionalidades validadas]
```

---

## Artefato Consolidado — DESIGN_SPRINT.md

```markdown
# Design Sprint — [Nome do Desafio]
<!-- Período: [data início] a [data fim] | Time: [n pessoas] | Facilitador: [nome] -->

## Desafio
[Uma frase descrevendo o problema/oportunidade central]

## Long-term Goal
> [Visão de longo prazo]

## Sprint Question Principal
> [A pergunta que o sprint tentou responder]

---

[Artefatos de cada dia: Mapa, HMWs, Soluções selecionadas, Storyboard, Protótipo (link), Resultados]

---

## Resultado
**Decisão:** PERSEVERE / ITERATE / PIVOT  
**Confiança:** [Alta / Média / Baixa]  
**Aprendizados principais:**
1. [Aprendizado]
2. [Aprendizado]
3. [Aprendizado]
```

---

## Edge Cases e Situações Comuns

### "Não conseguimos recrutar 5 usuários para o Dia 5"
→ Mínimo aceitável: 3 usuários. Com 3 já é possível identificar padrões.  
→ Alternativa: "gorilla testing" — abordar usuários em locais onde o público-alvo frequenta.  
→ Nunca testar com membros do time ou familiares.

### "O time não consegue decidir entre duas soluções no Dia 3"
→ Prototipar as duas em paralelo (se o time tiver capacidade no Dia 4).  
→ Ou fazer uma votação secreta — cada um escreve sua escolha em papel.  
→ Último recurso: o Decisor tem voto de minerva.

### "O protótipo não ficou pronto no Dia 4"
→ Simplificar: o protótipo precisa ser "real o suficiente para enganar", não perfeito.  
→ Reduzir escopo: testar apenas os quadros críticos do Storyboard (Q4-Q8, por exemplo).  
→ Usar um facilitador humano para "jogar o papel" do produto (Wizard of Oz).

### "Os usuários não entenderam o protótipo"
→ Isso É um aprendizado. Registrar como insight crítico.  
→ Não explicar o produto durante a entrevista — a confusão é um dado real.  
→ Decisão: ITERATE com foco em clareza de comunicação.

### "Todos os 5 usuários amaram o protótipo"
→ Ótimo sinal, mas validar com mais rigor: "Você pagaria por isso? Quanto?"  
→ Verificar se as Sprint Questions de risco foram todas respondidas.  
→ Cuidado com viés de cortesia — investigar com "O que te faria NÃO usar isso?".

### "Adaptação para Design Sprint de 3 dias"
→ Dia 1 (comprimido): Mapa + HMW + Lightning Demos + Crazy 8s + Dot Voting  
→ Dia 2 (comprimido): Solution Sketch + Storyboard + Protótipo  
→ Dia 3 (igual): 5 entrevistas + Debriefing  
→ Perda: menos diversidade de ideias no esboço; compensar com prep prévia dos participantes.

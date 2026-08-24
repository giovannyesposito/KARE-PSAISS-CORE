---
name: lean-inception
description: >
  Apoio completo à condução e geração de artefatos da Lean Inception (metodologia Paulo Caroli).
  Cobre os 5 dias do workshop: Visão do Produto, É/Não É/Faz/Não Faz, Personas, Jornada,
  Brainstorming de Funcionalidades, Revisão Técnica/UX/Negócio, Sequenciador e MVP Canvas.
  Protocolo proativo: orienta facilitação, gera templates prontos e consolida backlog inicial.
triggers:
  - "lean inception"
  - "inception"
  - "visão do produto"
  - "mvp canvas"
  - "sequenciador"
  - "é não é faz não faz"
  - "persona lean"
  - "jornada do usuário"
  - "brainstorming de funcionalidades"
  - "workshop de produto"
  - "/lean-inception"
  - "/gen-inception"
---

# Lean Inception Skill

> **Referência:** Metodologia Lean Inception — Paulo Caroli (caroli.org)  
> **Duração típica:** 5 dias de workshop (pode ser comprimido em 3 dias intensivos)  
> **Output final:** MVP Canvas + Backlog inicial priorizado + Visão compartilhada de produto

---

## Protocolo de Atuação (Proativo)

Ao ser ativado, o agente:

1. Verifica se existe `PROJECT_CONTEXT.md` ou `PRD.md` no workspace
2. Identifica em que fase da Lean Inception o usuário está
3. Gera o artefato solicitado ou orienta a atividade seguinte
4. Consolida outputs em `LEAN_INCEPTION.md` no workspace
5. Propõe próximo passo no sequenciador de atividades

---

## Estrutura dos 5 Dias

```
DIA 1 — ALINHAMENTO
  └─ Atividade 1: Visão do Produto
  └─ Atividade 2: O produto É / Não É / Faz / Não Faz
  └─ Atividade 3: Objetivos do produto

DIA 2 — PESSOAS
  └─ Atividade 4: Personas
  └─ Atividade 5: Jornada do Usuário

DIA 3 — FUNCIONALIDADES
  └─ Atividade 6: Brainstorming de Funcionalidades
  └─ Atividade 7: Revisão Técnica, de UX e de Negócio

DIA 4 — PRIORIZAÇÃO
  └─ Atividade 8: Sequenciador de Funcionalidades

DIA 5 — MVP
  └─ Atividade 9: MVP Canvas
  └─ Consolidação e próximos passos
```

---

## Atividade 1 — Visão do Produto

### Template

```markdown
## Visão do Produto

Para [cliente-alvo]
Cujo [problema ou oportunidade]
O [nome do produto]
É um [categoria do produto]
Que [benefício-chave, razão de compra]
Diferente de [alternativa concorrente]
Nosso produto [diferença-chave]
```

### Exemplo

```markdown
## Visão do Produto

Para times de produto B2B
Cujo processo de discovery é lento e inconsistente
O KARE Agile Agent
É um assistente de IA especializado em ciclo de vida ágil
Que acelera descoberta, planejamento e entrega com qualidade rastreável
Diferente de assistentes genéricos de IA
Nosso produto domina o contexto do projeto e integra com Jira/Confluence nativamente
```

### Perguntas Facilitadoras

- Quem usa o produto? (não quem paga — quem usa)
- Qual o maior problema que o produto resolve?
- O que torna o produto único frente às alternativas?
- Em qual categoria o produto se enquadra?

---

## Atividade 2 — É / Não É / Faz / Não Faz

> **Objetivo:** Alinhar o time sobre o que está DENTRO e FORA do escopo do produto.

### Template

```markdown
## É / Não É / Faz / Não Faz — [Nome do Produto]

| | É | Não É |
|---|---|---|
| **Faz** | [o que o produto É e FAZ] | [o que o produto FAZ mas NÃO É] |
| **Não Faz** | [o que o produto É mas NÃO FAZ] | [o que o produto NÃO É e NÃO FAZ] |
```

### Quadrantes Explicados

| Quadrante | Significado | Exemplo |
|-----------|------------|---------|
| **É + Faz** | Core do produto | "É um assistente de IA e faz geração de stories" |
| **É + Não Faz** | O produto É isso mas ainda não FAZ | "É um agente mas ainda não faz deploy automático" |
| **Não É + Faz** | O produto FAZ mas não é categorizado assim | "Faz análise de risco mas não é um tool de governança" |
| **Não É + Não Faz** | Explicitamente fora do escopo | "Não é um ERP e não faz gestão financeira" |

### Perguntas Facilitadoras

- "Isso é parte do produto ou fora do escopo?"
- "O produto FAZ isso hoje ou está previsto?"
- "Isso é algo que NUNCA faremos ou só não fazemos agora?"

---

## Atividade 3 — Objetivos do Produto

### Template

```markdown
## Objetivos do Produto

### Objetivos de Negócio
1. [Objetivo mensurável — ex: Reduzir time-to-market em 30%]
2. [Objetivo mensurável]
3. [Objetivo mensurável]

### Objetivos de Usuário
1. [O que o usuário ganha — ex: Criar stories válidas em < 5 minutos]
2. [O que o usuário ganha]

### Objetivos Técnicos
1. [Qualidade, performance, segurança — ex: 99.9% uptime]
2. [Objetivo técnico]

### Métricas de Sucesso (OKRs / KPIs)
| Objetivo | Métrica | Meta | Prazo |
|----------|---------|------|-------|
| [Obj] | [Métrica] | [Valor alvo] | [Data] |
```

---

## Atividade 4 — Personas

### Template

```markdown
## Persona — [Nome da Persona]

**Nome:** [Nome fictício representativo]
**Papel:** [Cargo/Função]
**Empresa/Contexto:** [Tipo de empresa ou contexto de uso]

### Quem é
[2-3 frases descrevendo o perfil]

### Comportamentos
- [Comportamento 1]
- [Comportamento 2]
- [Comportamento 3]

### Necessidades e Objetivos
- [O que precisa realizar]
- [O que considera sucesso]

### Frustrações e Dores
- [O que a impede hoje]
- [O que a frustra no processo atual]

### Citação representativa
> "[Fala típica desta persona sobre o problema que o produto resolve]"

### Nível de Engajamento
- **Frequência de uso:** [Diário / Semanal / Esporádico]
- **Proficiência técnica:** [Baixa / Média / Alta]
- **Poder de decisão:** [Usuário final / Influenciador / Decisor]
```

### Perguntas para Construção de Persona

- Quem usa o produto no dia a dia? (≠ quem decide comprar)
- Qual o contexto de uso? (onde, quando, com que frequência?)
- O que define sucesso para esta persona?
- Quais suas maiores frustrações com o processo atual?
- Como ela tomaria a decisão de adotar este produto?

---

## Atividade 5 — Jornada do Usuário

### Template

```markdown
## Jornada — [Persona] realizando [Objetivo]

| Fase | Ação do Usuário | Pensamento | Sentimento | Oportunidade |
|------|----------------|------------|------------|--------------|
| [F1] | [O que faz] | [O que pensa] | 😊/😐/😤 | [Como o produto ajuda] |
| [F2] | | | | |
| [F3] | | | | |

### Pontos de Dor Identificados
1. [Dor crítica na jornada]
2. [Dor secundária]

### Momentos de Deleite
1. [Onde o produto pode surpreender positivamente]
```

---

## Atividade 6 — Brainstorming de Funcionalidades

### Protocolo

1. **Fase divergente (10-15 min):** Cada participante escreve funcionalidades em post-its (1 por post-it)
2. **Agrupamento:** Organizar post-its em clusters temáticos
3. **Nomeação:** Cada cluster vira uma categoria de funcionalidade
4. **Listagem:** Extrair lista de funcionalidades individuais

### Template de Saída

```markdown
## Funcionalidades — [Nome do Produto]

### Categoria: [Nome do Cluster]
- F-01: [Nome da funcionalidade] — [Persona beneficiada] — [Objetivo atendido]
- F-02: [Nome da funcionalidade] — [Persona beneficiada] — [Objetivo atendido]
- F-03: [Nome da funcionalidade] — [Persona beneficiada] — [Objetivo atendido]

### Categoria: [Nome do Cluster]
- F-04: [Nome da funcionalidade] — [Persona beneficiada] — [Objetivo atendido]
```

---

## Atividade 7 — Revisão Técnica, UX e de Negócio

> **Objetivo:** Avaliar cada funcionalidade em 3 dimensões antes de priorizar.

### Template de Avaliação

```markdown
## Revisão de Funcionalidades

| ID | Funcionalidade | Esforço Técnico | Valor UX | Valor Negócio | Confiança | Classificação |
|----|---------------|:--------------:|:-------:|:-------------:|:---------:|:-------------:|
| F-01 | [Nome] | P/M/G/GG | 1-3 | 1-3 | A/M/B | Fazer/Analisar/Descartar |
| F-02 | [Nome] | | | | | |
```

### Legenda

| Campo | Opções |
|-------|--------|
| **Esforço Técnico** | P (Pequeno) / M (Médio) / G (Grande) / GG (Muito Grande) |
| **Valor UX** | 1 (Baixo) / 2 (Médio) / 3 (Alto) |
| **Valor Negócio** | 1 (Baixo) / 2 (Médio) / 3 (Alto) |
| **Confiança** | A (Alta) / M (Média) / B (Baixa) |
| **Classificação** | Fazer / Analisar / Descartar |

### Regras de Classificação

- **Fazer:** Alto valor (UX + Negócio ≥ 5) + Esforço ≤ M + Confiança A/M
- **Analisar:** Valor médio OU esforço alto OU confiança baixa → precisa de mais informação
- **Descartar (por ora):** Baixo valor + alto esforço OU fora do escopo do MVP

---

## Atividade 8 — Sequenciador

> **Objetivo:** Definir a ordem de implementação em ondas (waves), formando o roadmap MVP.

### Regras do Sequenciador (Paulo Caroli)

1. Uma onda pode ter no máximo **3 funcionalidades**
2. Não podem ter 2 funcionalidades de **alto esforço (GG)** na mesma onda
3. Toda onda deve ter pelo menos **uma funcionalidade de alto valor de negócio**
4. Toda onda deve ter pelo menos **uma funcionalidade de alto valor de UX**
5. Uma onda não pode ter apenas funcionalidades de **baixo valor** (negócio E UX = 1)

### Template

```markdown
## Sequenciador de Funcionalidades

### Onda 1 — [Nome da onda / Objetivo]
- ✅ F-XX: [Nome] — [Valor Negócio: 3 | Valor UX: 2 | Esforço: M]
- ✅ F-XX: [Nome] — [Valor Negócio: 2 | Valor UX: 3 | Esforço: P]

**Sprint estimadas:** [n sprints]  
**Hipótese validada:** [Qual hipótese de negócio essa onda valida?]

---

### Onda 2 — [Nome da onda / Objetivo]
- ✅ F-XX: [Nome]
- ✅ F-XX: [Nome]

**Sprint estimadas:** [n sprints]  
**Hipótese validada:** [...]

---

### Backlog Futuro (pós-MVP)
- F-XX: [Nome] — [Motivo para depois]
```

---

## Atividade 9 — MVP Canvas

### Template Completo

```markdown
## MVP Canvas — [Nome do Produto]

### 1. Proposta do MVP
[Uma frase descrevendo o que é o MVP — o mínimo que entrega valor real]

### 2. Personas Atendidas
- [Persona 1] — [Principal problema resolvido]
- [Persona 2] — [Principal problema resolvido]

### 3. Jornadas Cobertas
- [Jornada 1 — qual parte da jornada o MVP cobre]
- [Jornada 2 — qual parte da jornada o MVP cobre]

### 4. Funcionalidades do MVP
| Funcionalidade | Onda | Valor | Esforço |
|---------------|------|-------|---------|
| [F-XX] | 1 | Alto | Médio |
| [F-XX] | 1 | Alto | Pequeno |
| [F-XX] | 2 | Médio | Médio |

### 5. Resultado Esperado
[O que esperamos que aconteça quando o MVP for lançado — hipótese de negócio]

### 6. Métricas de Validação do MVP
| Métrica | Valor Atual (Baseline) | Meta MVP | Como Medir |
|---------|----------------------|---------|------------|
| [Métrica 1] | [valor] | [meta] | [instrumento] |
| [Métrica 2] | [valor] | [meta] | [instrumento] |

### 7. Custo & Esforço Estimado
- **Sprints de desenvolvimento:** [n]
- **Equipe necessária:** [composição]
- **Prazo estimado:** [período]

### 8. Restrições e Premissas
- [Restrição técnica ou de negócio]
- [Premissa assumida que precisa ser validada]
```

---

## Artefato Consolidado — LEAN_INCEPTION.md

Ao finalizar todos os dias, consolidar em:

```markdown
# Lean Inception — [Nome do Produto]
<!-- Data: [período do workshop] | Facilitador: [nome] | Participantes: [n] -->

## Sumário Executivo
[2-3 parágrafos descrevendo produto, personas e MVP decidido]

---

[Artefatos de cada atividade, na ordem do workshop]

---

## Decisões Críticas Tomadas
1. [Decisão] — [Justificativa] — [Data]
2. [Decisão] — [Justificativa] — [Data]

## Próximos Passos
- [ ] Criar backlog inicial a partir do Sequenciador
- [ ] Detalhar stories da Onda 1
- [ ] Definir time de desenvolvimento
- [ ] Agendar Sprint 0
```

---

## Perguntas de Saúde do Workshop

Use para verificar alinhamento ao final de cada dia:

| Pergunta | Resposta esperada |
|----------|-------------------|
| Todos concordam com a Visão do Produto? | ✅ Sim sem reservas |
| As personas refletem os usuários reais? | ✅ Validado com dados |
| O MVP valida uma hipótese de negócio clara? | ✅ Hipótese explícita |
| O sequenciador respeita as regras de ondas? | ✅ Validado |
| O time sente confiança para começar Sprint 1? | ✅ Confiança ≥ 7/10 |

---

## Edge Cases e Situações Comuns

### "Não sabemos quem são as personas"
→ Propor pesquisa rápida (entrevistas com 3-5 usuários) antes de continuar.  
→ Criar "proto-persona" baseada em hipótese, marcada como `[HIPÓTESE — validar]`.

### "Time não consegue priorizar as funcionalidades"
→ Usar dot voting: cada participante tem 3 votos para distribuir.  
→ Desempate: decidir quem tem voto de minerva (PO ou patrocinador).

### "O backlog explodiu — temos 50+ funcionalidades"
→ Aplicar critério: "Seria esta funcionalidade um bloqueador para o usuário usar o produto?"  
→ Mover tudo que não é bloqueador para "Backlog Futuro" no Sequenciador.

### "Discordância sobre o escopo do MVP"
→ Voltar ao É / Não É / Faz / Não Faz.  
→ Testar cada funcionalidade contra a Visão do Produto.  
→ Lembrar: MVP ≠ produto mínimo inútil — é o menor produto que valida a hipótese principal.

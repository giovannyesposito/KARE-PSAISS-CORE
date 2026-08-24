---
name: user-story-mapping
description: >
  Técnica de User Story Mapping (Jeff Patton): mapeia a jornada do usuário em
  Atividades ? Tarefas ? Stories, gerando mapa visual com slices de release
  (MVP, v1, v2). Use quando precisar organizar um backlog orientado à jornada
  do usuário, identificar gaps de cobertura, definir MVP ou planejar releases
  com base em fluxo de uso real. Invoque como /map-story ou ao mencionar
  "story map", "mapa de stories", "jornada do usuário", "user story mapping",
  "backbone", "walking skeleton".
triggers:
  - "user story mapping"
  - "story map"
  - "mapa de stories"
  - "jornada do usuário"
  - "backbone"
  - "walking skeleton"
  - "slice de release"
  - "mapa de jornada"
  - "/map-story"
agents:
  - story-crafter
  - backlog-architect
  - product-discovery
  - kare-orchestrator
---

# User Story Mapping Skill

> Técnica criada por Jeff Patton. Objetivo: visualizar o produto inteiro de uma
> vez, descobrir o que construir no MVP e alinhar o time em torno da jornada
> real do usuário — não de uma lista plana e descontextualizada.

---

## Conceito Fundamental

```
BACKBONE (horizontal)
???????????????????????????????????????????????????
[ Atividade 1 ]    [ Atividade 2 ]    [ Atividade N ]
   ?  ?  ?            ?  ?  ?            ?  ?  ?
 Task Task Task      Task Task Task      Task Task Task

SLICES DE RELEASE (horizontais por nível)
???????????????????????????????????????????????????
• MVP / Walking Skeleton   ? stories mínimas por tarefa
• Release 1.0              ? stories de valor adicional
• Release 2.0              ? stories de maturidade
• Backlog / Futuro         ? ideias e melhorias
```

### Camadas do Mapa

| Camada | Nome KARE | Sigla KARE | Descrição |
|--------|-----------|------------|----------| 
| Nível 0 | **Épico** | EP-XX | Objetivo de negócio de alto nível (múltiplos sprints) |
| Nível 1 | **Feature** | FT-XX | Entregavel concreto em 1-2 sprints; **nível intermediário OBRIGATÓRIO** entre Épico e Story |
| Nível 2 | **História de Usuário** | US-XX | Funcionalidade específica entregável em 1 sprint |
| Nível 2 | **Enabler** | EN-XX | Item técnico/infra sem valor direto ao usuário |
| Slice | **Fatia de Release** | — | Corte horizontal que agrupa features de valor viável |

> **REGRA INEGOCIÁVEL:** O USER_STORY_MAP.md gerado por esta skill DEVE incluir a linha de Features (FT-XX) como nível intermediário entre Épicos e Stories. Story Map sem Features é BLOQUEADO pelo `@quality-guardian`.

---

## Protocolo de Execução (Obrigatório)

### FASE 1 — Contexto

1. Ler `uploads/` e `PROJECT_CONTEXT.md` para identificar:
   - Persona(s) principais
   - Trilha (GF ou BF)
   - PRD ou Brief existente
2. Ler `demandas_processadas/<context_slug>/upstream/BACKLOG.md` para evitar duplicação
3. Se não existir PRD: aplicar o mínimo de clarificação via `@product-discovery`

### FASE 2 — Backbone (Atividades)

Identificar as **grandes etapas** que o usuário realiza do início ao fim do fluxo.

Regras:
- Ordenar cronologicamente da esquerda para a direita
- Máximo de **7 atividades** por persona (lei de Miller)
- Nomear com verbo no infinitivo: "Autenticar", "Pesquisar", "Comprar", "Acompanhar"
- Mapear para Épicos KARE (`EP-XX`) se já existirem

### FASE 3 — Features (FT-XX)

Para cada Épico, identificar as **Features** que o compõem — nível intermediário obrigatório.

Regras:
- Nomear com substantivo + complemento: "Acionamento HPSD VVN", "Abertura Chamado ServiceNow"
- Identificar `FT-XX` sequencial dentro do épico pai
- Toda Feature deve referenciar o Épico pai (EP-XX)
- Usar sigla `FT-XX` (não `FEAT-XXX`)

### FASE 4 — Tarefas de Usuário (Stories US-XX / Enablers EN-XX)

Para cada Feature, listar as **stories específicas** que a compõem.

Regras:
- Formato padrão KARE:  
  `Como [persona], quero [ação], para [valor]`
- Aplicar critério INVEST automaticamente
- Identificar `US-XX` (sequencial no backlog existente)
- Sinalizar itens técnicos/infra como `EN-XX` (Enabler)
- Toda US DEVE referenciar a Feature pai (FT-XX)

### FASE 5 — Slices de Release

Definir cortes horizontais que formam releases coerentes de valor.

Perguntas guia:
- "Qual é o **menor produto usável** que entrega valor real?"  ? MVP
- "O que matura a experiência sem ser crítico para lançar?" ? Release 1.0
- "O que diferencia o produto da concorrência a longo prazo?" ? Release 2.0+

Regras:
- Pelo menos **1 story por Tarefa** no MVP (walking skeleton)
- Não deixar nenhuma Atividade sem cobertura no MVP
- Anotar riscos e dependências em cada slice

### FASE 6 — Saída e Artefatos

Gerar os artefatos em `demandas_processadas/INI-XXX - Nome da Iniciativa/upstream/`:
- `USER_STORY_MAP.md` — mapa visual completo com hierarquia EP ? FT ? US
- Atualizar `BACKLOG.md` com as stories priorizadas por Feature e slice

#### Formato Visual Obrigatório — Mermaid block-beta

O mapa visual DEVE ser gerado como diagrama `block-beta` com a seguinte estrutura de grid:
- **6 colunas**: coluna 0 (rótulo da camada) + 1 coluna por Atividade (máx 5)
- **Linhas fixas**: PERSONA ? ATIVIDADES ? TAREFAS (N linhas) ? Versão 1/MVP (N linhas) ? Versão 2/v1.0 (N linhas)
- **Color coding obrigatório** via `classDef`:
  - `rotLabel` — cinza `#d9d9d9` para rótulos de camada (coluna esquerda)
  - `persona` — verde-claro `#b7e1cd` para persona
  - `atividade` — verde `#93c47d` para backbone (atividades)
  - `tarefa` — azul-claro `#9fc5e8` para tarefas do usuário
  - `mvp` — amarelo `#ffe599` para stories do MVP/Versão 1
  - `v2` — laranja-claro `#fce5cd` para stories da Versão 2+
- **Células vazias**: usar `space` (1 coluna) ou `space:N` (N colunas)
- Validar com `mermaid-diagram-validator` ANTES de salvar no arquivo

```
block-beta
  columns [N_ATIVIDADES + 1]

  lPer["PERSONA DO USUÁRIO"]:1  per["[Persona]"]:[N_ATIVIDADES]

  lAt["ATIVIDADES"]:1  a1["A1 [nome]"]:1  ... aN["AN [nome]"]:1

  lTar["TAREFAS"]:1  t1a["[tarefa]"]:1  ... tNa["[tarefa]"]:1
  space  t1b["[tarefa]"]:1  ... tNb["[tarefa]"]:1
  [repetir para cada linha de tarefa; usar space para atividades sem tarefa na linha]

  lMVP["MVP - Versao 1"]:1  v1a1["US-XXX [desc]"]:1  ... v1N1["US-XXX [desc]"]:1
  [repetir para cada linha de stories MVP; usar space para colunas sem story]

  lV2["v1.0 - Versao 2"]:1  [space para atividades sem stories v1.0]  v2X["US-XXX [desc]"]:1  ...

  classDef rotLabel fill:#d9d9d9,stroke:#999,color:#333,font-weight:bold;
  classDef persona fill:#b7e1cd,stroke:#57a96e,color:#1a4731,font-weight:bold;
  classDef atividade fill:#93c47d,stroke:#38761d,color:#1a3a00,font-weight:bold;
  classDef tarefa fill:#9fc5e8,stroke:#3d85c8,color:#0a2f5c;
  classDef mvp fill:#ffe599,stroke:#f1c232,color:#7a5200;
  classDef v2 fill:#fce5cd,stroke:#e69138,color:#5a2000;

  class lPer,lAt,lTar,lMVP,lV2 rotLabel
  class per persona
  class a1,...,aN atividade
  class t1a,...,tNx tarefa
  class v1a1,...,v1Nx mvp
  class v2x,...,v2y v2
```

---

## Template de Saída — USER_STORY_MAP.md

```markdown
# User Story Map — [Nome do Produto/Feature]

> Gerado por KARE | @[agente] | Data: [YYYY-MM-DD]  
> PRD: [link] | Contexto: [context_slug]

## Personas
- **[Persona Principal]**: [descrição em 1 linha]
- **[Persona Secundária]**: [descrição em 1 linha]

---

## Backbone — Atividades

| # | Atividade | Epic KARE | Descrição |
|---|-----------|-----------|-----------|
| A1 | [Autenticar] | EP-001 | [O usuário prova sua identidade] |
| A2 | [Pesquisar] | EP-002 | [...] |
| AN | [...] | EP-00N | [...] |

---

## Mapa Completo

### ?? A1 — [Atividade 1]

| Tarefa de Usuário | FEAT | MVP (Walking Skeleton) | Release 1.0 | Release 2.0 | Backlog |
|---|---|---|---|---|---|
| [Tarefa 1.1] | FEAT-001 | US-001: [...] | US-010: [...] | — | US-020: [...] |
| [Tarefa 1.2] | FEAT-002 | US-002: [...] | US-011: [...] | US-021: [...] | — |

### ?? A2 — [Atividade 2]

| Tarefa de Usuário | FEAT | MVP (Walking Skeleton) | Release 1.0 | Release 2.0 | Backlog |
|---|---|---|---|---|---|
| [Tarefa 2.1] | FEAT-003 | US-003: [...] | — | US-022: [...] | — |

---

## Slices de Release

### ?? MVP — Walking Skeleton
> Objetivo: [qual é o fluxo mínimo completo?]

| ID | Story | Atividade | Tarefa | Critério de Pronto |
|----|-------|-----------|--------|---------------------|
| US-001 | Como [...] | A1 | T1.1 | [AC em 1 linha] |
| US-002 | Como [...] | A1 | T1.2 | [...] |
| US-003 | Como [...] | A2 | T2.1 | [...] |

**Riscos do MVP:**  
- [Risco 1]
- [Risco 2]

---

### ?? Release 1.0
> Objetivo: [qual valor incremental entregamos?]

| ID | Story | Depdência | AC Resumido |
|----|-------|-----------|-------------|
| US-010 | [...] | US-001 | [...] |

---

### ?? Release 2.0
> Objetivo: [que maturidade ou diferenciação entregamos?]

| ID | Story | AC Resumido |
|----|-------|-------------|
| US-021 | [...] | [...] |

---

## Gaps Identificados
> Stories ou tarefas sem cobertura detectadas durante o mapeamento

| Atividade | Tarefa | Gap | Prioridade Sugerida |
|-----------|--------|-----|---------------------|
| [A1] | [T1.3] | [Não há story para recuperação de senha] | MVP |

---

## Rastreabilidade

| Story | Epic | Feature | ADR | Sprint |
|-------|------|---------|-----|--------|
| US-001 | EP-001 | FEAT-001 | — | Sprint 1 |

---

## Checklist de Qualidade do Mapa

- [ ] Todas as Atividades têm pelo menos 1 Tarefa
- [ ] Todas as Tarefas têm pelo menos 1 Story no MVP
- [ ] Todas as Stories têm AC Gherkin definido (ou referência)
- [ ] Não há duplicação com BACKLOG.md existente
- [ ] Personas confirmadas com o PRD
- [ ] Gaps documentados
- [ ] Slices coerentes (MVP não vazio, releases incrementais)
- [ ] IDs sequenciais sem colisão
```

---

## Regras de Qualidade (INVEST Aplicado ao Mapa)

| Critério | Verificação |
|----------|-------------|
| **I**ndependent | Cada story pode ser desenvolvida sem bloquear outra no mesmo slice? |
| **N**egotiable | O escopo de cada slice foi discutido e aprovado ou marcado `[PRECISA_VALIDAR]`? |
| **V**aluable | O MVP entrega fluxo completo de ponta a ponta para a persona principal? |
| **E**stimable | Stories grandes demais foram divididas (split)? |
| **S**mall | Nenhuma story excede 8 pontos estimados (candidata a split)? |
| **T**estable | Cada story tem AC testável identificado? |

---

## Padrões de Splitting (quando story é grande demais)

```
1. Por variação de dados  ? "Login com email" / "Login com Google" / "Login com SSO"
2. Por persona            ? "Busca para usuário logado" / "Busca para visitante"
3. Por regra de negócio   ? "Pagamento à vista" / "Pagamento parcelado"
4. Por plataforma         ? "Web" / "Mobile" / "API"
5. Por cenário de erro    ? "Happy path" / "Unhappy path"
6. Por performance        ? "Funcional" / "Otimizado"
7. Por CRUD               ? "Criar" / "Listar" / "Editar" / "Excluir"
```

---

## Anti-padrões a Evitar

| Anti-padrão | Sintoma | Correção |
|-------------|---------|----------|
| **Backlog plano** | Stories sem atividade pai | Agrupar em Tarefas/Atividades |
| **MVP obeso** | Mais de 40% das stories no MVP | Revisar critério de "mínimo" |
| **Atividade técnica** | "Criar banco de dados" no backbone | Reformular para perspectiva do usuário ou mover para Enabler |
| **Story vaga** | Sem "para que" ou sem AC | Aplicar `/story` para refinar |
| **Gap oculto** | Atividade sem cobertura no MVP | Criar Walking Skeleton mínimo |
| **Persona ausente** | Stories sem "Como [quem]" | Inferir do PRD ou marcar `[PRECISA_VALIDAR]` |

---

## Integração com Comandos KARE

| Comando | Integração com User Story Mapping |
|---------|-----------------------------------|
| `/create` | Executa Fases 1-6 automaticamente após PRD |
| `/story US-XXX` | Detalha story específica do mapa |
| `/sprint --capacity N` | Usa slices como base para seleção de sprint |
| `/quality --story US-XXX` | Valida story individualmente do mapa |
| `/risk --sprint N` | Avalia riscos por slice de release |
| `/analisar` | Verifica cobertura e rastreabilidade do mapa |

---

## Invocação Recomendada

```
@story-crafter /map-story para o módulo de [nome]
@backlog-architect gere o user story map do épico EP-001
@product-discovery quero um story map para [ideia]
@kare-orchestrator /map-story completo: discovery + mapa + backlog
```

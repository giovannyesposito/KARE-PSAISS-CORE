---
name: bcp-counting
description: >
  Contagem de BCP (Business Complexity Points) para User Stories e Backlog Items.
  Avalia 10 dimensões de complexidade de negócio segundo a régua CI&T, com critérios
  em PT-BR e tamanhos válidos por dimensão. Use quando precisar estimar complexidade
  de stories, features ou épicos em BCPs.
triggers:
  - "BCP"
  - "Business Complexity Points"
  - "complexidade de negócio"
  - "contar BCP"
  - "estimar complexidade"
  - "régua de complexidade"
  - "pontos de complexidade"
  - "quantos BCPs"
  - "sizing de story"
  - "complexidade da story"
allowed-tools: Read, Glob, Grep
---

# BCP Counting Skill

## O que são BCPs?

**Business Complexity Points (BCP)** é um método criado pela CI&T para medir,
demonstrar e padronizar a complexidade de software através de uma lente de negócio.
Diferente de Story Points (subjetivos), BCPs são baseados em critérios objetivos e
normalizados, permitindo comparações entre times e projetos.

A pontuação segue a **sequência Fibonacci**:

| Tamanho | Sigla | Pontos |
|---------|-------|--------|
| Extra Pequeno | XS | 1 |
| Pequeno | S | 2 |
| Médio | M | 3 |
| Grande | L | 5 |
| Extra Grande | XL | 8 |
| Não Aplicável | N/A | 0 |

**Total BCPs de uma story = soma dos pontos de todas as dimensões aplicáveis.**

---

## As 10 Dimensões de Complexidade

### Regras de Entrada

**Itens SEMPRE PRESENTES** (obrigatórios — nunca podem ser N/A ou Ocorrências=0):
- Regras de Negócio
- Papéis/Permissões
- Variações de Solução
- Entidades de Domínio
- Fronteiras

**Itens OPCIONAIS** (podem ser N/A se não se aplicam):
- Elementos de Interface
- Novas Entidades de Domínio
- Processos em Segundo Plano
- Notificações
- Auditorias

---

### Dimensão 1 — Regras de Negócio

**Descrição:** Qualquer tipo de instrução de negócio com pontos claros de disparo e interrupção.

**Tamanhos válidos:** XS, S, M, XL, N/A

| Tamanho | Critério |
|---------|---------|
| XS (1) | Instruções diretas, fórmulas ou validações simples (ex.: email válido, campo obrigatório, maior que, menor que) |
| S (2) | Processos iterativos com poucas fases/passos e **sem** pontos de decisão |
| M (3) | Processos iterativos com poucas fases/passos e com **poucos** pontos de decisão |
| XL (8) | Processos iterativos com **muitas** fases/passos e/ou **muitos** pontos de decisão |

> **Importante:** Cada regra de negócio distinta é uma linha separada (múltiplas Ocorrências).
> L não é um tamanho válido para esta dimensão.

---

### Dimensão 2 — Elementos de Interface

**Descrição:** Elementos de interface que representem conceitos de negócio.

**Tamanhos válidos:** S, M, L, XL, N/A

| Tamanho | Critério |
|---------|---------|
| S (2) | Adiciona e/ou remove até 5 elementos **estáticos** num contexto de negócio **existente**. Ex.: campos de texto, checkboxes, botões radio, tabelas simples, parâmetros. |
| M (3) | Adiciona e/ou remove até 5 elementos **estáticos** num contexto de negócio **novo**. |
| L (5) | Adiciona e/ou remove até 5 elementos **dinâmicos** num contexto de negócio **existente**. Ex.: abas, comportamentos dinâmicos, modals, grids/tabelas dinâmicas. |
| XL (8) | Adiciona e/ou remove até 5 elementos **dinâmicos** num contexto de negócio **novo**. |

> **Regra dos 5:** Para cada grupo de até 5 elementos, contar 1 Ocorrência. Se a story tem 11 elementos estáticos em contexto existente → 3 Ocorrências de S.
> XS não é um tamanho válido para esta dimensão.

---

### Dimensão 3 — Papéis/Permissões

**Descrição:** Quantidade de níveis de permissões especificados no Backlog Item para os papéis existentes na aplicação.

**Tamanhos válidos:** XS, S, M

| Tamanho | Critério |
|---------|---------|
| XS (1) | Mesmas permissões para todos os usuários. |
| S (2) | Conjuntos de permissões em um mesmo nível (ex.: Interno ou Externo; Consultor ou Operador). |
| M (3) | Conjuntos de permissões que abrangem dois ou mais níveis de profundidade (ex.: Usuário Externo: Operador ou Analista de Contratos; Usuário Interno: Analista de Crédito). |

> **Sempre presente.** Mínimo XS. L e XL não são válidos.

---

### Dimensão 4 — Variações de Solução

**Descrição:** Soluções que cumprem um mesmo objetivo de negócio podendo variar por influência de um parâmetro.

**Tamanhos válidos:** XS, M, XL

| Tamanho | Critério |
|---------|---------|
| XS (1) | Solução única para o fluxo de negócio. |
| M (3) | Solução comum com pequenas alterações de comportamento de acordo com o valor de um parâmetro. |
| XL (8) | Solução varia **significativamente** de acordo com o valor de um parâmetro. |

> **Sempre presente.** Mínimo XS. S, L não são válidos.

---

### Dimensão 5 — Fronteiras

**Descrição:** Interações que um Backlog Item possui com fontes/destinos de dados em função da propriedade, validade e durabilidade das informações trocadas.

**Tamanhos válidos:** XS, S, M, XL

| Tamanho | Critério |
|---------|---------|
| XS (1) | Tela e/ou banco de dados, ou não atravessa fronteiras (auto-contido). |
| S (2) | Leitura, escrita, troca de informações com device físico. |
| M (3) | Serviço de negócio remoto com troca de informações **perenes** (duradouras). |
| XL (8) | Serviço de negócio remoto com troca de informações **voláteis** (efêmeras). |

> **Sempre presente.** L não é válido. Cada sistema/fronteira externo é uma Ocorrência separada.

---

### Dimensão 6 — Entidades de Domínio

**Descrição:** Quantidade de entidades que possuem semântica de negócio envolvidas no domínio de um Backlog Item.

**Tamanhos válidos:** XS, S, M, L, XL

| Tamanho | Critério |
|---------|---------|
| XS (1) | 1 entidade |
| S (2) | 2 ou 3 entidades |
| M (3) | 4 ou 5 entidades |
| L (5) | 6 ou 7 entidades |
| XL (8) | Mais que 7 entidades |

> **Sempre presente.** Contar todas as entidades de negócio envolvidas (lidas, escritas ou referenciadas pela story).

---

### Dimensão 7 — Novas Entidades de Domínio

**Descrição:** Quantidade de entidades incorporadas ao domínio de negócio ou modificadas pelo Backlog Item.

**Tamanhos válidos:** S, L, N/A

| Tamanho | Critério |
|---------|---------|
| S (2) | Adiciona novos atributos ou relacionamentos para até 3 Entidades **existentes**. |
| L (5) | Adiciona ao contexto de negócio até 3 novas **Entidades**. |
| N/A (0) | Não há criação nem modificação estrutural de entidades. |

---

### Dimensão 8 — Processos em Segundo Plano

**Descrição:** Processos disparados de maneira indireta (stealth), que não impedem a utilização do sistema durante a execução.

**Tamanhos válidos:** S, M, L, XL, N/A

| Tamanho | Critério |
|---------|---------|
| S (2) | Processo disparado por um evento do sistema (ex.: avaliação de crédito quando todas as aprovações necessárias foram feitas). |
| M (3) | Processo agendado (ex.: processo que finaliza todos os dias às 11h). |
| L (5) | Processo agendado que pode ser disparado manualmente (ex.: finalização manual do ciclo de pedidos). |
| XL (8) | Processo externo e independente (ex.: nova aplicação executada fora do sistema). |
| N/A (0) | Não há processos em segundo plano. |

---

### Dimensão 9 — Notificações

**Descrição:** Avisos de ocorrência de eventos em um Backlog Item.

**Tamanhos válidos:** XS, N/A

| Tamanho | Critério |
|---------|---------|
| XS (1) | Envio de e-mail, textos de notificação de sistema, SMS ou notificações de hardware. |
| N/A (0) | Não há notificações. |

> Cada tipo de notificação pode ser uma Ocorrência separada.

---

### Dimensão 10 — Auditorias

**Descrição:** Registro de informações de identificação (data e responsável) associados a manipulações de negócio sobre Entidades de Domínio.

**Tamanhos válidos:** XS, N/A

| Tamanho | Critério |
|---------|---------|
| XS (1) | Trilha de auditoria para uma Entidade. |
| N/A (0) | Não há requisito de auditoria. |

> Uma Ocorrência por Entidade auditada.

---

## Protocolo de Contagem — Passo a Passo

### Fase 1: Leitura da Story

1. Leia a User Story completa (título, narrativa, Critérios de Aceite)
2. Identifique: qual o objetivo de negócio? Quais entidades? Quais sistemas externos?
3. Liste os elementos candidatos para cada dimensão

### Fase 2: Avaliação Dimensão por Dimensão

Para cada uma das 10 dimensões:

1. **Determine se se aplica** (para opcionais: se N/A, registre 0)
2. **Conte Ocorrências** (ex.: 3 regras de negócio = 3 linhas)
3. **Para cada Ocorrência, determine o tamanho** usando os critérios acima
4. **Documente o racional** explicando por que aquele tamanho foi escolhido

### Fase 3: Cálculo

```
Total BCPs = Σ (Pontos de cada Ocorrência de cada Dimensão)
```

> Não há multiplicação — apenas soma. Cada ocorrência contribui independentemente.

### Fase 4: Apresentação

Use sempre o formato de tabela padrão (ver seção Formato de Saída).

---

## Formato de Saída Padrão

```markdown
## Contagem BCP — [Título da Story]

| Item de Complexidade | Ocorrências | Qtde | Racional | Complexidade | Pontos |
|---|---|---|---|---|---|
| Regras de Negócio | 1 | — | [descrição da regra] | M | 3 |
| Regras de Negócio | 1 | — | [descrição de segunda regra] | XS | 1 |
| Elementos de Interface | 0 | 0 | n/a | N/A | 0 |
| Papéis/Permissões | 1 | — | [justificativa] | XS | 1 |
| Variações de Solução | 1 | — | [justificativa] | XS | 1 |
| Fronteiras | 1 | — | [sistema A / sistema B] | M | 3 |
| Entidades de Domínio | 1 | 3 | [Entidade1, Entidade2, Entidade3] | S | 2 |
| Novas Entidades de Domínio | 0 | 0 | n/a | N/A | 0 |
| Processos em Segundo Plano | 0 | 0 | n/a | N/A | 0 |
| Notificações | 0 | 0 | n/a | N/A | 0 |
| Auditorias | 0 | 0 | n/a | N/A | 0 |
| **TOTAL** | | | | | **11** |

> 🔴 **Itens obrigatórios** (nunca N/A): Regras de Negócio, Papéis/Permissões,
> Variações de Solução, Entidades de Domínio, Fronteiras.
```

### Campos da tabela

| Campo | Descrição |
|---|---|
| **Item de Complexidade** | Nome da dimensão |
| **Ocorrências** | Quantas instâncias distintas desta dimensão existem na story |
| **Qtde** | Quantidade do objeto contado (ex.: nº de entidades, nº de elementos de interface) |
| **Racional** | Justificativa textual da escolha do tamanho |
| **Complexidade** | Tamanho escolhido (XS/S/M/L/XL/N/A) |
| **Pontos** | Valor Fibonacci correspondente (0 se N/A) |

---

## Regras de Ouro

1. **Regras de Negócio pode ter múltiplas ocorrências** — cada regra distinta é uma linha separada na tabela
2. **Fronteiras conta por sistema externo** — se a story integra 3 sistemas, pode haver 3 linhas de Fronteiras
3. **Elementos de Interface conta em grupos de 5** — a cada 5 elementos, uma nova Ocorrência
4. **Entidades de Domínio é sempre 1 Ocorrência** com a Qtde representando o total de entidades
5. **Tamanhos inválidos não podem ser usados** — consulte a lista de tamanhos válidos por dimensão
6. **Itens obrigatórios nunca são N/A** — se não conseguir identificar, revisar o entendimento da story
7. **O racional deve ser registrado** — sem justificativa, a contagem não é auditável

---

## Referências

- Régua completa em PT-BR: `.agent/skills/bcp-counting/references/BCP_RULER_PT.md`
- Exemplos reais de contagem: `.agent/skills/bcp-counting/references/COUNTING_EXAMPLES.md`
- Site oficial CI&T: https://ciandt.com/us/en-us/complexitypoints

# Régua de Complexidade de Negócio (BCP) — Referência Completa PT-BR

> **Fonte:** CI&T Business Complexity Points | Versão PT-BR baseada na planilha
> oficial "Contagem BCPs.xlsx" e no site https://ciandt.com/us/en-us/complexitypoints

---

## Escala de Pontos

| Complexidade | Tamanho | Pontos |
|---|---|---|
| Extra Pequeno | XS | **1** |
| Pequeno | S | **2** |
| Médio | M | **3** |
| Grande | L | **5** |
| Extra Grande | XL | **8** |
| Não Aplicável | N/A | **0** |

---

## Tabela Completa — Dimensões × Tamanhos

### 1. Regras de Negócio

> Qualquer tipo de instrução de negócio com pontos claros de disparo e interrupção.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Instruções diretas, fórmulas ou validações simples (ex.: email válido, campo obrigatório, maior que, menor que) |
| S | 2 | Processos iterativos com poucas fases/passos e **sem** pontos de decisão |
| M | 3 | Processos iterativos com poucas fases/passos e com **poucos** pontos de decisão |
| ~~L~~ | — | *Não aplicável a esta dimensão* |
| XL | 8 | Processos iterativos com **muitas** fases/passos e/ou **muitos** pontos de decisão |
| N/A | 0 | *Não recomendado — Regras de Negócio são sempre obrigatórias* |

**Tamanhos válidos: XS · S · M · XL**

---

### 2. Elementos de Interface

> Elementos de interface que representem conceitos de negócio.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| ~~XS~~ | — | *Não aplicável a esta dimensão* |
| S | 2 | Adiciona e/ou remove até 5 elementos **estáticos** num contexto de negócio **existente**. Ex.: campos de texto, checkboxes, botões radio, tabelas simples, parâmetros. |
| M | 3 | Adiciona e/ou remove até 5 elementos **estáticos** num contexto de negócio **novo**. |
| L | 5 | Adiciona e/ou remove até 5 elementos **dinâmicos** num contexto de negócio **existente**. Ex.: abas, comportamentos dinâmicos, modals, grids/tabelas dinâmicas. |
| XL | 8 | Adiciona e/ou remove até 5 elementos **dinâmicos** num contexto de negócio **novo**. |
| N/A | 0 | Não há alterações de interface nesta story. |

**Tamanhos válidos: S · M · L · XL · N/A**

> **Regra dos 5:** Para cada grupo de até 5 elementos, 1 Ocorrência.
> - 1–5 elementos → 1 Ocorrência
> - 6–10 elementos → 2 Ocorrências
> - 11–15 elementos → 3 Ocorrências

---

### 3. Papéis/Permissões

> Quantidade de níveis de permissões especificados no Backlog Item para os papéis existentes na aplicação.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Mesmas permissões para todos os usuários. |
| S | 2 | Conjuntos de permissões em um mesmo nível. Ex.: (Interno **ou** Externo), (Consultor **ou** Operador). |
| M | 3 | Conjuntos de permissões que abrangem **dois ou mais níveis de profundidade**. Ex.: Usuário Externo: Operador ou Analista de Contratos; Usuário Interno: Analista de Crédito. |
| N/A | 0 | *Não recomendado — Papéis/Permissões são sempre obrigatórios* |

**Tamanhos válidos: XS · S · M**

---

### 4. Variações de Solução

> Soluções que cumprem um mesmo objetivo de negócio podendo variar (ligeira ou significativamente) por influência de um parâmetro.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Solução **única** para o fluxo de negócio. |
| ~~S~~ | — | *Não aplicável a esta dimensão* |
| M | 3 | Solução comum com **pequenas** alterações de comportamento de acordo com o valor de um parâmetro. |
| ~~L~~ | — | *Não aplicável a esta dimensão* |
| XL | 8 | Solução varia **significativamente** de acordo com o valor de um parâmetro. |

**Tamanhos válidos: XS · M · XL**

---

### 5. Fronteiras

> Interações que um Backlog Item possui com fontes/destinos de dados em função da propriedade, validade e durabilidade das informações trocadas.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Tela e/ou banco de dados, ou não atravessa fronteiras (auto-contido). |
| S | 2 | Leitura, escrita, troca de informações com **device físico**. |
| M | 3 | Serviço de negócio remoto com troca de informações **perenes** (duradouras, persistidas). |
| ~~L~~ | — | *Não aplicável a esta dimensão* |
| XL | 8 | Serviço de negócio remoto com troca de informações **voláteis** (efêmeras, não persistidas). |

**Tamanhos válidos: XS · S · M · XL**

> Cada sistema/serviço externo integrado é uma **Ocorrência separada** de Fronteiras.

---

### 6. Entidades de Domínio

> Quantidade de entidades que possuem semântica de negócio envolvidas no domínio de um Backlog Item.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | **1** entidade |
| S | 2 | **2 ou 3** entidades |
| M | 3 | **4 ou 5** entidades |
| L | 5 | **6 ou 7** entidades |
| XL | 8 | **Mais que 7** entidades |

**Tamanhos válidos: XS · S · M · L · XL**

> Sempre 1 Ocorrência. A Qtde representa o total de entidades contadas.
> Incluir todas entidades lidas, escritas ou referenciadas pela story.

---

### 7. Novas Entidades de Domínio

> Quantidade de entidades incorporadas ao domínio de negócio ou modificadas pelo Backlog Item.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| ~~XS~~ | — | *Não aplicável a esta dimensão* |
| S | 2 | Adiciona novos **atributos ou relacionamentos** para até 3 Entidades **existentes**. |
| ~~M~~ | — | *Não aplicável a esta dimensão* |
| L | 5 | Adiciona ao contexto de negócio até 3 **novas Entidades**. |
| ~~XL~~ | — | *Não aplicável a esta dimensão* |
| N/A | 0 | Não há criação nem modificação estrutural de entidades. |

**Tamanhos válidos: S · L · N/A**

---

### 8. Processos em Segundo Plano

> Processos disparados de maneira indireta (stealth), que não impedem a utilização do sistema durante a execução.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| ~~XS~~ | — | *Não aplicável a esta dimensão* |
| S | 2 | Processo disparado por um **evento do sistema**. Ex.: avaliação de crédito quando todas aprovações foram feitas. |
| M | 3 | Processo **agendado**. Ex.: processo que finaliza todos os dias às 11h. |
| L | 5 | Processo agendado que pode ser **disparado manualmente**. Ex.: finalização manual do ciclo de pedidos. |
| XL | 8 | Processo **externo e independente**. Ex.: nova aplicação executada fora do sistema principal. |
| N/A | 0 | Não há processos em segundo plano. |

**Tamanhos válidos: S · M · L · XL · N/A**

---

### 9. Notificações

> Avisos de ocorrência de eventos em um Backlog Item.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Envio de e-mail, textos de notificação de sistema, SMS ou notificações de hardware. |
| N/A | 0 | Não há notificações. |

**Tamanhos válidos: XS · N/A**

> Cada **tipo** de notificação (e-mail, SMS, push) pode ser uma Ocorrência separada.

---

### 10. Auditorias

> Registro de informações de identificação (data e responsável) associados a manipulações de negócio sobre Entidades de Domínio.

| Tamanho | Pts | Critério |
|---------|-----|---------|
| XS | 1 | Trilha de auditoria para **uma** Entidade. |
| N/A | 0 | Não há requisito de auditoria. |

**Tamanhos válidos: XS · N/A**

> Uma Ocorrência por Entidade auditada.

---

## Resumo — Tamanhos Válidos por Dimensão

| Dimensão | XS | S | M | L | XL | N/A | Obrigatório? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Regras de Negócio | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ | **SIM** |
| Elementos de Interface | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | Não |
| Papéis/Permissões | ✅ | ✅ | ✅ | ❌ | ❌ | ⚠️ | **SIM** |
| Variações de Solução | ✅ | ❌ | ✅ | ❌ | ✅ | ⚠️ | **SIM** |
| Fronteiras | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ | **SIM** |
| Entidades de Domínio | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | **SIM** |
| Novas Entidades de Domínio | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ | Não |
| Processos em Segundo Plano | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | Não |
| Notificações | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | Não |
| Auditorias | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | Não |

> ⚠️ N/A tecnicamente permitido mas **não recomendado** para dimensões obrigatórias.

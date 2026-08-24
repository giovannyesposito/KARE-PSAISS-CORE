# Exemplos Reais de Contagem BCP

> Exemplos extraídos da planilha oficial "Contagem BCPs.xlsx" de um programa de referência.
> Usados como referência para calibrar contagens futuras.

---

## Exemplo 1 — Envio de Dados ao MKT Cloud (Abandono de Carrinho)

**Contexto da Story:** Criação de novos campos para envio de informações ao MKT Cloud
no evento de abandono de carrinho no Hybris. Captar dados necessários e enviá-los
ao sistema de Marketing Cloud.

### Tabela de Contagem

| Item de Complexidade | Ocorrências | Qtde | Racional | Complexidade | Pontos |
|---|---|---|---|---|---|
| Regras de Negócio | 1 | — | Criar novos campos para envio das informações ao MKT Cloud. Ponto de Processamento: Abandono do carrinho, captação dos dados e envio ao MKT Cloud. Ponto de interrupção: MKT Cloud receber os dados. | M | 3 |
| Regras de Negócio | 1 | — | Comportamento do envio dos dados para o MKT Cloud. Enviar os campos com um escopo definido. Ponto de interrupção: MKT Cloud receber os dados. | XS | 1 |
| Elementos de Interface | 0 | 0 | n/a | N/A | 0 |
| Papéis/Permissões | 1 | — | Mesmas permissões para todos os usuários. | XS | 1 |
| Variações de Solução | 1 | — | Solução única de negócio. | XS | 1 |
| Entidades de Domínio | 1 | 4 | Produto, Cliente, Carrinho, Empresa. | XL | 8 |
| Fronteiras | 1 | — | Hybris / GTW / MKT Cloud | M | 3 |
| Novas Entidades de Domínio | 0 | 0 | n/a | N/A | 0 |
| Processos em Segundo Plano | 0 | 0 | n/a | N/A | 0 |
| Notificações | 1 | — | Push notification | XS | 1 |
| Auditorias | 0 | 0 | n/a | N/A | 0 |
| **TOTAL** | | | | | **18** |

### Análise do Exemplo

- **2 Ocorrências de Regras de Negócio:** A story tem duas regras distintas — uma para captação/envio (processo iterativo com poucos passos e decisões → M) e outra para o comportamento do envio (instrução direta com escopo definido → XS).
- **Entidades de Domínio como XL:** 4 entidades listadas (Produto, Cliente, Carrinho, Empresa), mas a contagem pode incluir entidades implícitas do sistema, resultando em classificação XL. *Atenção: 4 entidades pelos critérios formais seria M (3pts). Revisar com o time.*
- **Fronteiras M:** Integração com serviço remoto (MKT Cloud) trocando informações perenes (dados de clientes/pedidos).
- **Notificação XS:** Push notification é uma notificação de hardware → XS obrigatório.
- **Total: 18 BCPs**

---

## Exemplo 2 — Relatório de Carrinho Abandonado no Hybris

**Contexto da Story:** Criação de modelo de relatório de carrinho abandonado no Hybris.
Captar dados das bases necessárias, consolidar no relatório e enviar os campos em
ordem pré-determinada. Exportar em formato XLS ou CSV.

### Tabela de Contagem

| Item de Complexidade | Ocorrências | Qtde | Racional | Complexidade | Pontos |
|---|---|---|---|---|---|
| Regras de Negócio | 1 | — | Criação do modelo de relatório de carrinho abandonado. Captar dados, consolidar e enviar em ordem pré-determinada. Ponto de interrupção: visualizar os dados após a geração. | M | 3 |
| Regras de Negócio | 1 | — | Geração do arquivo no formato XLS ou CSV. | XS | 1 |
| Elementos de Interface | 0 | 0 | n/a | N/A | 0 |
| Papéis/Permissões | 1 | — | Mesmas permissões para todos os usuários. | XS | 1 |
| Variações de Solução | 1 | — | Solução única de negócio. | XS | 1 |
| Entidades de Domínio | 1 | 4 | Produto, Cliente, Carrinho, Empresa. | XL | 8 |
| Fronteiras | 1 | — | Hybris / GTW / MKT Cloud | M | 3 |
| Novas Entidades de Domínio | 0 | 0 | n/a | N/A | 0 |
| Processos em Segundo Plano | 0 | 0 | n/a | N/A | 0 |
| Notificações | 0 | 0 | n/a | N/A | 0 |
| Auditorias | 0 | 0 | n/a | N/A | 0 |
| **TOTAL** | | | | | **17** |

### Análise do Exemplo

- **Diferença chave vs Exemplo 1:** Sem Notificações (este relatório não dispara notificações) → 1 BCP a menos.
- **Regra de Negócio XS:** A geração do arquivo (XLS/CSV) é uma instrução direta e simples → XS.
- **Total: 17 BCPs**

---

## Padrões Identificados nos Exemplos

### 1. Múltiplas Regras de Negócio são comuns
Quase toda story tem 2+ ocorrências de Regras de Negócio. Uma regra de orquestração
do processo (geralmente M ou XL) e uma ou mais regras de validação/output simples (XS ou S).

### 2. Itens obrigatórios com valor mínimo
Quando uma story não tem complexidade especial em Papéis/Permissões ou Variações de
Solução, ambos recebem XS (1pt cada) — mas nunca N/A.

### 3. Fronteiras por integração
Cada serviço externo integrado pode ser uma ocorrência. No caso Hybris → GTW → MKT Cloud,
como são três sistemas, poderia ser contado como 1 Fronteira M (perene) ou até 3 ocorrências
dependendo do grau de especificidade da análise.

### 4. Racional documentado no Jira
O campo "Racional" deve ser suficientemente descritivo para ser colado diretamente no Jira
como evidência da contagem. Inclui:
- Ponto de Processamento (o que acontece)
- Ponto de Interrupção (quando a regra termina)

---

## Template para Nova Contagem

Use este template em branco para iniciar uma nova contagem:

```markdown
## Contagem BCP — [Título da Story / US-XXX]

**Story:** Como [persona], quero [ação] para [benefício].
**Referência:** [US-XXX / link Jira]

| Item de Complexidade | Ocorrências | Qtde | Racional | Complexidade | Pontos |
|---|---|---|---|---|---|
| Regras de Negócio | | | | | |
| Elementos de Interface | | | | N/A | 0 |
| Papéis/Permissões | | | | | |
| Variações de Solução | | | | | |
| Fronteiras | | | | | |
| Entidades de Domínio | | | | | |
| Novas Entidades de Domínio | | | | N/A | 0 |
| Processos em Segundo Plano | | | | N/A | 0 |
| Notificações | | | | N/A | 0 |
| Auditorias | | | | N/A | 0 |
| **TOTAL** | | | | | **0** |
```

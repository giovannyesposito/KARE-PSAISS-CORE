---
description: "Conta Business Complexity Points (BCPs) de User Stories usando a régua CI&T com 10 dimensões de complexidade"
command: /contagem-bcp
category: Backlog
orchestrator: kare-orchestrator
orchestrator-mode: sequential
agents-required:
   - primary: "@backlog-architect"
     secondary: ["@story-crafter"]
context-required:
   - BACKLOG.md
disclaimer: "📊 Analisa cada dimensão da régua BCP (CI&T) e calcula o total de pontos. Requer story ou descrição do Backlog Item. Tempo: 3-5 min. Saídas: Tabela BCP com racional por dimensão"
---

# /contagem-bcp Workflow

## O que faz

Realiza a contagem de **Business Complexity Points (BCP)** para um ou mais
Backlog Items usando a régua CI&T de 10 dimensões. Produz tabela auditável
com racional por dimensão, pronta para colar no Jira.

## O que NÃO faz

- Não substitui a estimativa de esforço (story points de engenharia)
- Não valida critérios de aceite (use `/story` para isso)
- Não planeja sprint (use `/sprint` para isso)

## Skill Requerida

> **Carregar obrigatoriamente:** `.agent/skills/bcp-counting/SKILL.md`
> Régua completa: `.agent/skills/bcp-counting/references/BCP_RULER_PT.md`
> Exemplos reais: `.agent/skills/bcp-counting/references/COUNTING_EXAMPLES.md`

## Passos

// turbo
1. Ler a skill BCP:
   - `.agent/skills/bcp-counting/SKILL.md`
   - `.agent/skills/bcp-counting/references/BCP_RULER_PT.md`

// turbo
2. Ler o Backlog Item alvo:
   - Se `--story US-XXX`: localizar story no BACKLOG.md ou arquivo da story
   - Se descrição inline: usar o texto fornecido diretamente
   - Se `--all`: listar todas as stories sem BCP no BACKLOG.md

3. Para **cada** Backlog Item, executar contagem dimensão por dimensão:

   a. **Regras de Negócio** (obrigatório)
      - Identificar cada regra distinta → 1 linha por regra
      - Tamanhos válidos: XS · S · M · XL
      - Documentar: Ponto de Processamento + Ponto de Interrupção

   b. **Elementos de Interface** (opcional)
      - Verificar se há alterações de UI
      - Aplicar regra dos 5: grupos de até 5 elementos = 1 Ocorrência
      - Tamanhos válidos: S · M · L · XL · N/A

   c. **Papéis/Permissões** (obrigatório — mínimo XS)
      - Identificar quem acessa e se há diferentes níveis
      - Tamanhos válidos: XS · S · M

   d. **Variações de Solução** (obrigatório — mínimo XS)
      - Verificar se o comportamento varia por parâmetro
      - Tamanhos válidos: XS · M · XL

   e. **Fronteiras** (obrigatório — mínimo XS)
      - Listar todos os sistemas externos integrados
      - 1 Ocorrência por sistema/serviço
      - Tamanhos válidos: XS · S · M · XL

   f. **Entidades de Domínio** (obrigatório)
      - Listar TODAS as entidades de negócio envolvidas
      - 1 Ocorrência com Qtde = total de entidades
      - Tamanhos válidos: XS (1) · S (2-3) · M (4-5) · L (6-7) · XL (>7)

   g. **Novas Entidades de Domínio** (opcional)
      - Verificar criação ou modificação estrutural de entidades
      - Tamanhos válidos: S · L · N/A

   h. **Processos em Segundo Plano** (opcional)
      - Verificar processos stealth, agendamentos, eventos
      - Tamanhos válidos: S · M · L · XL · N/A

   i. **Notificações** (opcional)
      - Verificar e-mails, SMS, push notifications, alertas
      - Tamanho único válido: XS · N/A

   j. **Auditorias** (opcional)
      - Verificar trilha de auditoria por entidade
      - Tamanho único válido: XS · N/A

4. Calcular total: `BCPs = Σ pontos de todas as Ocorrências`

5. Apresentar tabela no formato padrão (ver seção Formato de Saída)

6. Se `--all` ou múltiplas stories: gerar resumo comparativo ao final

## Uso

```
/contagem-bcp [descrição inline da story]
/contagem-bcp --story US-42
/contagem-bcp --story US-42 --story US-43
/contagem-bcp --all
/contagem-bcp --sprint N
```

## Formato de Saída

```markdown
## Contagem BCP — [Título / US-XXX]

| Item de Complexidade | Ocorrências | Qtde | Racional | Complexidade | Pontos |
|---|---|---|---|---|---|
| Regras de Negócio | 1 | — | [descrição da regra — Ponto de Processamento / Ponto de Interrupção] | M | 3 |
| Elementos de Interface | 0 | 0 | n/a | N/A | 0 |
| Papéis/Permissões | 1 | — | [justificativa] | XS | 1 |
| Variações de Solução | 1 | — | [justificativa] | XS | 1 |
| Fronteiras | 1 | — | [sistema(s) integrado(s)] | M | 3 |
| Entidades de Domínio | 1 | N | [lista de entidades] | ? | ? |
| Novas Entidades de Domínio | 0 | 0 | n/a | N/A | 0 |
| Processos em Segundo Plano | 0 | 0 | n/a | N/A | 0 |
| Notificações | 0 | 0 | n/a | N/A | 0 |
| Auditorias | 0 | 0 | n/a | N/A | 0 |
| **TOTAL** | | | | | **?** |

> 🔴 Itens obrigatórios (nunca N/A): Regras de Negócio · Papéis/Permissões ·
> Variações de Solução · Entidades de Domínio · Fronteiras
```

> **Dica:** O conteúdo da tabela pode ser colado diretamente no campo de
> comentário/descrição do Jira.

## Validações Automáticas

Antes de apresentar o resultado, verificar:

- [ ] Todos os 5 itens obrigatórios têm Ocorrências > 0 e Complexidade ≠ N/A
- [ ] Nenhum tamanho inválido foi usado (ex.: L em Regras de Negócio)
- [ ] Racional preenchido para cada Ocorrência
- [ ] Total calculado corretamente (soma de todos os Pontos)

Se alguma validação falhar: apontar o erro e sugerir correção antes de exibir o total.

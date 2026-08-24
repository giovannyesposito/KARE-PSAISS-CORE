# Direcional de Solução — {{CAP_ID}}

> **Status:** ⏳ PENDENTE APROVAÇÃO | **Data:** {{Mês Ano}} | **Demanda:** {{INI_ID}} — {{INI_NOME}}

---

## 1. Identificação

| Campo | Valor |
|---|---|
| **ID da Capability** | {{CAP_ID}} |
| **Título** | {{CAP_TITULO}} |
| **Iniciativa** | {{INI_ID}} — {{INI_NOME}} |
| **Arquiteto Responsável** | {{ARQUITETO}} |
| **Data** | {{DATA}} |

---

## 2. Visão Geral da Solução

{{Descreva em 2-3 parágrafos o que será construído, qual problema resolve e qual a abordagem técnica escolhida.}}

---

## 3. Decisões Arquiteturais

| ID | Decisão | Alternativas Consideradas | Motivo da Escolha |
|---|---|---|---|
| {{ADR_ID}} | {{decisão}} | {{alternativas}} | {{motivo}} |

---

## 4. Stack Tecnológica

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| Frontend | {{tech}} | {{versão}} | {{justificativa}} |
| Backend | {{tech}} | {{versão}} | {{justificativa}} |
| Dados | {{tech}} | {{versão}} | {{justificativa}} |
| Integração | {{tech}} | {{versão}} | {{justificativa}} |

---

## 5. Arquitetura de Alto Nível

```
{{Diagrama ASCII ou link para draw.io/Miro}}
```

---

## 6. Integrações

| Sistema | Tipo | Protocolo | Responsável |
|---|---|---|---|
| {{sistema}} | Entrada / Saída / Bidirecional | REST / Event / Batch | {{time}} |

---

## 7. Sequência de Entrega

| Sprint | Features / Capabilities | Dependências |
|---|---|---|
| Sprint {{N}} | {{o que entrega}} | {{dependências}} |
| Sprint {{N+1}} | {{o que entrega}} | {{dependências}} |

---

## 8. Riscos Técnicos

| ID | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| R-01 | {{risco}} | Alta / Média / Baixa | Alto / Médio / Baixo | {{mitigação}} |

---

## 9. Critérios de Saúde Técnica

- [ ] Cobertura de testes ≥ {{N}}%
- [ ] Latência P95 ≤ {{N}}ms
- [ ] Zero breaking changes em contratos existentes
- [ ] ADRs registrados para todas as decisões relevantes

---

## 10. Rastreabilidade

| Artefato | Referência |
|---|---|
| Jira Capability | [{{CAP_ID}}]({{jira_url}}) |
| ADRs | {{ADR_IDs}} |
| PRD | [PRD — {{INI_ID}}]({{confluence_url}}) |

# Detalhamento de História de Usuário — {{US_ID}}

> **Status:** ⏳ PENDENTE APROVAÇÃO | **Data:** {{Mês Ano}} | **Demanda:** {{INI_ID}} — {{INI_NOME}}

---

## 1. Identificação

| Campo | Valor |
|---|---|
| **ID da Story** | {{US_ID}} |
| **Título** | {{US_TITULO}} |
| **Feature** | {{FEAT_ID}} — {{FEAT_TITULO}} |
| **Iniciativa** | {{INI_ID}} — {{INI_NOME}} |
| **PI / Sprint** | {{PI}} / Sprint {{SPRINT}} |
| **Squad** | {{SQUAD}} |
| **Tech Lead** | {{TECH_LEAD}} |

---

## 2. Story Statement

**Como** {{persona}}  
**quero** {{ação}}  
**para** {{benefício}}.

---

## 3. Contexto e Motivação

{{Descreva o contexto de negócio que gerou esta story. Por que ela existe? Qual dor resolve?}}

---

## 4. Regras de Negócio

| ID | Regra |
|---|---|
| RN-01 | {{regra}} |
| RN-02 | {{regra}} |

---

## 5. Critérios de Aceite (Gherkin)

```gherkin
Feature: {{US_TITULO}}

  Scenario: {{AC_01_TITULO}}
    Given {{contexto}}
    When {{ação}}
    Then {{resultado esperado}}

  Scenario: {{AC_02_TITULO}}
    Given {{contexto}}
    When {{ação}}
    Then {{resultado esperado}}
```

---

## 6. Casos de Borda / Exceções

| Cenário | Comportamento Esperado |
|---|---|
| {{caso}} | {{comportamento}} |

---

## 7. Integrações e Dependências

- **Sistemas impactados:** {{sistemas}}
- **APIs / Endpoints:** {{endpoints}}
- **Dependências de outras stories:** {{US_IDs}}

---

## 8. Protótipos / Mockups

{{Link para Figma ou descrição visual da interface}}

---

## 9. Notas de Implementação

{{Orientações técnicas relevantes para o time de desenvolvimento}}

---

## 10. Rastreabilidade

| Artefato | Referência |
|---|---|
| Jira | [{{US_ID}}]({{jira_url}}) |
| ADR relacionado | {{ADR_ID}} |
| Confluence pai | [{{INI_ID}} — {{INI_NOME}}]({{confluence_url}}) |

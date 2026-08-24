---
name: servicenow-developer
description: >
  Agente especialista em ServiceNow para o projeto: GlideScript,
  workflows de Service Order Management (SOM), REST integrations,
  Business Rules, Script Includes e catálogo de serviços B2B do projeto.
sprint: 6
agente_destino: "@servicenow-developer (novo agente)"
framework: "ServiceNow Platform"
referencia: "https://developer.servicenow.com/dev.do"
tools:
  - Read
  - Grep
  - Write
  - Edit
triggers:
  - "servicenow"
  - "glide"
  - "SOM"
  - "service order"
  - "business rule"
  - "script include"
  - "catálogo servicenow"
  - "workflow servicenow"
activation: on-demand
---

# ServiceNow Developer — SOM e Automações B2B

> **Sprint 6 — Stack SaaS** | Framework: ServiceNow | Agente: `@servicenow-developer`

## Propósito

Agente especialista na instância ServiceNow do projeto, focado no módulo Service Order
Management (SOM) utilizado pelo projeto para orquestrar pedidos B2B desde
a venda até a ativação do serviço.

---

## Módulos ServiceNow

| Módulo | Uso | Tecnologia |
|---|---|---|
| Service Order Management (SOM) | Orquestração de pedidos B2B | GlideScript + Flow Designer |
| Service Catalog | Produtos B2B (fibra, VPN, SD-WAN) | Catalog Builder + Variables |
| Integrations Hub | Integração com Salesforce, BRM, HPE-SD | IntegrationHub + REST Steps |
| ITSM | Incident/Change Management TI | Business Rules + Notifications |
| Customer Service Management (CSM) | Portal B2B do cliente | CMS + Agent Workspace |

---

## GlideScript — Padrões

### Business Rule (Server-side)

```javascript
// Business Rule: Validar CNPJ em Service Order
// Tabela: x_kare_som_service_order
// When: before insert, before update
// Condition: (new) cnpj changed

(function executeRule(current, previous) {
    var cnpj = current.cnpj.toString().replace(/[^\d]/g, '');

    if (!validarFormatoCNPJ(cnpj)) {
        current.setAbortAction(true);
        gs.addErrorMessage('CNPJ inválido: ' + current.cnpj);
        return;
    }

    // Verificar unicidade (INI-001: múltiplos CNPJs por conta)
    var gr = new GlideRecord('x_kare_som_service_order');
    gr.addQuery('cnpj', cnpj);
    gr.addQuery('state', '!=', 'cancelled');
    gr.addQuery('sys_id', '!=', current.sys_id.toString());
    gr.query();

    if (gr.next()) {
        // Avisar mas não bloquear — múltiplos CNPJs são permitidos
        gs.addInfoMessage('CNPJ já possui pedido ativo: ' + gr.number);
    }
})(current, previous);

function validarFormatoCNPJ(cnpj) {
    return /^\d{14}$/.test(cnpj) && cnpj !== '00000000000000';
}
```

---

### Script Include (Reusável)

```javascript
var KareSOMUtils = Class.create();
KareSOMUtils.prototype = {
    initialize: function() {},

    getServiceOrdersByAccount: function(accountSysId) {
        var orders = [];
        var gr = new GlideRecord('x_kare_som_service_order');
        gr.addQuery('account', accountSysId);
        gr.orderByDesc('opened_at');
        gr.setLimit(50);
        gr.query();
        while (gr.next()) {
            orders.push({
                number: gr.number.toString(),
                state: gr.state.toString(),
                product: gr.product_name.toString(),
                cnpj: gr.cnpj.toString(),
                created: gr.opened_at.toString()
            });
        }
        return orders;
    },

    type: 'KareSOMUtils'
};
```

---

## Flow Designer — Workflow de Pedido B2B

```
[Início] → Receber Pedido (Salesforce webhook)
         → Validar CNPJ e conta
         → Verificar elegibilidade do produto
         → [Fork] Tipo de produto
            ├── Fibra Corporativa → Provisionar HPE-SD
            ├── VPN → Configurar roteador
            └── Mobile B2B → Provisionar BSIM
         → Notificar cliente (email + portal)
         → Atualizar BRM (faturamento)
         → [Fim] Pedido Ativado
```

---

## Integração ServiceNow ↔ Salesforce

```javascript
// REST Message para notificar Salesforce após ativação
var rm = new sn_ws.RESTMessageV2('Salesforce_Integration', 'UpdateOpportunityStatus');
rm.setStringParameterNoEscape('opportunity_id', current.salesforce_opportunity_id.toString());
rm.setStringParameterNoEscape('status', 'Activated');
rm.setStringParameterNoEscape('activation_date', current.activation_date.toString());

var response = rm.execute();
if (response.getStatusCode() !== 200) {
    gs.log('Erro ao notificar Salesforce: ' + response.getBody(), 'KareSOM');
}
```

---

## Critérios de Aceite

- [ ] Business Rules com validação de CNPJ para SOM
- [ ] Script Includes modulares e reutilizáveis
- [ ] Integração ServiceNow ↔ Salesforce via REST Message
- [ ] Fluxos SOM documentados no Flow Designer
- [ ] Testes ATF (Automated Test Framework) >= 80% de cobertura

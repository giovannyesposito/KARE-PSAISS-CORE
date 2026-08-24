---
name: elastic-observability
description: >
  Agente especialista em observabilidade do projeto via Elastic Stack:
  ingestão de eventos Kafka → Logstash/Vector → Elasticsearch, dashboards
  Kibana para SLO/SLA, alertas de anomalia e correlação de logs entre os
  sistemas distribuídos B2B (Salesforce, ServiceNow, BRM, HPE-SD).
sprint: 7
agente_destino: "@elastic-observability (novo agente)"
framework: "Elastic Stack (ELK) + Vector"
referencia: "https://www.elastic.co/guide/en/observability/current/index.html"
tools:
  - Read
  - Grep
  - Write
  - Edit
triggers:
  - "elastic"
  - "kibana"
  - "logstash"
  - "elasticsearch"
  - "observabilidade"
  - "SLO"
  - "alertas"
  - "logs"
  - "APM"
  - "ELK"
---

# Elastic Observability — Monitoramento B2B

> **Sprint 7 — DevOps e Infraestrutura** | Framework: Elastic Stack | Agente: `@elastic-observability`

## Propósito

Agente especialista na plataforma de observabilidade do projeto,
responsável por configurar ingestão de logs/eventos, dashboards de SLO/SLA
e alertas para os sistemas distribuídos B2B.

---

## Arquitetura de Ingestão

```
[Salesforce Platform Events] ─────┐
[ServiceNow Syslog] ──────────────┼──► [Vector/Logstash] ──► [Elasticsearch]
[Kafka Consumer Logs] ────────────┤                                 │
[BRM REST Logs] ──────────────────┘                                 │
[HPE-SD API Logs] ────────────────────────────────────────          │
                                                                     ▼
                                                              [Kibana Dashboards]
                                                              [Elastic Alerts]
                                                              [SLO/SLA Reports]
```

---

## Vector Pipeline — Kafka → Elasticsearch

```toml
# vector.toml — Ingestão de eventos Kafka do projeto

[sources.kafka_KARE]
type = "kafka"
bootstrap_servers = "kafka-broker-1:9092,kafka-broker-2:9092"
topics = [
    "KARE.orders.created",
    "KARE.orders.completed",
    "KARE.brm.responses",
    "KARE.hpesd.activated"
]
group_id = "vector-observability"
key_field = "kafka_key"

# Enriquecer com metadados
[transforms.enrich_events]
type = "remap"
inputs = ["kafka_KARE"]
source = '''
    .timestamp = now()
    .environment = get_env_var!("DEPLOY_ENV")
    .program = "KARE"
    .pi_planning = "CLOCK02-26"

    # Extrair correlationId para rastreamento Saga
    .correlation_id = .payload.correlationId ?? "unknown"

    # Classificar severidade por tipo de evento
    .severity = if includes(["KARE.orders.completed"], .topic) {
        "INFO"
    } else if includes(["KARE.brm.responses"], .topic) && .payload.success == false {
        "ERROR"
    } else {
        "DEBUG"
    }
'''

[sinks.elasticsearch_KARE]
type = "elasticsearch"
inputs = ["enrich_events"]
endpoints = ["https://elasticsearch:9200"]
index = "KARE-events-%Y.%m.%d"
auth.strategy = "basic"
auth.user = "${ES_USER}"
auth.password = "${ES_PASSWORD}"
```

---

## SLO Definitions — Kibana

```yaml
# SLOs do projeto — Kafka → Elasticsearch via API

# SLO 1: Taxa de sucesso de pedidos B2B
- name: "Order Success Rate"
  indicator:
    type: kql_custom
    params:
      index: "KARE-events-*"
      filter: 'topic: "KARE.orders.completed"'
      good: 'payload.success: true'
      total: '*'
  objective: 0.995  # 99.5% SLO
  time_window:
    duration: 7d

# SLO 2: Latência de ativação
- name: "Order Activation Latency"
  indicator:
    type: metric_custom
    params:
      index: "KARE-events-*"
      filter: 'topic: "KARE.orders.completed"'
      good: 'payload.activationDurationMs: [0 TO 300000]'  # < 5 min
      total: 'topic: "KARE.orders.completed"'
  objective: 0.95  # 95% em < 5 minutos
```

---

## Alertas — Anomalias Críticas

```json
{
  "name": "KARE BRM Failures Spike",
  "rule_type_id": "metrics.alert.threshold",
  "params": {
    "criteria": [{
      "metric": "count",
      "comparator": ">",
      "threshold": [10],
      "timeSize": 5,
      "timeUnit": "m",
      "customMetric": {
        "filter": "topic: KARE.brm.responses AND payload.success: false"
      }
    }],
    "sourceId": "default"
  },
  "actions": [{
    "id": "teams-webhook",
    "params": {
      "message": "ALERTA: {{context.value}} falhas no BRM nos últimos 5 minutos"
    }
  }]
}
```

---

## Dashboard Kibana — Estrutura

| Painel | Métrica | Visualização |
|---|---|---|
| Order Success Rate | % pedidos completados | Gauge + trend |
| Order Volume | Pedidos/hora | Bar chart |
| Error Distribution | Erros por sistema | Pie chart |
| Saga Trace | Duração do fluxo completo | Timeline |
| SLO Status | 99.5% meta | SLO widget |

---

## Critérios de Aceite

- [ ] Vector pipeline consumindo tópicos Kafka sem lag > 1000 mensagens
- [ ] Elasticsearch índices com ILM (rollover automático após 30 dias)
- [ ] SLO de taxa de sucesso (99.5%) e latência (95% < 5min) configurados
- [ ] Alertas no Teams/PagerDuty para spikes de erro
- [ ] Dashboard Kibana com 5 painéis principais do projeto

---
name: gcp-analytics-agent
description: >
  Agente especialista em analytics e dados no GCP para o projeto:
  BigQuery para data warehouse, Vertex AI para modelos de ML (churn prediction,
  propensão de venda B2B), Dataflow para pipelines de dados e integração com
  Kafka e Elasticsearch.
sprint: 8
agente_destino: "@gcp-analytics-agent (novo agente)"
framework: "GCP BigQuery + Vertex AI + Dataflow"
referencia: "https://cloud.google.com/bigquery/docs ; https://cloud.google.com/vertex-ai/docs"
tools:
  - Read
  - Grep
  - Write
  - Edit
triggers:
  - "bigquery"
  - "vertex AI"
  - "dataflow"
  - "GCP"
  - "machine learning"
  - "churn prediction"
  - "data warehouse"
  - "analytics B2B"
  - "propensão de compra"
---

# GCP Analytics Agent — Analytics e ML para o Projeto

> **Sprint 8 — Sistemas Legados e Cloud** | Framework: GCP BigQuery + Vertex AI | Agente: `@gcp-analytics-agent`

## Propósito

Agente especialista na plataforma GCP para analytics do projeto:
construção de pipelines de dados, modelos de ML para propensão de venda B2B,
predição de churn e dashboards de performance por iniciativa.

---

## Casos de Uso Analytics

| Caso de Uso | Tecnologia GCP | KPI |
|---|---|---|
| Churn Prediction B2B | BigQuery ML + Vertex AI | Reduzir churn em 15% |
| Propensão de Venda | Vertex AI Tabular | Aumentar conversão em 20% |
| Performance de INIs | BigQuery + Looker | Dashboard por PI Planning |
| Log Analysis | Dataflow + BigQuery | MTTR reduzido em 30% |
| Anomaly Detection | Vertex AI Anomaly | Detecção de fraude |

---

## BigQuery — Schema Data Warehouse

```sql
-- Dataset: KARE_dw
-- Tabela: orders_fact (Fato de Pedidos B2B)
CREATE TABLE `kare-analytics.KARE_dw.orders_fact`
PARTITION BY DATE(created_date)
CLUSTER BY account_id, product_code
AS (
  SELECT
    o.order_id,
    o.account_id,
    o.cnpj,
    o.billing_cnpj,                    -- INI-001: CNPJ de faturamento
    o.product_code,
    o.product_category,
    o.monthly_revenue_brl,
    o.status,
    o.activation_duration_minutes,
    DATE(o.created_at) AS created_date,
    DATE(o.activated_at) AS activation_date,
    -- Dimensões calculadas
    CASE
      WHEN o.activation_duration_minutes <= 5 THEN 'FAST'
      WHEN o.activation_duration_minutes <= 30 THEN 'NORMAL'
      ELSE 'SLOW'
    END AS activation_tier,
    -- SLO compliance
    o.activation_duration_minutes <= 300 AS slo_compliant  -- < 5 min SLO
  FROM `kare-analytics.raw.orders` o
);
```

---

## BigQuery ML — Modelo de Churn

```sql
-- Treinar modelo de churn para clientes B2B
CREATE OR REPLACE MODEL `kare-analytics.KARE_ml.churn_model`
OPTIONS(
  model_type = 'LOGISTIC_REG',
  input_label_cols = ['churned'],
  auto_class_weights = TRUE,
  max_iterations = 50
) AS
SELECT
  a.account_id,
  a.company_size_employees,
  a.months_as_customer,
  a.total_products_count,
  a.last_interaction_days_ago,
  a.avg_nps_score,
  a.open_tickets_count,
  a.payment_delays_last_12m,
  -- Target
  IF(a.status = 'CHURNED', 1, 0) AS churned
FROM `kare-analytics.KARE_dw.accounts_features` a
WHERE a.data_date = DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);

-- Avaliar modelo
SELECT * FROM ML.EVALUATE(MODEL `kare-analytics.KARE_ml.churn_model`);
-- Predizer churn para contas ativas
SELECT
  account_id,
  predicted_churned_probs[OFFSET(1)].prob AS churn_probability
FROM ML.PREDICT(MODEL `kare-analytics.KARE_ml.churn_model`,
  TABLE `kare-analytics.KARE_dw.accounts_features`)
WHERE churn_probability > 0.70
ORDER BY churn_probability DESC;
```

---

## Dataflow — Pipeline Kafka → BigQuery

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def run_KARE_pipeline():
    options = PipelineOptions([
        "--runner=DataflowRunner",
        "--project=kare-analytics",
        "--region=southamerica-east1",
        "--temp_location=gs://KARE-dataflow-temp/tmp",
        "--staging_location=gs://KARE-dataflow-temp/staging",
    ])

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read from Kafka" >> beam.io.ReadFromKafka(
                consumer_config={"bootstrap.servers": "kafka-broker:9092"},
                topics=["KARE.orders.completed"],
            )
            | "Parse JSON" >> beam.Map(lambda msg: json.loads(msg[1]))
            | "Enrich with Account Data" >> beam.ParDo(EnrichWithAccountDoFn())
            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table="kare-analytics:KARE_dw.orders_streaming",
                schema=ORDERS_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )
```

---

## Vertex AI — Deploy de Modelo

```python
from google.cloud import aiplatform

# Deploy modelo de churn para endpoint de predição em tempo real
aiplatform.init(project="kare-analytics", location="southamerica-east1")

model = aiplatform.Model.upload(
    display_name="KARE-churn-model-v2",
    artifact_uri="gs://KARE-models/churn-v2/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest",
)

endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=5,
    traffic_split={"0": 100},
)
```

---

## Guardrail — Autorização + Controle de Custo GCP

> ⛔ **NÍVEL: ALTO** — Jobs BigQuery e Vertex AI geram custo real e podem expor dados B2B.
> Autorização obrigatória + Budget Alert verificado antes de qualquer job de computação.

### Ativar antes de usar

```powershell
# 1. Autorizar (expira em 60 min)
python .agent/scripts/guards/guardrail_gate.py approve gcp-analytics-agent \
  --reason "Training churn model INI-XXX — dataset: synthetic — aprovado por <data-lead>"

# 2. Verificar status
python .agent/scripts/guards/guardrail_gate.py check gcp-analytics-agent
```

### Controles Obrigatórios no Código

```python
from guardrail_gate import require_authorization
import os

require_authorization("gcp-analytics-agent")

# Verificar que não há PII no dataset antes de qualquer job
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
assert PROJECT_ID, "GCP_PROJECT_ID não definido"
assert "prod" not in PROJECT_ID.lower() or os.getenv("FORCE_PROD") == "true", \
    "BLOQUEADO: Use projeto de staging. Defina FORCE_PROD=true apenas após revisão."

# Budget Alert — verificar antes de jobs pesados
BUDGET_LIMIT_USD = float(os.getenv("BQ_BUDGET_LIMIT_USD", "100"))
print(f"[GCP GUARD] Budget mensal configurado: US$ {BUDGET_LIMIT_USD}")
print("[GCP GUARD] Confirme que Budget Alert está ativo no GCP Console antes de continuar.")
```

### VPC Service Controls Obrigatório

Datasets BigQuery com dados B2B não podem ser acessados fora da VPC:
```hcl
# Sempre declarar no módulo Terraform do projeto GCP
resource "google_access_context_manager_service_perimeter" "bq_perimeter" {
  restricted_services = ["bigquery.googleapis.com", "aiplatform.googleapis.com"]
}
```

---

## Critérios de Aceite

- [ ] BigQuery DW particionado por data e clusterizado por account_id
- [ ] Modelo de churn com AUC >= 0.80 no conjunto de validação
- [ ] Pipeline Dataflow processando eventos em < 30s de latência
- [ ] Predições de churn exportadas para Salesforce via MuleSoft
- [ ] Custos BigQuery monitorados via Budget Alert (limite mensal definido)
- [ ] **Autorização `guardrail_gate.py approve` registrada antes de qualquer job**
- [ ] **`GCP_PROJECT_ID` aponta para ambiente de staging (não produção)**
- [ ] **VPC Service Controls ativo para BigQuery e Vertex AI**
- [ ] **Nenhum PII (CPF, CNPJ, nome) presente no dataset de treino**

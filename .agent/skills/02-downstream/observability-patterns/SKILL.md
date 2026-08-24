---
name: observability-patterns
description: >
  Patterns de observabilidade: logs estruturados, métricas, distributed tracing
  e SLOs. Define runbooks e alert strategy. Framework-agnóstico com exemplos
  para as principais stacks.
triggers:
  - "observabilidade"
  - "monitoring"
  - "logs"
  - "métricas"
  - "tracing"
  - "SLO"
  - "alertas"
  - "runbook"
---

# Observability Patterns Skill

## Os Três Pilares

```
┌─────────────────────────────────────────────────────┐
│                  OBSERVABILIDADE                     │
├─────────────┬─────────────────┬────────────────────┤
│    LOGS     │    MÉTRICAS     │     TRACING        │
│ Eventos     │ Agregações      │ Rastreamento       │
│ textuais    │ numéricas       │ distribuído        │
│ estruturados│ no tempo        │ entre serviços     │
│ (JSON)      │ (counters,      │ (spans, traces)    │
│             │ histogramas)    │                    │
└─────────────┴─────────────────┴────────────────────┘
```

---

## Logs Estruturados

### Formato obrigatório (JSON)

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "usr_789",
  "event": "payment_failed",
  "message": "Charge declined by gateway",
  "error": {
    "type": "GatewayDeclinedError",
    "code": "INSUFFICIENT_FUNDS",
    "stack": "[apenas em dev/staging]"
  },
  "context": {
    "payment_id": "pay_001",
    "amount_cents": 5000,
    "currency": "BRL"
  }
}
```

### Níveis de Log e quando usar

| Nível | Quando usar |
|-------|-------------|
| `ERROR` | Falha que requer atenção imediata (perda de dados, falha de integração) |
| `WARN` | Degradação não crítica, retry automático, behavior inesperado |
| `INFO` | Eventos de negócio relevantes (pedido criado, pagamento aprovado) |
| `DEBUG` | Diagnóstico de desenvolvimento (desabilitado em produção) |

### O que NUNCA logar:
```
❌ Senhas, tokens, chaves de API
❌ Dados pessoais completos (CPF, cartão, endereço)
❌ Conteúdo de requisições HTTP completo (pode ter PII)
```

---

## SLOs — Service Level Objectives

### Template de SLO

```markdown
## SLO — [Serviço]

### SLO 1 — Disponibilidade
- **SLI**: % de requests com status 2xx
- **Objetivo**: ≥ 99.5%
- **Janela**: 30 dias rolling
- **Error Budget**: 3.6 horas/mês

### SLO 2 — Latência
- **SLI**: p99 de latência de resposta
- **Objetivo**: ≤ 500ms para 99% das requests
- **Janela**: 7 dias rolling

### SLO 3 — Taxa de erro
- **SLI**: % de erros 5xx sobre total de requests
- **Objetivo**: ≤ 0.1%
- **Janela**: 24h rolling
```

### Error Budget Policy

```
Error Budget > 50% → Velocity normal
Error Budget 10-50% → Pausar features novas, foco em confiabilidade
Error Budget < 10% → Feature freeze, apenas fixes de reliability
Error Budget esgotado → Post-mortem obrigatório, release freeze
```

---

## Alert Strategy

### Rulesets por severidade

| Severidade | SLA de Resposta | Canal | Exemplos |
|-----------|----------------|-------|---------|
| P0 — Crítico | 5 min | PagerDuty + Slack | Sistema fora, DB down |
| P1 — Alto | 30 min | Slack + email | Error rate >1%, p99 >2s |
| P2 — Médio | 4h | Slack | Warning de capacity |
| P3 — Baixo | Next business day | Ticket | Drift de métricas |

### Alert Template

```yaml
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
for: 2m
labels:
  severity: P1
annotations:
  summary: "Error rate acima de 1% em {{ $labels.service }}"
  runbook: "https://wiki/runbooks/high-error-rate"
  dashboard: "https://grafana/d/xxx"
```

---

## Runbook Template

```markdown
# Runbook — [Nome do Alerta]

**Alert**: [nome exato do alerta]
**Severidade**: P0/P1/P2/P3
**Owner**: [time]

## Sintomas
[O que o usuário/sistema está experimentando]

## Diagnóstico Rápido (1-2 min)
\`\`\`bash
# Verificar status dos pods
kubectl get pods -n [namespace]

# Ver logs recentes do serviço
kubectl logs -n [namespace] deploy/[service] --tail=100

# Checar métricas chave
# [link direto para dashboard Grafana]
\`\`\`

## Causas Comuns e Ações
| Causa | Evidência | Ação |
|-------|-----------|------|
| Memory leak | RSS crescendo monotonicamente | Restart do pod |
| DB connection pool esgotado | Timeout em queries | Verificar conexões abertas |

## Escalação
- Não resolvido em 10 min → [pessoa/time]
- Impacto crítico → [pessoa/time + stakeholder]

## Pós-Incidente
- Criar ticket de follow-up
- Post-mortem se duração >30min
```

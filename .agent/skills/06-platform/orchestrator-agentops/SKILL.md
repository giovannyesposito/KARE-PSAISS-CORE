---
name: orchestrator-agentops
description: >
  Observabilidade do ecossistema KARE via AgentOps: rastreia chamadas LLM,
  uso de ferramentas, latência, erros e custo por sessão. Complementa o
  ORCHESTRATION_REPORT.md com métricas em tempo real. Framework: AutoGen.
sprint: 1
agente_destino: "@kare-orchestrator"
framework: AutoGen
referencia: "https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_agentops.ipynb"
tools:
  - Read
  - Grep
  - Write
  - mcp_mcp-atlassian_confluence_create_page
  - mcp_mcp-atlassian_jira_add_comment
triggers:
  - "agentops"
  - "observabilidade de agentes"
  - "rastrear chamadas LLM"
  - "custo por sessão"
  - "latência do agente"
  - "monitoramento KARE"
  - "auditoria de ferramentas"
  - "dashboard de uso"
---

# Orchestrator AgentOps — Observabilidade KARE

> **Sprint 1 — Fundação** | Framework: AutoGen | Agente: `@kare-orchestrator`

## Propósito

Rastrear **toda** interação do ecossistema KARE: chamadas LLM, ferramentas utilizadas,
latência por agente, custo estimado de tokens e erros — por sessão, por INI e por agente.

---

## Métricas Capturadas

| Métrica | Descrição | Alerta |
|---|---|---|
| `llm_calls` | Nº de chamadas ao modelo por sessão | > 50/sessão → revisar |
| `tool_calls` | Ferramentas invocadas com args resumidos | Loop detectado → HITL |
| `latency_p50/p99` | Tempo de resposta por agente | P99 > 10s → investigar |
| `token_cost_usd` | Custo estimado da sessão | > $0.50 → alertar |
| `errors` | Erros com stack trace por agente | Qualquer erro → log |
| `hitl_escalations` | Vezes que humano foi acionado | — |

---

## Integração com o Ecossistema KARE

### 1. Rastreamento de Sessão

Toda sessão KARE deve iniciar com:
```python
import agentops
agentops.init(api_key=os.environ["AGENTOPS_API_KEY"])

# Tagear por INI / contexto
agentops.start_session(tags=["ini-579", "sprint-1", "story-crafter"])
```

### 2. Rastreamento de Agente Customizado

```python
from agentops import track_agent, record_action

@track_agent(name="@story-crafter")
class StoryCrafter:
    @record_action("generate_story")
    def gerar_story(self, requisito: str) -> str:
        # ...geração da story
        pass
```

### 3. Encerramento com Métricas

```python
agentops.end_session(
    end_state="Success",
    end_state_reason="Story gerada e aprovada pelo DoR",
    video="<link-opcional>"
)
```

---

## Integração com Loop Guard

Quando `loop_guard.py` detectar repetição, registrar no AgentOps:

```python
from loop_guard import get_session_tracker, LoopDetectedError

tracker = get_session_tracker("sessao-id")
try:
    tracker.record("Bash", {"cmd": "pytest tests/"})
except LoopDetectedError as e:
    agentops.record(agentops.ErrorEvent(
        trigger_event=e,
        exception=e,
        init_timestamp=datetime.now().isoformat(),
        end_timestamp=datetime.now().isoformat()
    ))
    # HITL — parar e notificar
```

---

## Dashboard — Integração com telemetria SQLite

O AgentOps registra métricas via `kare_rag.py telemetry log` (banco `kare_telemetry.db`):

```python
# Registrar métricas da sessão no banco de telemetria
def export_session_to_telemetry(session_id: str) -> None:
    metrics = agentops.get_session_metrics(session_id)
    # kare_rag.py telemetry log --agent <nome> --action-type <tipo> ...
    _telem(
        action_type="planning" if not metrics["errors"] else "other",
        agent=metrics["agent_name"],
        tokens_in=metrics["total_tokens"],
        artifact_ref=metrics["tags"].get("ini", "global"),
    )
```

---

## Alertas por Threshold

| Condição | Severidade | Ação |
|---|---|---|
| `token_cost_usd > 0.50` | 🟠 ALTO | Log + alerta no chat |
| `latency_p99 > 10_000ms` | 🟡 MÉDIO | Log para otimização |
| `loop_detected = true` | 🔴 CRÍTICO | HITL imediato |
| `errors > 0` | 🟠 ALTO | Stack trace no ORCHESTRATION_REPORT |
| `hitl_escalations > 3` | 🔴 CRÍTICO | Pausar agente + revisão humana |

---

## ORCHESTRATION_REPORT — Seção AgentOps

Todo `ORCHESTRATION_REPORT.md` deve incluir:

```markdown
## AgentOps — Métricas da Sessão

| Agente | LLM Calls | Tokens | Custo | Latência P99 | Erros |
|--------|-----------|--------|-------|--------------|-------|
| @story-crafter | 8 | 12.450 | $0.12 | 2.3s | 0 |
| @test-engineer | 5 | 8.200 | $0.08 | 1.8s | 0 |

**Total:** 13 calls | 20.650 tokens | $0.20 | 0 erros
```

---

## Critérios de Aceite

- [ ] Custo por sessão rastreado e exportável por INI
- [ ] Latência por agente logada e disponível no dashboard
- [ ] Alertas automáticos para loops detectados (> 3 iterações)
- [ ] Integração com `kare_rag.py telemetry` (SQLite `kare_telemetry.db`)
- [ ] ORCHESTRATION_REPORT com seção AgentOps preenchida

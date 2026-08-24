---
name: delivery-observer-sql
description: >
  Agente que interpreta perguntas em linguagem natural sobre o estado do
  projeto e as converte em queries SQL contra o banco de dados do KARE
  (session_store.db / SQLite). Responde perguntas como "Quantas stories foram
  entregues no último sprint?". Framework: LangGraph.
sprint: 4
agente_destino: "@delivery-observer"
framework: LangGraph
referencia: "https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/sql-agent.ipynb"
tools:
  - Read
  - Grep
triggers:
  - "SQL agent"
  - "consulta ao banco"
  - "quantas stories"
  - "métricas de projeto"
  - "velocity"
  - "burn down"
  - "relatório de entrega"
  - "status do sprint"
---

# Delivery Observer SQL — Métricas via SQL em Linguagem Natural

> **Sprint 4 — Agentes de Planejamento** | Framework: LangGraph | Agente: `@delivery-observer`

## Propósito

Permitir que o `@delivery-observer` responda perguntas sobre o estado do projeto
diretamente a partir do banco SQLite do KARE — sem exigir conhecimento de SQL
do usuário.

---

## Perguntas Suportadas

| Pergunta (linguagem natural) | SQL Gerado | Resultado |
|---|---|---|
| "Quantas stories foram entregues este sprint?" | `SELECT COUNT(*) FROM stories WHERE status='done' AND sprint=N` | "12 stories entregues" |
| "Qual é a velocidade média das últimas 3 sprints?" | `SELECT AVG(pontos_entregues) FROM sprints ORDER BY id DESC LIMIT 3` | "34.7 story points" |
| "Quais stories estão em bloqueio?" | `SELECT id, titulo FROM stories WHERE status='blocked'` | Lista de stories |
| "Quanto do roadmap foi completado?" | `SELECT... percentual` | "67% do roadmap concluído" |

---

## Grafo LangGraph

```
Pergunta natural
       │
       ▼
[UNDERSTAND] — Identificar intenção e entidades
       │ (sprint_id, tipo_métrica, filtros)
       ▼
[GENERATE SQL] — Converter para SQL seguro
       │
       ▼
[VALIDATE SQL] — Verificar contra schema (somente SELECT)
       │
       ▼
[EXECUTE] — Executar via SQLite read-only connection
       │
       ▼
[FORMAT] — Converter resultado em resposta legível
```

---

## SQL Agent Seguro

```python
import sqlite3
import re

SCHEMA_PERMITIDO = """
Tables:
  - stories(id, titulo, epic_id, sprint_id, status, pontos, assignee, created_at)
  - sprints(id, nome, start_date, end_date, pontos_planejados, pontos_entregues)
  - epics(id, titulo, iniciativa, status, pontos_total)
  - sessions(id, agente, acao, timestamp, duracao_ms)
"""

def validar_sql(sql: str) -> bool:
    """Garante que apenas SELECT é executado (sem DDL/DML)."""
    sql_limpo = sql.strip().upper()
    if not sql_limpo.startswith("SELECT"):
        return False
    # Bloquear operações destrutivas
    proibidas = ["DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER", "EXEC"]
    return not any(p in sql_limpo for p in proibidas)

def executar_query(sql: str) -> list[dict]:
    """Executa query em modo read-only."""
    if not validar_sql(sql):
        raise SecurityError(f"SQL não permitido: {sql}")
    conn = sqlite3.connect("session_store.db", uri=True)  # read-only
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(sql)
    return [dict(row) for row in cursor.fetchall()]
```

---

## Formatação de Resposta

```python
def formatar_resposta(pergunta: str, dados: list[dict]) -> str:
    """Usa LLM para converter dados brutos em resposta natural."""
    return llm.invoke(f"""
    Pergunta original: {pergunta}
    Dados retornados: {dados}

    Responda a pergunta em linguagem natural, de forma concisa.
    Use markdown para tabelas quando houver múltiplas linhas.
    """)
```

---

## Guardrail — SQL Guard (SELECT-Only Enforcer)

> ⛔ **NÍVEL: CRÍTICO** — Queries são geradas por LLM a partir de linguagem natural.
> Um prompt malicioso pode induzir geração de DELETE/DROP. Toda query passa pelo `sql_guard.py`.

### Ativar antes de usar

```powershell
# 1. Autorizar a sessão (expira em 30 min)
python .agent/scripts/guards/guardrail_gate.py approve delivery-observer-sql \
  --reason "Consulta de métricas sprint N — autoria: <seu nome>"

# 2. Testar validação de query
python .agent/scripts/guards/sql_guard.py validate "SELECT count(*) FROM stories"
python .agent/scripts/guards/sql_guard.py validate "DELETE FROM stories"  # ← bloqueado
```

### Integração obrigatória no código

```python
from guardrail_gate import require_authorization
from sql_guard import safe_execute, open_readonly_connection, SQLGuardError

# 1. Verificar autorização da sessão
require_authorization("delivery-observer-sql")

# 2. Abrir conexão em modo READ-ONLY
conn = open_readonly_connection(".specify/session_store.db")

# 3. Executar APENAS via safe_execute (valida + audita + limita rows)
try:
    rows = safe_execute(conn, generated_sql_query)
except SQLGuardError as e:
    print(str(e))  # erro claro para o usuário
    rows = []
```

### Keywords Bloqueadas

`DELETE` `DROP` `UPDATE` `INSERT` `ALTER` `TRUNCATE` `ATTACH` `DETACH`
`PRAGMA` `CREATE` `REPLACE` `--` `/*` `xp_` `EXEC(` `EXECUTE(`

### Audit Log de Queries

Toda query executada é registrada em:
`.agent/.guardrails/sql_audit.jsonl` (timestamp + preview da query + resultado)

---

## Critérios de Aceite

- [ ] Somente queries SELECT executadas (segurança: sem DDL/DML)
- [ ] Resposta em linguagem natural a partir de dados SQLite
- [ ] Cobertura de métricas: velocity, burn-down, stories por status
- [ ] Tempo de resposta <= 2s para queries simples
- [ ] Schema validado antes de qualquer execução de query
- [ ] **`sql_guard.py validate` bloqueia DELETE/DROP/UPDATE em teste**
- [ ] **Conexão SQLite aberta em modo read-only (`?mode=ro`)**
- [ ] **Resultado limitado a 5.000 linhas com aviso de truncamento**
- [ ] **Audit log contém todas as queries executadas na sessão**

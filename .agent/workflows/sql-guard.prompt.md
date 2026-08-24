---
description: "Valida query SQL gerada por LLM — garante que apenas SELECT seja executado contra o banco KARE."
command: /sql-guard
category: Security
disclaimer: "🔒 Valida segurança de query SQL antes da execução. Bloqueia DELETE/DROP/UPDATE/INSERT e qualquer DDL. Somente leitura no banco. Tempo: < 2s."
---

# /sql-guard — Validar Query SQL Gerada por LLM

$ARGUMENTS

---

## O que faz

Executa o `sql_guard.py` para validar que uma query SQL gerada pelo agente
`delivery-observer-sql` é segura antes de ser executada. Bloqueia qualquer
operação que não seja `SELECT`, e keywords que indicam injection ou operações destrutivas.

Use **sempre** antes de executar qualquer query que venha de linguagem natural → SQL.

---

## Uso

```
/sql-guard "SELECT count(*) FROM stories WHERE sprint_id = 8"
/sql-guard "SELECT velocity, sprint_id FROM sprints ORDER BY sprint_id DESC LIMIT 5"
/sql-guard "DELETE FROM stories WHERE id = 42"          ← bloqueado
/sql-guard "SELECT * FROM sqlite_master"                ← bloqueado (tabela interna)
/sql-guard --log
/sql-guard --log --last 30
```

---

## Keywords Bloqueadas

Qualquer uma dessas keywords na query resulta em bloqueio imediato:

```
DELETE    DROP       UPDATE    INSERT    ALTER     TRUNCATE
ATTACH    DETACH     CREATE    REPLACE   VACUUM    PRAGMA
REINDEX   ANALYZE    --        /*        xp_       EXEC(
EXECUTE(  CAST(      CHAR(
```

Tabelas/views internas também bloqueadas:
```
sqlite_master    sqlite_sequence    information_schema
credentials      tokens             secrets
```

---

## Passos de Execução

1. Extrair query de `$ARGUMENTS`
   - Se `--log` → executar modo de log em vez de validação
   - Se query vazia → solicitar ao usuário

2. Executar validação:

```powershell
# Validar query
python .agent/scripts/guards/sql_guard.py validate "<query>"

# Ver log de queries anteriores
python .agent/scripts/guards/sql_guard.py log --last 20
```

3. Interpretar resultado:

   **✅ Query segura:**
   ```
   [SQL GUARD] ✅ Query segura: 'SELECT count(*) FROM stories'
   → Pronto para execução via safe_execute()
   ```

   **❌ Query bloqueada:**
   ```
   [SQL GUARD] ❌ Keyword proibida detectada: 'DELETE'
              Query: 'DELETE FROM stories WHERE id = 42'
   → NÃO executar. Revisar a pergunta original em linguagem natural.
   ```

4. Se bloqueada → sugerir alternativa segura:
   - Identificar a intenção original da pergunta
   - Reformular como SELECT equivalente
   - Exemplo: `"delete outdated stories"` → `"SELECT id, title FROM stories WHERE sprint_id < 3"` (para revisão manual)

5. Se aprovada → informar que a query pode ser executada via `safe_execute()` com conexão read-only

---

## Integração com `delivery-observer-sql`

```python
# Fluxo completo de uso seguro
from guardrail_gate import require_authorization
from sql_guard import safe_execute, open_readonly_connection

require_authorization("delivery-observer-sql")          # 1. autorização da sessão
conn = open_readonly_connection(".specify/session_store.db")  # 2. conexão somente leitura
rows = safe_execute(conn, generated_sql)                # 3. valida + executa + audita
```

---

## Saídas Esperadas

- ✅ Confirmação de segurança da query (pronta para execução)
- ❌ Bloqueio com motivo claro + sugestão de alternativa segura
- Entry no audit log: `.agent/.guardrails/sql_audit.jsonl`

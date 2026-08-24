#!/usr/bin/env python3
"""
KARE SQL Guard — Enforcer de Segurança para Queries Geradas por LLM

Garante que APENAS queries SELECT sejam executadas contra o banco SQLite do KARE.
Integrado ao skill `delivery-observer-sql`.

Uso standalone:
    python .agent/scripts/guards/sql_guard.py validate "SELECT * FROM metrics"
    python .agent/scripts/guards/sql_guard.py validate "DELETE FROM metrics"   # ← bloqueado

Uso como módulo:
    from sql_guard import safe_execute
    rows = safe_execute(conn, "SELECT count(*) FROM stories WHERE sprint=5")
"""

import re
import sys
import sqlite3
import argparse
import datetime
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
_BASE = Path(__file__).parents[2]  # .agent/ (script está em .agent/scripts/guards/)
_AUDIT_LOG = _BASE / ".guardrails" / "sql_audit.jsonl"
_AUDIT_LOG.parent.mkdir(exist_ok=True)

# Apenas estas operações são permitidas
ALLOWED_STMT_PREFIXES = ("SELECT",)

# Qualquer ocorrência dessas palavras (mesmo em comentários ou subqueries) bloqueia
BLOCKED_KEYWORDS = [
    "DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "ATTACH", "DETACH", "CREATE", "REPLACE", "VACUUM",
    "PRAGMA", "REINDEX", "ANALYZE",
    "--",        # comentário SQL inline (vetor de injection)
    "/*",        # comentário SQL bloco
    "xp_",       # SQL Server procs (defesa em profundidade)
    "EXEC(",     # dynamic exec
    "EXECUTE(",
    "CAST(",     # pode encobrir injection
    "CHAR(",     # ofuscação
]

# Colunas / tabelas nunca permitidas em queries externas
BLOCKED_TABLE_PATTERNS = [
    r"sqlite_master",
    r"sqlite_sequence",
    r"information_schema",
    r"credentials",
    r"tokens",
    r"secrets",
]

# Limite de segurança para resultado
MAX_ROWS = 5_000

# ---------------------------------------------------------------------------
# Funções de auditoria
# ---------------------------------------------------------------------------

def _log(event: str, query: str, details: dict = None) -> None:
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": event,
        "query_preview": query[:200],
        **(details or {}),
    }
    with open(_AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

class SQLGuardError(Exception):
    """Lançado quando uma query viola as políticas de segurança."""


def validate_query(query: str) -> None:
    """
    Valida a query SQL. Lança SQLGuardError se não for segura.
    Caso contrário retorna None.
    """
    if not query or not query.strip():
        raise SQLGuardError("Query vazia.")

    cleaned = query.strip()
    upper = cleaned.upper()

    # 1. Deve começar com SELECT
    if not upper.lstrip().startswith("SELECT"):
        raise SQLGuardError(
            f"[SQL GUARD] ❌ Apenas SELECT é permitido. "
            f"Query inicia com: {cleaned[:40]!r}"
        )

    # 2. Palavras-chave bloqueadas
    for kw in BLOCKED_KEYWORDS:
        if kw in upper:
            raise SQLGuardError(
                f"[SQL GUARD] ❌ Keyword proibida detectada: {kw!r}\n"
                f"           Query: {cleaned[:80]!r}"
            )

    # 3. Tabelas bloqueadas
    for pattern in BLOCKED_TABLE_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise SQLGuardError(
                f"[SQL GUARD] ❌ Acesso a tabela interna bloqueado: {pattern!r}"
            )

    # 4. Subquery infinita / CROSS JOIN sem WHERE (heurística básica)
    if "CROSS JOIN" in upper and "WHERE" not in upper:
        raise SQLGuardError(
            "[SQL GUARD] ❌ CROSS JOIN sem WHERE detectado — risco de tabela cartesiana."
        )


def safe_execute(
    conn: sqlite3.Connection,
    query: str,
    params: tuple = (),
    max_rows: int = MAX_ROWS,
) -> list[dict]:
    """
    Executa a query com segurança:
    1. Valida contra blocklist
    2. Usa cursor de read-only (via BEGIN DEFERRED)
    3. Limita linhas retornadas a max_rows
    4. Registra no audit log

    Retorna lista de dicts (column→value).
    Lança SQLGuardError se não seguro.
    """
    validate_query(query)
    _log("EXECUTE", query)

    try:
        # Força transação read-only
        conn.execute("BEGIN DEFERRED")
        cursor = conn.execute(query, params)
        columns = [d[0] for d in cursor.description or []]
        rows = cursor.fetchmany(max_rows + 1)

        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]

        conn.rollback()  # garante que nada foi commitado

        result = [dict(zip(columns, row)) for row in rows]
        _log("SUCCESS", query, {"rows": len(result), "truncated": truncated})

        if truncated:
            result.append({"_warning": f"Resultado limitado a {max_rows} linhas por segurança."})

        return result

    except SQLGuardError:
        conn.rollback()
        raise
    except sqlite3.Error as e:
        conn.rollback()
        _log("ERROR", query, {"error": str(e)})
        raise SQLGuardError(f"[SQL GUARD] Erro de execução: {e}") from e


def open_readonly_connection(db_path: str) -> sqlite3.Connection:
    """
    Abre conexão SQLite em modo imutável (URI read-only).
    Use sempre que possível ao invés de sqlite3.connect() direto.
    """
    uri = f"file:{db_path}?mode=ro"
    return sqlite3.connect(uri, uri=True)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="sql_guard.py",
        description="KARE SQL Guard — Valida queries SQL geradas por LLM",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # validate
    p_val = sub.add_parser("validate", help="Valida uma query SQL")
    p_val.add_argument("query", help="Query SQL a validar")

    # log
    p_log = sub.add_parser("log", help="Exibe audit log de queries")
    p_log.add_argument("--last", type=int, default=20)

    args = parser.parse_args()

    if args.cmd == "validate":
        try:
            validate_query(args.query)
            print(f"[SQL GUARD] ✅ Query segura: {args.query[:80]!r}")
            _log("VALIDATE_OK", args.query)
        except SQLGuardError as e:
            print(str(e))
            _log("VALIDATE_FAIL", args.query, {"reason": str(e)})
            sys.exit(1)

    elif args.cmd == "log":
        if not _AUDIT_LOG.exists():
            print("[SQL GUARD] Nenhum evento no audit log.")
            return
        lines = _AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()
        for line in lines[-args.last:]:
            try:
                e = json.loads(line)
                print(f"  {e['ts'][:19]}Z  [{e['event']:12s}] {e.get('query_preview','')[:60]}")
            except Exception:
                print(f"  {line}")


if __name__ == "__main__":
    main()

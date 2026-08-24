"""Testes para sql_guard.py — enforcer de SELECT-only para queries geradas por LLM."""

import sqlite3

import pytest

from conftest import AGENT_DIR, load_module


@pytest.fixture
def sql_guard(tmp_path, monkeypatch):
    module = load_module("sql_guard", AGENT_DIR / "scripts" / "guards" / "sql_guard.py")
    monkeypatch.setattr(module, "_AUDIT_LOG", tmp_path / "sql_audit.jsonl")
    return module


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM nodes",
        "  select id, title from nodes where type = 'concept'",
        "SELECT COUNT(*) FROM nodes",
    ],
)
def test_valid_select_queries_pass(sql_guard, query):
    sql_guard.validate_query(query)  # não deve levantar


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM nodes",
        "DROP TABLE nodes",
        "UPDATE nodes SET title='x'",
        "INSERT INTO nodes VALUES (1,2,3)",
        "ALTER TABLE nodes ADD COLUMN x TEXT",
        "SELECT * FROM nodes; DROP TABLE nodes;--",
        "SELECT * FROM sqlite_master",
        "SELECT * FROM credentials",
        "PRAGMA table_info(nodes)",
    ],
)
def test_dangerous_queries_are_blocked(sql_guard, query):
    with pytest.raises(sql_guard.SQLGuardError):
        sql_guard.validate_query(query)


def test_empty_query_blocked(sql_guard):
    with pytest.raises(sql_guard.SQLGuardError):
        sql_guard.validate_query("")
    with pytest.raises(sql_guard.SQLGuardError):
        sql_guard.validate_query("   ")


def test_safe_execute_returns_rows_for_valid_query(sql_guard):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'a'), (2, 'b')")
    conn.commit()

    rows = sql_guard.safe_execute(conn, "SELECT * FROM t ORDER BY id")

    assert rows == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


def test_safe_execute_rejects_write_query_without_touching_db(sql_guard):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.commit()

    with pytest.raises(sql_guard.SQLGuardError):
        sql_guard.safe_execute(conn, "DELETE FROM t")

    count = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert count == 0  # nada foi alterado


def test_safe_execute_truncates_at_max_rows(sql_guard):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(10)])
    conn.commit()

    rows = sql_guard.safe_execute(conn, "SELECT * FROM t", max_rows=3)

    assert len(rows) == 4  # 3 linhas + aviso de truncamento
    assert "_warning" in rows[-1]


def test_audit_log_writes_entries(sql_guard, tmp_path):
    sql_guard.validate_query("SELECT 1")
    sql_guard._log("VALIDATE_OK", "SELECT 1")

    log_path = tmp_path / "sql_audit.jsonl"
    assert log_path.exists()
    assert "VALIDATE_OK" in log_path.read_text(encoding="utf-8")

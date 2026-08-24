"""Testes para a proteção por senha da base RAG perene em kare_rag.py."""

import pytest

FACTORY_DEFAULT_VALUE = "@Kar3Padr4o123"


def test_first_insertion_true_when_db_missing(isolated_rag_dir):
    assert isolated_rag_dir._perene_is_first_insertion() is True


def test_password_is_default_when_no_credentials_module(isolated_rag_dir, monkeypatch):
    monkeypatch.setattr(isolated_rag_dir, "_kare_credentials", lambda: None)
    assert isolated_rag_dir._perene_password_is_default() is True


def test_factory_password_accepted_on_first_insertion(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials
    # Não deve levantar (o _err da lib chama sys.exit em caso de falha)
    first_insertion = kare_rag._require_perene_password(FACTORY_DEFAULT_VALUE)
    assert first_insertion is True


def test_wrong_password_rejected(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials
    with pytest.raises(SystemExit):
        kare_rag._require_perene_password("senha-errada")


def test_first_insertion_false_after_a_node_is_inserted(isolated_rag_with_credentials):
    kare_rag, _ = isolated_rag_with_credentials

    class Args:
        title = "Teste"
        type = "concept"
        context = "global"
        file = None
        content = "conteúdo de teste"
        symbols = ""
        password = FACTORY_DEFAULT_VALUE

    kare_rag.cmd_ingest(Args())

    assert kare_rag._perene_is_first_insertion() is False


def test_custom_password_overrides_factory_default(isolated_rag_with_credentials):
    kare_rag, kare_credentials = isolated_rag_with_credentials
    kare_credentials.set_perene_rag_password("SenhaCustomizada789")

    assert kare_rag._perene_password_is_default() is False

    with pytest.raises(SystemExit):
        kare_rag._require_perene_password(FACTORY_DEFAULT_VALUE)

    # não deve lançar
    kare_rag._require_perene_password("SenhaCustomizada789")


def test_bootstrap_populates_from_seed_and_is_idempotent_without_force(
    isolated_rag_with_credentials, tmp_path
):
    kare_rag, _ = isolated_rag_with_credentials

    seed_path = tmp_path / "seed.json"
    seed_path.write_text(
        '{"nodes": [{"type": "concept", "title": "Teste", "content": "x", "symbols": ""}], "edges": []}',
        encoding="utf-8",
    )

    class Args:
        seed = str(seed_path)
        force = False
        password = FACTORY_DEFAULT_VALUE

    kare_rag.cmd_bootstrap(Args())

    import sqlite3
    conn = sqlite3.connect(kare_rag.DB_PERENE)
    count = conn.execute("SELECT COUNT(*) FROM nodes WHERE layer='universal'").fetchone()[0]
    conn.close()
    assert count == 1

    # Rodar de novo sem --force não deve duplicar nem exigir senha nova
    kare_rag.cmd_bootstrap(Args())
    conn = sqlite3.connect(kare_rag.DB_PERENE)
    count = conn.execute("SELECT COUNT(*) FROM nodes WHERE layer='universal'").fetchone()[0]
    conn.close()
    assert count == 1

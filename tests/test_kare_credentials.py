"""Testes para kare_credentials.py — cofre de credenciais AES-256-GCM."""

import pytest


def test_get_all_as_env_vars_raises_when_not_configured(isolated_credentials):
    with pytest.raises(RuntimeError, match="não configuradas"):
        isolated_credentials.get_all_as_env_vars()


def test_encrypt_decrypt_roundtrip(isolated_credentials):
    key = isolated_credentials._ensure_key()
    original = {"JIRA_URL": "https://example.atlassian.net", "JIRA_API_TOKEN": "s3cr3t"}

    blob = isolated_credentials._encrypt(original, key)
    decrypted = isolated_credentials._decrypt(blob, key)

    assert decrypted == original


def test_decrypt_fails_with_wrong_key(isolated_credentials):
    key1 = isolated_credentials._ensure_key()
    blob = isolated_credentials._encrypt({"a": "b"}, key1)

    wrong_key = b"\x00" * 32
    with pytest.raises(Exception):
        isolated_credentials._decrypt(blob, wrong_key)


def test_ensure_key_is_stable_across_calls(isolated_credentials):
    key1 = isolated_credentials._ensure_key()
    key2 = isolated_credentials._ensure_key()
    assert key1 == key2
    assert len(key1) == 32  # AES-256


def test_get_perene_rag_password_returns_none_when_unset(isolated_credentials):
    assert isolated_credentials.get_perene_rag_password() is None


def test_set_and_get_perene_rag_password_roundtrip(isolated_credentials):
    isolated_credentials.set_perene_rag_password("MinhaSenhaForte123")
    assert isolated_credentials.get_perene_rag_password() == "MinhaSenhaForte123"


def test_set_perene_rag_password_preserves_other_credentials(isolated_credentials):
    key = isolated_credentials._ensure_key()
    existing = {"JIRA_URL": "https://example.atlassian.net"}
    blob = isolated_credentials._encrypt(existing, key)
    isolated_credentials._cred_path().write_bytes(blob)

    isolated_credentials.set_perene_rag_password("NovaSenha456")

    data = isolated_credentials.get_all_as_env_vars()
    assert data["JIRA_URL"] == "https://example.atlassian.net"
    assert data["PERENE_RAG_PASSWORD"] == "NovaSenha456"


def test_get_perene_rag_password_none_on_corrupt_vault(isolated_credentials):
    isolated_credentials._ensure_key()
    isolated_credentials._cred_path().write_bytes(b"not a valid encrypted blob")
    # Não deve levantar exceção — get_perene_rag_password() é best-effort.
    assert isolated_credentials.get_perene_rag_password() is None

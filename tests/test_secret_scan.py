"""Testes para secret_scan.py — usado pelo CI como defesa em profundidade
além do hook local de pre-commit.

As linhas-fixture de credencial "de mentira" são montadas por concatenação
em vez de literais contíguos, para não disparar o próprio hook de pre-commit
deste repositório ao commitar este arquivo de teste (o hook não distingue
"exemplo de teste do detector" de "credencial real")."""

import pytest

from conftest import AGENT_DIR, load_module


@pytest.fixture
def secret_scan():
    return load_module("secret_scan", AGENT_DIR / "scripts" / "guards" / "secret_scan.py")


def _fake_credential_lines():
    return [
        "password" + " = " + '"abc123real"',
        "api_token" + " = " + "'sk-live-1234567890'",
        "secret" + '="' + 'hardcoded-value-here"',
        "Authorization: " + "Bearer" + " eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "ATATT3x" + "FfGF0abcdefghijklmnop",
    ]


@pytest.mark.parametrize("line", _fake_credential_lines())
def test_detects_hardcoded_credentials(secret_scan, tmp_path, line):
    f = tmp_path / "suspect.py"
    f.write_text(line, encoding="utf-8")
    assert secret_scan.scan_file(f) != []


@pytest.mark.parametrize(
    "line",
    [
        'JIRA_API_TOKEN="$ATL_TOKEN"',
        "password = os.environ['PASSWORD']",
        "secret = ${SECRET_VALUE}",
        "this is just a normal comment about passwords",
    ],
)
def test_does_not_flag_variable_references_or_safe_text(secret_scan, tmp_path, line):
    f = tmp_path / "safe.py"
    f.write_text(line, encoding="utf-8")
    assert secret_scan.scan_file(f) == []


def test_skips_binary_like_extensions(secret_scan, tmp_path):
    f = tmp_path / "creds.enc"
    f.write_bytes(("password" + " = " + '"should-not-be-scanned"').encode())
    assert secret_scan.scan_file(f) == []


def test_skips_files_that_are_not_valid_utf8(secret_scan, tmp_path):
    f = tmp_path / "weird.py"
    line = "password" + " = " + '"café-token-value"'
    f.write_bytes(line.encode("cp1252"))
    # Não deve levantar exceção — apenas não escaneia o que não consegue ler.
    assert secret_scan.scan_file(f) == []

"""
conftest.py — fixtures compartilhadas para os testes do KARE-SPEC.

Os scripts em .agent/scripts/ não são um pacote Python instalável (são
scripts standalone invocados via CLI), então os testes os carregam por
caminho de arquivo (importlib) em vez de `import` normal. Isso evita
precisar de um pyproject.toml/setup.py só para rodar testes.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = REPO_ROOT / ".agent"


def load_module(name: str, path: Path):
    """Carrega um módulo Python a partir de um caminho de arquivo, sem precisar
    que .agent/scripts seja um pacote instalado. Registra em sys.modules para
    que imports internos do próprio módulo (ex: `import kare_credentials`
    dentro de outro script) funcionem quando o diretório já está no sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def isolated_rag_dir(tmp_path, monkeypatch):
    """Isola kare_rag.py para não tocar nos bancos reais do repositório."""
    scripts_ai = AGENT_DIR / "scripts" / "ai"
    kare_rag = load_module("kare_rag", scripts_ai / "kare_rag.py")

    rag_dir = tmp_path / "rag"
    rag_dir.mkdir()
    monkeypatch.setattr(kare_rag, "RAG_DIR", rag_dir)
    monkeypatch.setattr(kare_rag, "DB_PERENE", rag_dir / "kare_perene_rag.db")
    monkeypatch.setattr(kare_rag, "DB_HISTORY", rag_dir / "kare_history_rag.db")
    monkeypatch.setattr(kare_rag, "DB_TELEMETRY", rag_dir / "kare_telemetry.db")
    return kare_rag


@pytest.fixture
def isolated_credentials(tmp_path, monkeypatch):
    """Isola kare_credentials.py para não tocar no cofre real (.config/.venv,
    %USERPROFILE%\\kare.key) nem em credenciais reais do desenvolvedor."""
    infra = AGENT_DIR / "scripts" / "infra"
    kare_credentials = load_module("kare_credentials", infra / "kare_credentials.py")

    key_dir = tmp_path / "home"
    cred_dir = tmp_path / "config_venv"
    key_dir.mkdir()
    cred_dir.mkdir()
    monkeypatch.setattr(kare_credentials, "_key_path", lambda: key_dir / "kare.key")
    monkeypatch.setattr(kare_credentials, "_cred_path", lambda: cred_dir / "mcp-atlassian.enc")
    return kare_credentials


@pytest.fixture
def isolated_rag_with_credentials(isolated_rag_dir, isolated_credentials, monkeypatch):
    """kare_rag.py + kare_credentials.py isolados e explicitamente conectados
    (evita depender do cache de sys.modules entre testes para o import
    dinâmico que kare_rag.py faz de kare_credentials.py)."""
    monkeypatch.setattr(isolated_rag_dir, "_kare_credentials", lambda: isolated_credentials)
    return isolated_rag_dir, isolated_credentials

#!/usr/bin/env python3
"""
start_mcp_atlassian.py — Lança o servidor MCP Atlassian (Jira + Confluence)

Porte cross-platform de start_mcp_atlassian.ps1 (mesma lógica, mesmo
comportamento): resolve o binário mcp-atlassian, descriptografa as
credenciais via kare_credentials.py, injeta como variáveis de ambiente
apenas deste processo, e executa o servidor herdando stdio.

Chamado automaticamente pelo VS Code via .vscode/mcp.json — não executar
manualmente a não ser para diagnóstico.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


def _find_mcp_atlassian() -> str | None:
    """Resolve o binário mcp-atlassian:
    1) .venv local do repositório (preferido — isolado)
    2) PATH global (instalado pelo usuário sem .venv)
    """
    venv_bin_dir = "Scripts" if os.name == "nt" else "bin"
    venv_name = "mcp-atlassian.exe" if os.name == "nt" else "mcp-atlassian"
    venv_exe = REPO_ROOT / ".venv" / venv_bin_dir / venv_name
    if venv_exe.exists():
        return str(venv_exe)

    global_exe = shutil.which("mcp-atlassian")
    if global_exe:
        return global_exe

    return None


def _get_credentials() -> dict[str, str]:
    """Chama kare_credentials.py para descriptografar as credenciais em memória."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from kare_credentials import get_all_as_env_vars  # type: ignore

    return get_all_as_env_vars()


def main() -> int:
    mcp_exe = _find_mcp_atlassian()
    if not mcp_exe:
        print("", file=sys.stderr)
        print("ERRO: mcp-atlassian nao encontrado.", file=sys.stderr)
        print("Instale com um dos comandos abaixo:", file=sys.stderr)
        print("  pip install mcp-atlassian              (instalacao global)", file=sys.stderr)
        print("  .venv/bin/pip install mcp-atlassian     (instalacao isolada - recomendado)", file=sys.stderr)
        return 1

    try:
        creds = _get_credentials()
    except Exception as e:
        print("", file=sys.stderr)
        print("MCP Atlassian requer configuracao de credenciais antes do primeiro uso.", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Execute para configurar (uma vez por maquina):", file=sys.stderr)
        print("  python .agent/scripts/infra/kare_credentials.py setup", file=sys.stderr)
        print("", file=sys.stderr)
        print("ERRO: Credenciais Atlassian nao configuradas — MCP nao pode iniciar.", file=sys.stderr)
        return 1

    # Injeta nas variáveis de ambiente APENAS desta sessão de processo.
    # Ao encerrar o mcp-atlassian, as vars somem — nada persiste em disco.
    env = os.environ.copy()
    env["JIRA_URL"] = creds.get("JIRA_URL", "")
    env["JIRA_USERNAME"] = creds.get("JIRA_USERNAME", "")
    env["JIRA_API_TOKEN"] = creds.get("JIRA_API_TOKEN", "")
    env["CONFLUENCE_URL"] = creds.get("CONFLUENCE_URL", "")
    env["CONFLUENCE_USERNAME"] = creds.get("CONFLUENCE_USERNAME", "")
    env["CONFLUENCE_API_TOKEN"] = creds.get("CONFLUENCE_API_TOKEN", "")

    # Herda stdin/stdout/stderr do processo pai (protocolo MCP stdio)
    result = subprocess.run([mcp_exe, "--transport", "stdio"], env=env)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

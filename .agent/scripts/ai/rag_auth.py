"""
rag_auth.py — Autenticação JWT para a RAG API KARE

Obtém e cacheia o token JWT para os scripts clientes da RAG API.
Token cacheado por 25 min (expire no servidor em 30 min).

Uso:
    # scripts urllib
    from rag_auth import get_auth_headers
    headers = {"Content-Type": "application/json", **get_auth_headers()}

    # scripts requests
    from rag_auth import rag_session
    session = rag_session()
    session.get(url, timeout=10)
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

_API_BASE = os.environ.get("KARE_API_BASE", "http://localhost:8000")
_TOKEN_CACHE: dict = {"token": "", "expires_at": 0.0}


def _load_credentials() -> tuple:
    """
    Lê RAG_API_USER + RAG_API_PASSWORD.
    Prioridade: variáveis de ambiente → kare_credentials.py (arquivo criptografado).
    """
    user = os.environ.get("RAG_API_USER", "")
    pwd  = os.environ.get("RAG_API_PASSWORD", "")
    if user and pwd:
        return user, pwd
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from kare_credentials import get_all_as_env_vars  # noqa: PLC0415
        data = get_all_as_env_vars()
        return data.get("RAG_API_USER", ""), data.get("RAG_API_PASSWORD", "")
    except Exception:
        return "", ""


def _login() -> str:
    """
    Faz POST /auth/login e armazena o token no cache.
    Retorna '' se credenciais ausentes ou API inacessível (graceful fallback).
    """
    global _TOKEN_CACHE
    user, pwd = _load_credentials()
    if not user or not pwd:
        return ""

    payload = json.dumps({"username": user, "password": pwd}).encode()
    req = urllib.request.Request(
        f"{_API_BASE}/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            token = data.get("access_token", "")
            expires_in = int(data.get("expires_in", 1800))
            _TOKEN_CACHE = {
                "token": token,
                "expires_at": time.time() + expires_in - 60,  # margem de 60s
            }
            return token
    except Exception:
        return ""


def get_jwt_token() -> str:
    """Retorna token JWT válido (faz login automático se expirado)."""
    global _TOKEN_CACHE
    if _TOKEN_CACHE["token"] and time.time() < _TOKEN_CACHE["expires_at"]:
        return _TOKEN_CACHE["token"]
    return _login()


def get_auth_headers() -> dict:
    """
    Retorna {'Authorization': 'Bearer <token>'} ou {} se não configurado.
    Nunca lança exceção — falha silenciosa para não quebrar scripts em ambientes
    não configurados.
    """
    token = get_jwt_token()
    return {"Authorization": f"Bearer {token}"} if token else {}


def rag_session():
    """
    Retorna requests.Session com Authorization header atualizado.
    Cria uma nova session a cada chamada para garantir token fresco.
    """
    try:
        import requests  # noqa: PLC0415
        session = requests.Session()
        session.headers.update(get_auth_headers())
        return session
    except ImportError as exc:
        raise ImportError("requests não instalado: pip install requests") from exc

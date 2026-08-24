#!/usr/bin/env python3
"""
kare_credentials.py — Gerenciador seguro de credenciais KARE

Criptografa as credenciais com AES-256-GCM usando uma chave armazenada
FORA do projeto (ex: C:\\Users\\<user>\\kare.key).

Arquivos:
  KEY_FILE  : %USERPROFILE%\\kare.key           (gerado automaticamente, fora do projeto)
  CRED_FILE : .config\\.venv\\mcp-atlassian.enc  (criptografado, pode ser versionado)

Uso CLI:
  python kare_credentials.py setup         — configura credenciais Jira/Confluence interativamente
  python kare_credentials.py setup-perene  — define/troca a senha da base RAG perene
  python kare_credentials.py setup-rag     — configura credenciais da RAG API interna
  python kare_credentials.py check         — verifica status
  python kare_credentials.py clear         — remove chave e arquivo criptografado
"""

import os
import sys
import json
import getpass
import secrets
from pathlib import Path

# Força UTF-8 no stdout — evita UnicodeEncodeError no console Windows (cp1252)
if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "").lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

def _key_path() -> Path:
    """Arquivo de chave — FORA do projeto, na home do usuário."""
    return Path(os.environ.get("USERPROFILE", Path.home())) / "kare.key"


def _cred_path() -> Path:
    """Arquivo de credenciais criptografadas — dentro do projeto."""
    here = Path(__file__).parent
    cred_dir = here.parent.parent.parent / ".config" / ".venv"
    cred_dir.mkdir(parents=True, exist_ok=True)
    return cred_dir / "mcp-atlassian.enc"




# ---------------------------------------------------------------------------
# Criptografia AES-256-GCM via cryptography (sem dependência do OS)
# ---------------------------------------------------------------------------

def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM
    except ImportError:
        print(
            "❌ Pacote 'cryptography' não instalado.\n"
            "   Execute: pip install cryptography",
            file=sys.stderr,
        )
        sys.exit(1)


def _ensure_key() -> bytes:
    """Retorna a chave AES-256. Gera e salva uma nova se não existir."""
    kp = _key_path()
    if kp.exists():
        raw = kp.read_bytes().strip()
        import base64
        return base64.b64decode(raw)
    # Gerar chave nova de 32 bytes (256 bits)
    key = secrets.token_bytes(32)
    import base64
    kp.write_bytes(base64.b64encode(key))
    # Permissão restrita — somente o dono lê (funciona no Windows via ACL implícita)
    try:
        import stat
        kp.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass
    return key


def _encrypt(data: dict, key: bytes) -> bytes:
    """Serializa dict → JSON → criptografa com AES-256-GCM."""
    AESGCM = _crypto()
    nonce = secrets.token_bytes(12)          # 96-bit nonce único por encrypt
    plaintext = json.dumps(data, ensure_ascii=False).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    # Formato: [12 bytes nonce][ciphertext+tag]
    return nonce + ciphertext


def _decrypt(blob: bytes, key: bytes) -> dict:
    """Descriptografa blob → dict."""
    AESGCM = _crypto()
    nonce, ciphertext = blob[:12], blob[12:]
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def get_confluence_credentials() -> tuple[str, str, str]:
    """
    Retorna (confluence_url, username, token).
    Descriptografa em memória — nada é escrito em disco.
    Lança RuntimeError se não configurado.
    """
    cred_file = _cred_path()
    key_file  = _key_path()

    if not key_file.exists():
        raise RuntimeError(
            f"Arquivo de chave não encontrado: {key_file}\n"
            "   Execute: python .agent/scripts/infra/kare_credentials.py setup"
        )
    if not cred_file.exists():
        raise RuntimeError(
            f"Arquivo de credenciais não encontrado: {cred_file}\n"
            "   Execute: python .agent/scripts/infra/kare_credentials.py setup"
        )

    key  = _ensure_key()
    data = _decrypt(cred_file.read_bytes(), key)

    url   = data.get("CONFLUENCE_URL", "")
    user  = data.get("CONFLUENCE_USERNAME", "")
    token = data.get("CONFLUENCE_API_TOKEN", "")

    missing = [k for k, v in [("CONFLUENCE_URL", url), ("CONFLUENCE_USERNAME", user), ("CONFLUENCE_API_TOKEN", token)] if not v]
    if missing:
        raise RuntimeError(f"Credenciais incompletas: {', '.join(missing)}")

    return url, user, token


def get_jira_credentials() -> tuple[str, str, str]:
    """
    Retorna (jira_url, username, token).
    Descriptografa em memória.
    """
    cred_file = _cred_path()
    key_file  = _key_path()

    if not key_file.exists() or not cred_file.exists():
        raise RuntimeError(
            "Credenciais não configuradas.\n"
            "   Execute: python .agent/scripts/infra/kare_credentials.py setup"
        )

    key  = _ensure_key()
    data = _decrypt(cred_file.read_bytes(), key)

    url   = data.get("JIRA_URL", "")
    user  = data.get("JIRA_USERNAME", "")
    token = data.get("JIRA_API_TOKEN", "")

    missing = [k for k, v in [("JIRA_URL", url), ("JIRA_USERNAME", user), ("JIRA_API_TOKEN", token)] if not v]
    if missing:
        raise RuntimeError(f"Credenciais incompletas: {', '.join(missing)}")

    return url, user, token


def get_all_as_env_vars() -> dict[str, str]:
    """
    Retorna todas as credenciais como dict de variáveis de ambiente.
    Usado pelo start_mcp_atlassian.py via import direto.
    """
    cred_file = _cred_path()
    key_file  = _key_path()

    if not key_file.exists() or not cred_file.exists():
        raise RuntimeError(
            "Credenciais não configuradas.\n"
            "   Execute: python .agent/scripts/infra/kare_credentials.py setup"
        )

    key  = _ensure_key()
    return _decrypt(cred_file.read_bytes(), key)


def get_perene_rag_password() -> str | None:
    """
    Retorna a palavra-passe customizada da base RAG perene, se já tiver sido
    configurada via `setup-perene`. Retorna None (não lança exceção) se ainda
    não configurada — kare_rag.py usa isso para cair de volta na senha padrão
    de fábrica, já que essa credencial é opcional (tem fallback), diferente
    de Jira/Confluence que são obrigatórias.
    """
    cred_file = _cred_path()
    key_file  = _key_path()
    if not key_file.exists() or not cred_file.exists():
        return None
    try:
        key  = _ensure_key()
        data = _decrypt(cred_file.read_bytes(), key)
        return data.get("PERENE_RAG_PASSWORD") or None
    except Exception:
        return None


def set_perene_rag_password(password: str) -> None:
    """Salva/atualiza a palavra-passe da base RAG perene no cofre criptografado
    compartilhado, preservando as demais credenciais já configuradas (Jira,
    Confluence, RAG API etc)."""
    current: dict = {}
    try:
        current = get_all_as_env_vars()
    except Exception:
        pass
    fields = dict(current)
    fields["PERENE_RAG_PASSWORD"] = password
    key  = _ensure_key()
    blob = _encrypt(fields, key)
    _cred_path().write_bytes(blob)




# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _read_input(prompt: str, current: str | None = None, secret: bool = False) -> str:
    display = prompt
    if current:
        display += f" [{'***' if secret else current}]"
    display += ": "
    value = getpass.getpass(display) if secret else input(display).strip()
    return value if value else (current or "")


def cmd_setup():
    print("=" * 62)
    print("  KARE — Configuração de Credenciais (AES-256-GCM)")
    print("=" * 62)
    print(f"  Chave     : {_key_path()}  (fora do projeto)")
    print(f"  Credenciais: {_cred_path()}  (criptografado)")
    print()

    # Ler dados existentes se já configurado
    current: dict = {}
    try:
        current = get_all_as_env_vars()
    except Exception:
        pass

    jira_url  = _read_input("JIRA_URL",        current.get("JIRA_URL"))
    jira_user = _read_input("JIRA_USERNAME",   current.get("JIRA_USERNAME"))
    conf_url  = _read_input("CONFLUENCE_URL",  current.get("CONFLUENCE_URL"))
    conf_user = _read_input("CONFLUENCE_USERNAME", current.get("CONFLUENCE_USERNAME"))

    # Token
    if current.get("JIRA_API_TOKEN"):
        reuse = input("Manter token atual? [Y/n]: ").strip().lower()
        if reuse in ("", "y"):
            jira_token = current["JIRA_API_TOKEN"]
            conf_token = current.get("CONFLUENCE_API_TOKEN", jira_token)
        else:
            jira_token = _read_input("JIRA_API_TOKEN", secret=True)
            same = input("Usar mesmo token para Confluence? [Y/n]: ").strip().lower()
            conf_token = jira_token if same in ("", "y") else _read_input("CONFLUENCE_API_TOKEN", secret=True)
    else:
        jira_token = _read_input("JIRA_API_TOKEN", secret=True)
        same = input("Usar mesmo token para Confluence? [Y/n]: ").strip().lower()
        conf_token = jira_token if same in ("", "y") else _read_input("CONFLUENCE_API_TOKEN", secret=True)

    # Validar
    fields = {
        "JIRA_URL": jira_url, "JIRA_USERNAME": jira_user, "JIRA_API_TOKEN": jira_token,
        "CONFLUENCE_URL": conf_url, "CONFLUENCE_USERNAME": conf_user, "CONFLUENCE_API_TOKEN": conf_token,
    }
    missing = [k for k, v in fields.items() if not v]
    if missing:
        print(f"\n❌ Campos obrigatórios não preenchidos: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    # Criptografar e salvar
    key  = _ensure_key()
    blob = _encrypt(fields, key)
    _cred_path().write_bytes(blob)

    print()
    print(f"  ✅ Credenciais criptografadas salvas em: {_cred_path()}")
    print(f"  🔑 Chave de descriptografia em: {_key_path()}")
    print()
    print("  IMPORTANTE: Nunca compartilhe ou versione o arquivo kare.key!")
    print("  Reinicie o VS Code ou a sessão do KARE para recarregar o MCP.")


def cmd_check():
    print("KARE — Status das Credenciais\n")

    key_ok  = _key_path().exists()
    cred_ok = _cred_path().exists()

    print(f"  Chave  ({_key_path()}): {'✅ presente' if key_ok else '❌ ausente'}")
    print(f"  Creds  ({_cred_path()}): {'✅ presente' if cred_ok else '❌ ausente'}")

    if not key_ok or not cred_ok:
        print("\n  Execute: python .agent/scripts/infra/kare_credentials.py setup")
        return False

    try:
        data = get_all_as_env_vars()
        print()
        for k, v in data.items():
            display = v[:4] + "***" if "TOKEN" in k else v
            print(f"  ✅ {k:<30} {display}")
        print("\n  Todas as credenciais configuradas.")
        return True
    except Exception as e:
        print(f"\n  ❌ Erro ao descriptografar: {e}")
        return False


def cmd_clear():
    confirm = input("Remover chave e credenciais criptografadas? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelado.")
        return
    for p in [_key_path(), _cred_path()]:
        if p.exists():
            p.unlink()
            print(f"  Removido: {p}")
    print("✅ Credenciais removidas.")


def cmd_setup_from_json(json_path: str):
    """
    Configura credenciais a partir de um arquivo JSON temporário.
    O arquivo é APAGADO imediatamente após a leitura.

    Formato esperado:
    {
      "JIRA_URL": "https://...",
      "JIRA_USERNAME": "user",
      "JIRA_API_TOKEN": "token",
      "CONFLUENCE_URL": "https://...",
      "CONFLUENCE_USERNAME": "user",
      "CONFLUENCE_API_TOKEN": "token"
    }
    Se "CONFLUENCE_API_TOKEN" for omitido, usa o mesmo que "JIRA_API_TOKEN".
    """
    p = Path(json_path)
    if not p.exists():
        print(f"❌ Arquivo não encontrado: {p}", file=sys.stderr)
        sys.exit(1)

    try:
        raw = p.read_text(encoding="utf-8")
        fields = json.loads(raw)
    except Exception as e:
        print(f"❌ Erro ao ler arquivo JSON: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Apagar imediatamente — independente de erro
        try:
            p.unlink()
        except Exception:
            pass

    # Usar mesmo token para Confluence se não especificado
    if not fields.get("CONFLUENCE_API_TOKEN") and fields.get("JIRA_API_TOKEN"):
        fields["CONFLUENCE_API_TOKEN"] = fields["JIRA_API_TOKEN"]

    required = ["JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN",
                "CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"]
    missing = [k for k in required if not fields.get(k)]
    if missing:
        print(f"❌ Campos obrigatórios ausentes no JSON: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    key  = _ensure_key()
    blob = _encrypt(fields, key)
    _cred_path().write_bytes(blob)

    print(f"  ✅ Credenciais criptografadas salvas em: {_cred_path()}")
    print(f"  🔑 Chave de descriptografia em: {_key_path()}")
    print("  📄 Arquivo JSON temporário apagado.")
    print()
    print("  IMPORTANTE: Nunca compartilhe ou versione o arquivo kare.key!")
    print("  Reinicie o VS Code ou a sessão do KARE para recarregar o MCP.")


def cmd_setup_rag():
    """Configura credenciais da RAG API interativamente."""
    print("=" * 62)
    print("  KARE — Configuração da RAG API (AES-256-GCM)")
    print("=" * 62)

    current: dict = {}
    try:
        current = get_all_as_env_vars()
    except Exception:
        pass

    # JWT_SECRET_KEY — gerado automaticamente se não existir
    if current.get("JWT_SECRET_KEY"):
        print("  JWT_SECRET_KEY: já configurado (mantendo)")
        jwt_secret = current["JWT_SECRET_KEY"]
    else:
        import base64 as _b64
        jwt_secret = _b64.b64encode(secrets.token_bytes(32)).decode()
        print(f"  JWT_SECRET_KEY: gerado automaticamente")

    rag_user = _read_input("RAG_API_USER", current.get("RAG_API_USER"))
    rag_pass = _read_input("RAG_API_PASSWORD", secret=True)

    if not rag_pass and current.get("RAG_API_PASSWORD"):
        keep = input("Manter senha atual? [Y/n]: ").strip().lower()
        rag_pass = current["RAG_API_PASSWORD"] if keep in ("", "y") else ""

    if not rag_user or not rag_pass:
        print("❌ RAG_API_USER e RAG_API_PASSWORD são obrigatórios.", file=sys.stderr)
        sys.exit(1)

    # Mesclar com credenciais existentes
    fields = dict(current)
    fields["JWT_SECRET_KEY"]  = jwt_secret
    fields["RAG_API_USER"]    = rag_user
    fields["RAG_API_PASSWORD"] = rag_pass

    key  = _ensure_key()
    blob = _encrypt(fields, key)
    _cred_path().write_bytes(blob)

    print()
    print(f"  ✅ RAG API credentials salvas em: {_cred_path()}")
    print("  Reinicie o VS Code para recarregar o Context Engine.")


def cmd_setup_perene():
    """Define/troca a palavra-passe da base RAG perene (kare_perene_rag.db)."""
    print("=" * 62)
    print("  KARE — Palavra-passe da Base RAG Perene (AES-256-GCM)")
    print("=" * 62)

    current_stored = get_perene_rag_password()
    if current_stored is not None:
        print("  Já existe uma palavra-passe customizada configurada.")
    else:
        print("  Nenhuma palavra-passe customizada ainda — usando a senha padrão de fábrica")
        print("  (documentada em README.md). Esta operação define uma própria.")
    print()

    try:
        new1 = getpass.getpass("Nova palavra-passe da base perene: ")
        new2 = getpass.getpass("Confirme a nova palavra-passe: ")
    except (EOFError, KeyboardInterrupt):
        print("\nOperação cancelada.", file=sys.stderr)
        sys.exit(1)

    if new1 != new2:
        print("❌ As senhas não coincidem.", file=sys.stderr)
        sys.exit(1)
    if len(new1) < 8:
        print("❌ A nova senha deve ter ao menos 8 caracteres.", file=sys.stderr)
        sys.exit(1)

    set_perene_rag_password(new1)
    print()
    print(f"  ✅ Palavra-passe da base perene salva em: {_cred_path()} (criptografado)")
    print("  A senha padrão de fábrica deixa de funcionar a partir de agora.")


def cmd_setup_rag_from_json(json_path: str):
    """Configura credenciais da RAG API via arquivo JSON temporário (apagado após leitura)."""
    p = Path(json_path)
    if not p.exists():
        print(f"❌ Arquivo não encontrado: {p}", file=sys.stderr)
        sys.exit(1)

    try:
        fields_in = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            p.unlink()
        except Exception:
            pass

    current: dict = {}
    try:
        current = get_all_as_env_vars()
    except Exception:
        pass

    # Gerar JWT_SECRET_KEY automaticamente se não fornecido
    if not fields_in.get("JWT_SECRET_KEY"):
        import base64 as _b64
        fields_in["JWT_SECRET_KEY"] = _b64.b64encode(secrets.token_bytes(32)).decode()
        print("  JWT_SECRET_KEY: gerado automaticamente")

    missing = [k for k in ("RAG_API_USER", "RAG_API_PASSWORD") if not fields_in.get(k)]
    if missing:
        print(f"❌ Campos obrigatórios ausentes: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    fields = {**current, **fields_in}
    key  = _ensure_key()
    blob = _encrypt(fields, key)
    _cred_path().write_bytes(blob)

    print(f"  ✅ RAG API credentials salvas em: {_cred_path()}")
    print("  📄 Arquivo JSON temporário apagado.")
    print("  Reinicie o VS Code para recarregar o Context Engine.")




if __name__ == "__main__":
    # Chamado sem argumentos pelo kare_start.ps1 → emite JSON com todas as credenciais
    if len(sys.argv) == 1:
        try:
            data = get_all_as_env_vars()
            print(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
        sys.exit(0)
    # Suporte a: setup --from-json <caminho>
    if len(sys.argv) == 3 and sys.argv[1] == "setup" and sys.argv[2].startswith("--from-json="):
        cmd_setup_from_json(sys.argv[2].split("=", 1)[1])
        sys.exit(0)
    if len(sys.argv) == 4 and sys.argv[1] == "setup" and sys.argv[2] == "--from-json":
        cmd_setup_from_json(sys.argv[3])
        sys.exit(0)
    # Suporte a: setup-rag --from-json <caminho>
    if len(sys.argv) >= 2 and sys.argv[1] == "setup-rag":
        if len(sys.argv) == 4 and sys.argv[2] == "--from-json":
            cmd_setup_rag_from_json(sys.argv[3])
        elif len(sys.argv) == 3 and sys.argv[2].startswith("--from-json="):
            cmd_setup_rag_from_json(sys.argv[2].split("=", 1)[1])
        else:
            cmd_setup_rag()
        sys.exit(0)

    commands = {"setup": cmd_setup, "check": cmd_check, "clear": cmd_clear, "setup-perene": cmd_setup_perene}
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd not in commands:
        print(f"Uso: python kare_credentials.py [{'|'.join(commands)}|setup-rag]")
        print(f"     python kare_credentials.py setup --from-json <caminho.json>")
        print(f"     python kare_credentials.py setup-rag --from-json <caminho.json>")
        sys.exit(1)
    commands[cmd]()

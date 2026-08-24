#!/usr/bin/env python3
"""
KARE Guardrail Gate — Controle de Autorização para Operações de Alto Risco

Uso:
    python .agent/scripts/guards/guardrail_gate.py check <skill-name> [--operation <op>]
    python .agent/scripts/guards/guardrail_gate.py approve <skill-name> --reason "<motivo>"
    python .agent/scripts/guards/guardrail_gate.py status <skill-name>
    python .agent/scripts/guards/guardrail_gate.py log [--last N]

Integração nas skills:
    from guardrail_gate import require_authorization
    require_authorization("code-author-autogen")  # lança GuardrailDenied se não autorizado
"""

import sys
import json
import os
import datetime
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
_BASE = Path(__file__).parents[2]  # .agent/ (script está em .agent/scripts/guards/)
_AUTH_DIR = _BASE / ".guardrails"
_AUTH_DIR.mkdir(exist_ok=True)
_AUTH_DB = _AUTH_DIR / "authorizations.jsonl"
_AUDIT_LOG = _AUTH_DIR / "audit.jsonl"

# ---------------------------------------------------------------------------
# Registro de Risco por Skill
# ---------------------------------------------------------------------------
RISK_REGISTRY: dict = {
    "code-author-autogen": {
        "level": "CRITICAL",
        "label": "Execução de Código LLM em Sandbox",
        "description": (
            "O agente vai EXECUTAR código gerado por LLM em um processo local. "
            "Risco: sandbox escape, acesso ao filesystem, consumo excessivo de recursos."
        ),
        "blocked_modules": ["os", "subprocess", "shutil", "socket", "requests", "urllib"],
        "timeout_seconds": 30,
        "max_iterations": 3,
        "require_confirmation": True,
        "ttl_minutes": 60,         # autorização expira em 60 min
        "env_required": None,
    },
    "agent-builder-autogen": {
        "level": "CRITICAL",
        "label": "Criação de Novo Agente KARE Autônomo",
        "description": (
            "O meta-agente vai CRIAR e REGISTRAR um novo agente .agent.md com "
            "permissões de ferramenta. Risco: privilege escalation, agente criado com "
            "instruções maliciosas ou tools excessivas."
        ),
        "allowed_tools_for_generated_agent": ["Read", "Grep", "Write"],
        "require_human_review_of_output": True,
        "require_confirmation": True,
        "ttl_minutes": 30,         # revisão deve ser feita logo
        "env_required": None,
    },
    "rag-continual-learning": {
        "level": "CRITICAL",
        "label": "Ingestão Automática de Documentos no RAG",
        "description": (
            "O pipeline vai INGERIR documentos do Confluence/Jira no grafo de "
            "conhecimento sem revisão manual. Risco: data poisoning, prompt injection "
            "embutida em páginas Confluence."
        ),
        "trusted_spaces": ["<espaco-confluence-aprovado-1>", "<espaco-confluence-aprovado-2>"],
        "sanitize_patterns": [
            r"(?i)(ignore|ignora|esquece|forget).{0,30}(instru|rule|regra)",
            r"(?i)(system:|<system>|\[INSTRUÇÃO\]|\[SYSTEM\])",
            r"(?i)(jailbreak|bypass|override).{0,20}(agent|guardrail|rule)",
        ],
        "require_confirmation": True,
        "ttl_minutes": 120,
        "env_required": None,
    },
    "delivery-observer-sql": {
        "level": "CRITICAL",
        "label": "Execução de Query SQL Gerada por LLM",
        "description": (
            "O agente vai EXECUTAR uma query SQL contra o banco SQLite do KARE. "
            "Risco: SQL injection via NL2SQL, exposição de dados, operações destrutivas."
        ),
        "allowed_operations": ["SELECT"],
        "blocked_keywords": ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
                             "ATTACH", "DETACH", "PRAGMA", "--", "/*", "xp_", "EXEC"],
        "require_confirmation": True,
        "ttl_minutes": 30,
        "env_required": None,
    },
    "security-red-team": {
        "level": "HIGH",
        "label": "Execução de Testes Adversariais Red Team",
        "description": (
            "O agente vai EXECUTAR ataques simulados (prompt injection, jailbreak, "
            "OWASP LLM Top 10) contra sistemas KARE. PROIBIDO em produção."
        ),
        "require_confirmation": True,
        "ttl_minutes": 120,
        "env_required": "staging",
    },
    "azure-iac-engineer": {
        "level": "HIGH",
        "label": "Aplicação de IaC em Infraestrutura Azure",
        "description": (
            "O agente vai gerar e potencialmente APLICAR Terraform/Bicep em "
            "infraestrutura Azure real. Risco: misconfiguration, recursos públicos, "
            "custos inesperados."
        ),
        "require_plan_review": True,
        "require_confirmation": True,
        "ttl_minutes": 60,
        "env_required": None,
    },
    "gcp-analytics-agent": {
        "level": "HIGH",
        "label": "Operações em BigQuery/Vertex AI/Dataflow (GCP)",
        "description": (
            "O agente vai executar jobs no GCP (BigQuery, Vertex AI, Dataflow). "
            "Risco: exposição de dados analíticos B2B, custo excessivo de compute."
        ),
        "require_confirmation": True,
        "ttl_minutes": 60,
        "env_required": None,
    },
    "agent-simulation-testing": {
        "level": "MEDIUM",
        "label": "Simulação de Usuários Reais contra Agentes KARE",
        "description": (
            "O agente vai simular interações de usuário para validar robustez. "
            "Deve rodar ISOLADO — sem acesso ao MCP real."
        ),
        "require_confirmation": False,
        "ttl_minutes": 120,
        "env_required": "staging",
    },
}

# ---------------------------------------------------------------------------
# Exceções
# ---------------------------------------------------------------------------
class GuardrailDenied(Exception):
    """Lançado quando o usuário nega a autorização ou ela expirou."""

class GuardrailEnvError(Exception):
    """Lançado quando o ambiente atual não é o permitido para a skill."""

# ---------------------------------------------------------------------------
# Helpers de persistência
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _log_event(event_type: str, skill: str, details: dict) -> None:
    entry = {"ts": _now_iso(), "event": event_type, "skill": skill, **details}
    with open(_AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_authorizations() -> dict:
    auths: dict = {}
    if not _AUTH_DB.exists():
        return auths
    with open(_AUTH_DB, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                auths[entry["skill"]] = entry
            except json.JSONDecodeError:
                pass
    return auths


def _save_authorization(skill: str, reason: str, operator: str) -> None:
    config = RISK_REGISTRY.get(skill, {})
    ttl = config.get("ttl_minutes", 60)
    expires_at = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=ttl)
    ).isoformat()
    entry = {
        "skill": skill,
        "authorized_at": _now_iso(),
        "expires_at": expires_at,
        "reason": reason,
        "operator": operator,
        "ttl_minutes": ttl,
    }
    # rewrite file with updated entry
    auths = _load_authorizations()
    auths[skill] = entry
    with open(_AUTH_DB, "w", encoding="utf-8") as f:
        for v in auths.values():
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    _log_event("AUTHORIZED", skill, {"reason": reason, "operator": operator, "expires_at": expires_at})
    print(f"[GUARDRAIL] ✅ Autorização registrada para '{skill}'")
    print(f"           Expira em: {expires_at}")


def _is_authorized(skill: str) -> bool:
    auths = _load_authorizations()
    if skill not in auths:
        return False
    entry = auths[skill]
    expires_at = datetime.datetime.fromisoformat(entry["expires_at"])
    if datetime.datetime.now(datetime.timezone.utc) > expires_at:
        _log_event("EXPIRED", skill, {"expired_at": entry["expires_at"]})
        return False
    return True

# ---------------------------------------------------------------------------
# API pública — usar nas skills
# ---------------------------------------------------------------------------

def require_authorization(skill: str, operation: str = "execute") -> None:
    """
    Verifica se existe autorização válida para a skill.
    Lança GuardrailDenied se não houver.
    Lança GuardrailEnvError se o ambiente atual não for o permitido.

    Uso típico em SKILL.md:
        from guardrail_gate import require_authorization
        require_authorization("security-red-team")
    """
    config = RISK_REGISTRY.get(skill)
    if config is None:
        # skill não monitorada — permitir (não bloquear o que não foi classificado)
        return

    # Verificar ambiente
    env_required = config.get("env_required")
    if env_required:
        current_env = os.getenv("KARE_ENV", "").lower()
        if current_env != env_required.lower():
            env_display = repr(current_env) if current_env else "'(não definido)'"
            msg = (
                f"[GUARDRAIL] ❌ BLOQUEADO — '{skill}' exige KARE_ENV={env_required!r}.\n"
                f"            Ambiente atual: {env_display}.\n"
                f"            Defina: $env:KARE_ENV = '{env_required}'"
            )
            _log_event("BLOCKED_ENV", skill, {"required": env_required, "current": current_env})
            raise GuardrailEnvError(msg)

    # Verificar autorização
    if not config.get("require_confirmation", False):
        _log_event("ALLOWED_NO_CONFIRM", skill, {"operation": operation})
        return

    if not _is_authorized(skill):
        level = config.get("level", "?")
        label = config.get("label", skill)
        desc = config.get("description", "")
        msg = (
            f"\n{'='*64}\n"
            f"  ⛔  KARE GUARDRAIL — AUTORIZAÇÃO NECESSÁRIA\n"
            f"{'='*64}\n"
            f"  Skill    : {skill}\n"
            f"  Risco    : {level}\n"
            f"  Operação : {label}\n"
            f"\n  {desc}\n"
            f"\n  Para autorizar, execute:\n"
            f"  python .agent/scripts/guards/guardrail_gate.py approve {skill} --reason \"<motivo>\"\n"
            f"{'='*64}\n"
        )
        _log_event("DENIED", skill, {"operation": operation, "reason": "no_authorization"})
        raise GuardrailDenied(msg)

    # Autorizado
    _log_event("ALLOWED", skill, {"operation": operation})


def check_sql_safety(query: str) -> tuple[bool, str]:
    """
    Valida que uma query SQL gerada pelo LLM é segura (SELECT apenas).
    Retorna (is_safe, motivo_se_bloqueado).
    """
    config = RISK_REGISTRY.get("delivery-observer-sql", {})
    blocked = config.get("blocked_keywords", [])
    upper_q = query.strip().upper()

    if not upper_q.startswith("SELECT"):
        return False, f"Query não começa com SELECT: {query[:80]!r}"

    for kw in blocked:
        if kw in upper_q:
            return False, f"Keyword proibida detectada: {kw!r}"

    return True, ""


def sanitize_rag_content(text: str, source: str = "") -> tuple[str, list]:
    """
    Remove padrões de prompt injection de conteúdo antes de ingerir no RAG.
    Retorna (texto_sanitizado, lista_de_alertas).
    """
    import re
    config = RISK_REGISTRY.get("rag-continual-learning", {})
    patterns = config.get("sanitize_patterns", [])
    alerts = []

    sanitized = text
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            alerts.append(f"Padrão suspeito em '{source}': {matches}")
            sanitized = re.sub(pattern, "[CONTEÚDO REMOVIDO POR GUARDRAIL]", sanitized)

    return sanitized, alerts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_check(args) -> None:
    skill = args.skill
    config = RISK_REGISTRY.get(skill)
    if not config:
        print(f"[GUARDRAIL] Skill '{skill}' não está no registro de riscos.")
        return

    authorized = _is_authorized(skill)
    level = config.get("level", "?")
    label = config.get("label", skill)
    env_req = config.get("env_required")

    print(f"\n{'─'*56}")
    print(f"  Skill   : {skill}")
    print(f"  Risco   : {level}  |  {label}")
    if env_req:
        current = os.getenv("KARE_ENV", "(não definido)")
        ok = "✅" if current.lower() == env_req.lower() else "❌"
        print(f"  Ambiente: {ok}  requer={env_req}  atual={current}")
    if config.get("require_confirmation"):
        auths = _load_authorizations()
        if authorized:
            entry = auths[skill]
            print(f"  Autorização: ✅ válida até {entry['expires_at']}")
            print(f"  Aprovado por: {entry.get('operator', '?')} — {entry.get('reason', '')}")
        else:
            print(f"  Autorização: ❌ não autorizado")
            print(f"  → Execute: python .agent/scripts/guards/guardrail_gate.py approve {skill} --reason \"<motivo>\"")
    else:
        print(f"  Autorização: ✅ não necessária (risco MEDIUM sem confirmação)")
    print(f"{'─'*56}\n")


def cmd_approve(args) -> None:
    skill = args.skill
    if skill not in RISK_REGISTRY:
        print(f"[GUARDRAIL] ⚠️  Skill '{skill}' não está no registro. Verifique o nome.")
        sys.exit(1)
    config = RISK_REGISTRY[skill]
    level = config.get("level", "?")
    label = config.get("label", skill)
    desc = config.get("description", "")
    ttl = config.get("ttl_minutes", 60)

    print(f"\n{'='*64}")
    print(f"  KARE GUARDRAIL — SOLICITAÇÃO DE AUTORIZAÇÃO")
    print(f"{'='*64}")
    print(f"  Skill  : {skill}")
    print(f"  Risco  : {level}")
    print(f"  Label  : {label}")
    print(f"\n  {desc}\n")
    print(f"  Motivo informado: {args.reason}")
    print(f"  TTL desta autorização: {ttl} minutos")
    print(f"{'='*64}")

    operator = args.operator or os.getenv("USERNAME") or os.getenv("USER") or "unknown"

    if not args.yes:
        confirm = input(f"\n  ⚠️  Confirma autorização para '{skill}'? [sim/não]: ").strip().lower()
        if confirm not in ("sim", "s", "yes", "y"):
            print("[GUARDRAIL] ❌ Autorização cancelada pelo usuário.")
            _log_event("CANCELLED", skill, {"operator": operator, "reason": args.reason})
            sys.exit(0)

    _save_authorization(skill, args.reason, operator)


def cmd_status(args) -> None:
    print(f"\n{'─'*64}")
    print(f"  KARE GUARDRAIL STATUS — {_now_iso()}")
    print(f"{'─'*64}")
    auths = _load_authorizations()
    now = datetime.datetime.now(datetime.timezone.utc)

    for skill, config in RISK_REGISTRY.items():
        if not config.get("require_confirmation"):
            continue
        level = config.get("level", "?")
        if skill in auths:
            entry = auths[skill]
            exp = datetime.datetime.fromisoformat(entry["expires_at"])
            valid = now < exp
            status = f"✅ válida  (expira {entry['expires_at'][:16]}Z)" if valid else "⌛ EXPIRADA"
        else:
            status = "❌ não autorizado"
        print(f"  [{level:8s}] {skill:40s} {status}")
    print(f"{'─'*64}\n")


def cmd_log(args) -> None:
    if not _AUDIT_LOG.exists():
        print("[GUARDRAIL] Nenhum evento no audit log.")
        return
    lines = _AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()
    last_n = getattr(args, "last", 20) or 20
    for line in lines[-last_n:]:
        try:
            entry = json.loads(line)
            print(f"  {entry['ts'][:19]}Z  [{entry['event']:20s}] {entry['skill']}")
        except Exception:
            print(f"  {line}")


def cmd_revoke(args) -> None:
    auths = _load_authorizations()
    if args.skill not in auths:
        print(f"[GUARDRAIL] Nenhuma autorização ativa para '{args.skill}'.")
        return
    del auths[args.skill]
    with open(_AUTH_DB, "w", encoding="utf-8") as f:
        for v in auths.values():
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    _log_event("REVOKED", args.skill, {"operator": os.getenv("USERNAME", "cli")})
    print(f"[GUARDRAIL] ✅ Autorização para '{args.skill}' revogada.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="guardrail_gate.py",
        description="KARE Guardrail Gate — Controle de Autorização para Operações de Alto Risco",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # check
    p_check = sub.add_parser("check", help="Verifica status de autorização de uma skill")
    p_check.add_argument("skill", help="Nome da skill (ex: code-author-autogen)")
    p_check.add_argument("--operation", default="execute", help="Tipo de operação")

    # approve
    p_approve = sub.add_parser("approve", help="Aprova/autoriza uma operação de alto risco")
    p_approve.add_argument("skill", help="Nome da skill")
    p_approve.add_argument("--reason", required=True, help="Motivo da autorização")
    p_approve.add_argument("--operator", default=None, help="Identificador do operador (padrão: $USERNAME)")
    p_approve.add_argument("--yes", action="store_true", help="Pula confirmação interativa")

    # status
    p_status = sub.add_parser("status", help="Exibe status de todas as autorizações")

    # log
    p_log = sub.add_parser("log", help="Exibe audit log")
    p_log.add_argument("--last", type=int, default=20, help="Número de entradas a exibir")

    # revoke
    p_revoke = sub.add_parser("revoke", help="Revoga autorização ativa de uma skill")
    p_revoke.add_argument("skill", help="Nome da skill")

    args = parser.parse_args()
    dispatch = {
        "check": cmd_check,
        "approve": cmd_approve,
        "status": cmd_status,
        "log": cmd_log,
        "revoke": cmd_revoke,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()

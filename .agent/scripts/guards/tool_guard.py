"""
tool_guard.py — Interceptor programático de permissões de ferramentas KARE

Valida se um agente tem permissão para usar uma ferramenta antes da execução.
Registra audit log de cada chamada para rastreabilidade.

Uso:
    from tool_guard import ToolGuard

    guard = ToolGuard(agent_name="delivery-observer")
    guard.check("Bash")          # raises ToolPermissionError se não permitido
    guard.check("Read")          # OK — passa silenciosamente

    # Decorator para funções que executam ferramentas:
    @guard.require("Edit")
    def editar_arquivo(path): ...
"""

import json
import logging
import functools
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Permissões declaradas por agente
# Espelha o campo `tools:` dos frontmatters em .agent/agents/*.md
# ---------------------------------------------------------------------------
AGENT_TOOL_PERMISSIONS: dict[str, set[str]] = {
    # Agentes KARE — Produto, Agilidade e Gestão TI
    "product-discovery":     {"Read", "Grep", "Glob"},
    "story-crafter":         {"Read", "Grep", "Glob", "Write", "Edit"},
    "backlog-architect":     {"Read", "Grep", "Glob", "Write", "Edit"},
    "code-author":           {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "review-master":         {"Read", "Grep", "Glob"},
    "test-engineer":         {"Read", "Grep", "Glob", "Write", "Edit"},
    "quality-guardian":      {"Read", "Grep", "Glob"},
    "risk-analyst":          {"Read", "Grep", "Glob", "Write"},
    "tech-decision-maker":   {"Read", "Grep", "Glob", "Write", "Edit"},
    "spec-writer":           {"Read", "Grep", "Glob", "Write"},
    "delivery-observer":     {"Read", "Grep", "Glob", "Write"},
    "kare-orchestrator":     {"Read", "Grep", "Glob", "Write", "Edit", "Agent"},
    "prd-reviewer":          {"Read", "Grep", "Glob"},
    "project-classifier":    {"Read", "Grep", "Glob"},

    # Agentes KIT — Técnicos
    "frontend-specialist":   {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "backend-specialist":    {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "database-architect":    {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "mobile-developer":      {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "devops-engineer":       {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "security-auditor":      {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "qa-automation-engineer":{"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "debugger":              {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "performance-optimizer": {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "documentation-writer":  {"Read", "Grep", "Glob", "Bash", "Edit", "Write"},
    "ux-designer":           {"Read", "Grep", "Glob", "Edit", "Write", "Browser", "MCP"},
    "code-archaeologist":    {"Read", "Grep", "Glob", "Edit", "Write"},
    "explorer-agent":        {"Read", "Grep", "Glob", "Bash", "ViewCodeItem", "FindByName"},
    "project-planner":       {"Read", "Grep", "Glob", "Bash"},
    "orchestrator":          {"Read", "Grep", "Glob", "Bash", "Write", "Edit", "Agent"},
}

# Ferramentas consideradas de alto risco — sempre exigem log explícito
HIGH_RISK_TOOLS = {"Bash", "Write", "Edit", "Agent", "MCP", "Browser"}

# ---------------------------------------------------------------------------
# Exceção customizada
# ---------------------------------------------------------------------------
class ToolPermissionError(PermissionError):
    """Levantada quando um agente tenta usar ferramenta não autorizada."""
    def __init__(self, agent: str, tool: str):
        super().__init__(
            f"[tool_guard] BLOQUEADO — Agente '{agent}' não tem permissão para usar '{tool}'. "
            f"Ferramentas permitidas: {sorted(AGENT_TOOL_PERMISSIONS.get(agent, set()))}"
        )
        self.agent = agent
        self.tool = tool


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
_AUDIT_LOG_PATH = Path(__file__).parents[2] / "config" / ".tool_guard_audit.jsonl"

def _write_audit(agent: str, tool: str, allowed: bool, context: Optional[str] = None) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "tool": tool,
        "allowed": allowed,
        "risk": tool in HIGH_RISK_TOOLS,
        "context": context,
    }
    try:
        with _AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # audit log não pode bloquear operação


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------
class ToolGuard:
    """
    Guarda de permissões para um agente específico.

    Parâmetros:
        agent_name  : Nome do agente (ex: 'delivery-observer')
        strict      : Se True (padrão), levanta ToolPermissionError.
                      Se False, apenas loga e retorna False.
        context     : Identificador da sessão/tarefa para o audit log.
    """

    def __init__(self, agent_name: str, strict: bool = True, context: Optional[str] = None):
        self.agent = agent_name
        self.strict = strict
        self.context = context
        self._permissions: set[str] = AGENT_TOOL_PERMISSIONS.get(agent_name, set())

        if agent_name not in AGENT_TOOL_PERMISSIONS:
            logging.warning(
                "[tool_guard] Agente '%s' não encontrado no registro de permissões. "
                "Todas as ferramentas serão bloqueadas em modo strict.", agent_name
            )

    # ------------------------------------------------------------------
    def check(self, tool: str) -> bool:
        """
        Verifica se o agente pode usar a ferramenta.
        Levanta ToolPermissionError em modo strict (padrão).
        Retorna True se permitido, False se bloqueado em modo não-strict.
        """
        allowed = tool in self._permissions
        _write_audit(self.agent, tool, allowed, self.context)

        if not allowed:
            if self.strict:
                raise ToolPermissionError(self.agent, tool)
            logging.warning(
                "[tool_guard] AVISO — Agente '%s' tentou usar '%s' sem permissão.",
                self.agent, tool
            )
        elif tool in HIGH_RISK_TOOLS:
            logging.info(
                "[tool_guard] HIGH-RISK — Agente '%s' usando '%s'. Contexto: %s",
                self.agent, tool, self.context
            )
        return allowed

    # ------------------------------------------------------------------
    def require(self, tool: str):
        """
        Decorator: garante que a ferramenta é permitida antes de executar a função.

        Exemplo:
            guard = ToolGuard("code-author")

            @guard.require("Bash")
            def run_tests(): ...
        """
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.check(tool)
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    # ------------------------------------------------------------------
    def allowed_tools(self) -> list[str]:
        """Retorna lista ordenada de ferramentas permitidas para este agente."""
        return sorted(self._permissions)

    # ------------------------------------------------------------------
    @staticmethod
    def audit_report(last_n: int = 50) -> list[dict]:
        """Lê as últimas N entradas do audit log."""
        if not _AUDIT_LOG_PATH.exists():
            return []
        lines = _AUDIT_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in lines[-last_n:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return entries


# ---------------------------------------------------------------------------
# CLI — uso direto via terminal
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    def _usage():
        print(
            "Uso:\n"
            "  python tool_guard.py check <agente> <ferramenta>\n"
            "  python tool_guard.py list <agente>\n"
            "  python tool_guard.py audit [--last N]\n"
            "  python tool_guard.py agents\n"
        )

    args = sys.argv[1:]
    if not args:
        _usage()
        sys.exit(0)

    cmd = args[0]

    if cmd == "check" and len(args) == 3:
        _, agent, tool = args
        guard = ToolGuard(agent, strict=False)
        ok = guard.check(tool)
        status = "✅ PERMITIDO" if ok else "❌ BLOQUEADO"
        print(f"{status} — agente='{agent}' ferramenta='{tool}'")
        sys.exit(0 if ok else 1)

    elif cmd == "list" and len(args) == 2:
        agent = args[1]
        guard = ToolGuard(agent, strict=False)
        tools = guard.allowed_tools()
        print(f"Ferramentas permitidas para '{agent}':")
        for t in tools:
            risk = " ⚠️ HIGH-RISK" if t in HIGH_RISK_TOOLS else ""
            print(f"  • {t}{risk}")

    elif cmd == "audit":
        last = int(args[2]) if len(args) == 3 and args[1] == "--last" else 20
        entries = ToolGuard.audit_report(last)
        if not entries:
            print("Audit log vazio.")
        else:
            print(f"Últimas {len(entries)} entradas do audit log:\n")
            for e in entries:
                status = "✅" if e["allowed"] else "❌"
                risk = " ⚠️" if e.get("risk") else ""
                print(f"  {e['ts']}  {status}{risk}  {e['agent']} → {e['tool']}")

    elif cmd == "agents":
        print("Agentes registrados no tool_guard:\n")
        for a, tools in sorted(AGENT_TOOL_PERMISSIONS.items()):
            print(f"  {a}: {', '.join(sorted(tools))}")

    else:
        _usage()
        sys.exit(1)

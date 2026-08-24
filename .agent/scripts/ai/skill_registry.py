"""
KARE Skill Registry — Dynamic Skill Discovery (Fase 3 / F3.2)
==============================================================
Escaneia .agent/skills/, constrói/atualiza SKILL-REGISTRY.json e
oferece lookup semântico por tarefa via trigger matching.

Uso:
    # Escanear e (re)construir o registro
    python skill_registry.py scan

    # Buscar skills por tarefa/contexto
    python skill_registry.py query "criar user story com ACs"

    # Listar skills sem nenhum agente referenciando (candidatas a deprecação)
    python skill_registry.py audit --unused

    # Validar consistência (agentes referenciando skills inexistentes)
    python skill_registry.py validate

    # Exibir todas as skills em formato tabular
    python skill_registry.py list

    # Forçar re-scan e exportar
    python skill_registry.py scan --output .agent/skills/SKILL-REGISTRY.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Paths ─────────────────────────────────────────────────────────────────────

WORKSPACE = Path(__file__).resolve().parents[3]  # raiz do repo (script está em .agent/scripts/ai/)
SKILLS_DIR  = WORKSPACE / ".agent" / "skills"
AGENTS_DIR  = WORKSPACE / ".agent" / "agents"
REGISTRY_PATH = SKILLS_DIR / "SKILL-REGISTRY.json"

# ── Frontmatter parser ────────────────────────────────────────────────────────

_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    current_key = None
    current_list: list | None = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        # YAML list item
        if line.startswith("  - "):
            if current_list is not None:
                current_list.append(line.strip("  - ").strip().strip('"\''))
            continue
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip().strip('"\'')
            if v == ">":
                # YAML folded block scalar (multi-linha) — as linhas seguintes
                # indentadas são texto contínuo, não itens de lista.
                current_key = k
                current_list = None
                out[k] = ""
            elif v == "":
                current_key = k
                current_list = []
                out[k] = current_list
            elif v.startswith("["):
                items = [i.strip().strip("'\"") for i in v.strip("[]").split(",") if i.strip()]
                out[k] = items
                current_key = k
                current_list = None
            else:
                out[k] = v
                current_key = k
                current_list = None
        elif current_key and line.startswith("  "):
            # continuation of multiline string
            if isinstance(out.get(current_key), str):
                out[current_key] = (out[current_key] + " " + line.strip()).strip()
    return out


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class SkillEntry:
    name: str
    path: str
    description: str
    triggers: list[str] = field(default_factory=list)
    agents_using: list[str] = field(default_factory=list)
    deprecated: bool = False
    last_scanned: str = ""


@dataclass
class Registry:
    version: str = "1.0.0"
    generated_at: str = ""
    total_skills: int = 0
    skills: list[SkillEntry] = field(default_factory=list)


# ── Scanner ───────────────────────────────────────────────────────────────────

def scan_skills() -> list[SkillEntry]:
    """Scan .agent/skills/ and build SkillEntry for each.

    Skills vivem em subpastas por categoria (ex: 01-upstream/project-discovery/
    SKILL.md), não direto em .agent/skills/ — por isso a busca é recursiva
    (rglob), não um iterdir() raso."""
    entries: list[SkillEntry] = []
    for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
        raw = skill_md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(raw)

        name = fm.get("name") or skill_md.parent.name
        description = fm.get("description", "")
        if isinstance(description, list):
            description = " ".join(description)
        triggers = fm.get("triggers", [])
        if isinstance(triggers, str):
            triggers = [triggers]

        entries.append(SkillEntry(
            name=name,
            path=str(skill_md.relative_to(WORKSPACE)).replace("\\", "/"),
            description=description,
            triggers=triggers,
            last_scanned=datetime.now(timezone.utc).isoformat(),
        ))
    return entries


def find_agents_per_skill(entries: list[SkillEntry]) -> dict[str, list[str]]:
    """Cross-reference: for each skill, which agents declare it in `skills:`."""
    skill_agents: dict[str, list[str]] = {e.name: [] for e in entries}

    for agent_md in sorted(AGENTS_DIR.glob("*.md")):
        raw = agent_md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(raw)
        declared = fm.get("skills", [])
        if isinstance(declared, str):
            declared = [declared]
        for sk in declared:
            sk = sk.strip()
            if sk in skill_agents:
                skill_agents[sk].append(agent_md.stem)

    return skill_agents


def build_registry(entries: list[SkillEntry]) -> Registry:
    agent_map = find_agents_per_skill(entries)
    for e in entries:
        e.agents_using = agent_map.get(e.name, [])

    return Registry(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_skills=len(entries),
        skills=entries,
    )


def save_registry(registry: Registry, path: Path = REGISTRY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": registry.version,
        "generated_at": registry.generated_at,
        "total_skills": registry.total_skills,
        "skills": [asdict(e) for e in registry.skills],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_registry(path: Path = REGISTRY_PATH) -> Registry | None:
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = [SkillEntry(**s) for s in raw.get("skills", [])]
    return Registry(
        version=raw.get("version", "1.0.0"),
        generated_at=raw.get("generated_at", ""),
        total_skills=raw.get("total_skills", len(entries)),
        skills=entries,
    )


# ── Query ─────────────────────────────────────────────────────────────────────

def query_skills(text: str, registry: Registry, top: int = 5) -> list[tuple[SkillEntry, float]]:
    """
    Keyword overlap matching against triggers and description.
    Returns list of (skill, score) sorted descending.
    """
    words = set(re.sub(r"[^\w\s]", " ", text.lower()).split())
    results: list[tuple[SkillEntry, float]] = []

    for entry in registry.skills:
        score = 0.0
        # Trigger exact match = high weight
        for t in entry.triggers:
            t_words = set(t.lower().split())
            overlap = words & t_words
            if overlap:
                score += len(overlap) / max(len(t_words), 1) * 2.0
        # Description overlap = lower weight
        desc_words = set(re.sub(r"[^\w\s]", " ", entry.description.lower()).split())
        desc_overlap = words & desc_words
        if desc_overlap:
            score += len(desc_overlap) / max(len(desc_words), 1) * 0.5
        if score > 0:
            results.append((entry, round(score, 3)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top]


# ── CLI commands ──────────────────────────────────────────────────────────────

def cmd_scan(args: argparse.Namespace) -> None:
    print("Escaneando .agent/skills/ ...")
    entries = scan_skills()
    registry = build_registry(entries)
    output = Path(args.output) if args.output else REGISTRY_PATH
    save_registry(registry, output)
    print(f"✅ Registry atualizado: {output}")
    print(f"   {registry.total_skills} skills encontradas")
    unused = [e for e in registry.skills if not e.agents_using]
    if unused:
        print(f"   ⚠️  {len(unused)} skills sem agente referenciando: "
              f"{', '.join(e.name for e in unused[:5])}{'...' if len(unused) > 5 else ''}")


def cmd_query(args: argparse.Namespace) -> None:
    registry = load_registry()
    if registry is None:
        print("[ERRO] SKILL-REGISTRY.json não encontrado. Execute: python skill_registry.py scan", file=sys.stderr)
        sys.exit(1)
    results = query_skills(args.text, registry, top=args.top)
    if not results:
        print("Nenhuma skill encontrada para essa query.")
        return
    print(f"Top {len(results)} skills para: '{args.text}'\n")
    for entry, score in results:
        agents = ", ".join(entry.agents_using) or "—"
        print(f"  [{score:.2f}] {entry.name}")
        print(f"         {entry.description[:80]}")
        print(f"         Agentes: {agents}")
        print()


def cmd_list(_args: argparse.Namespace) -> None:
    registry = load_registry()
    if registry is None:
        print("[ERRO] Execute primeiro: python skill_registry.py scan", file=sys.stderr)
        sys.exit(1)
    print(f"{'Skill':<35} {'Agents':<25} {'Triggers'}")
    print("-" * 90)
    for e in registry.skills:
        agents = ", ".join(e.agents_using[:3]) or "—"
        triggers_short = ", ".join(e.triggers[:2]) or "—"
        print(f"{e.name:<35} {agents:<25} {triggers_short}")
    print(f"\nTotal: {registry.total_skills} skills | Gerado em: {registry.generated_at[:10]}")


def cmd_audit(args: argparse.Namespace) -> None:
    registry = load_registry()
    if registry is None:
        print("[ERRO] Execute primeiro: python skill_registry.py scan", file=sys.stderr)
        sys.exit(1)
    if args.unused:
        unused = [e for e in registry.skills if not e.agents_using]
        if not unused:
            print("✅ Todas as skills são referenciadas por pelo menos um agente.")
        else:
            print(f"⚠️  {len(unused)} skills sem agentes (candidatas a deprecação):\n")
            for e in unused:
                print(f"  - {e.name}")
                print(f"    {e.path}")


def cmd_validate(_args: argparse.Namespace) -> None:
    registry = load_registry()
    known = {e.name for e in registry.skills} if registry else set()
    errors: list[str] = []
    for agent_md in sorted(AGENTS_DIR.glob("*.md")):
        raw = agent_md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(raw)
        declared = fm.get("skills", [])
        if isinstance(declared, str):
            declared = [declared]
        for sk in declared:
            sk = sk.strip()
            if sk and sk not in known:
                errors.append(f"  @{agent_md.stem} → '{sk}' (skill não existe em .agent/skills/)")
    if not errors:
        print("✅ Todos os agentes referenciam skills válidas.")
    else:
        print(f"❌ {len(errors)} referências inválidas encontradas:\n")
        for e in errors:
            print(e)
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skill_registry",
        description="KARE Skill Registry — dynamic skill discovery",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="Scan and rebuild SKILL-REGISTRY.json")
    scan_p.add_argument("--output", default=None, help="Output path (default: .agent/skills/SKILL-REGISTRY.json)")

    q_p = sub.add_parser("query", help="Find skills matching a task description")
    q_p.add_argument("text", help="Task description to match against")
    q_p.add_argument("--top", type=int, default=5)

    sub.add_parser("list", help="List all registered skills")

    audit_p = sub.add_parser("audit", help="Audit skill usage")
    audit_p.add_argument("--unused", action="store_true", help="Show skills not used by any agent")

    sub.add_parser("validate", help="Validate agent→skill references")

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    cmds = {
        "scan":     cmd_scan,
        "query":    cmd_query,
        "list":     cmd_list,
        "audit":    cmd_audit,
        "validate": cmd_validate,
    }
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()

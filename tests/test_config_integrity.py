"""
Testes de integridade de configuração — pegam a classe de bug encontrada e
corrigida manualmente na preparação para open source: paths quebrados,
JSON inválido, encoding errado, frontmatter malformado.
"""

import ast
import json

import pytest

from conftest import AGENT_DIR, REPO_ROOT, load_module

# JSONC (com comentários // ) — não validamos como JSON estrito
JSONC_FILES = {".vscode/settings.json", ".vscode/tasks.json"}


def _all_json_files():
    return sorted(REPO_ROOT.rglob("*.json"))


def _all_python_files():
    return sorted(
        p for p in AGENT_DIR.rglob("*.py")
        if "__pycache__" not in p.parts
    )


@pytest.mark.parametrize("path", _all_json_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_json_files_parse(path):
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel in JSONC_FILES:
        pytest.skip("JSONC (comentários) — não é JSON estrito por design")
    if "node_modules" in path.parts:
        pytest.skip("dependência de terceiros")
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", _all_python_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_python_files_are_valid_utf8_and_parse(path):
    """Pega tanto erro de sintaxe quanto arquivos salvos com encoding errado
    (cp1252/Latin-1 lido como UTF-8) — a classe de bug mais comum encontrada
    nesta base de código."""
    content = path.read_text(encoding="utf-8")  # levanta UnicodeDecodeError se cp1252
    ast.parse(content)


def test_all_agents_have_name_in_frontmatter():
    agents_dir = AGENT_DIR / "agents"
    missing = []
    for path in sorted(agents_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8-sig")
        if not content.startswith("---"):
            missing.append((path.name, "sem frontmatter"))
            continue
        end = content.find("---", 3)
        frontmatter = content[3:end] if end != -1 else ""
        if "name:" not in frontmatter:
            missing.append((path.name, "sem campo 'name'"))
    assert not missing, f"Agentes com frontmatter incompleto: {missing}"


def test_all_workflows_pass_validate_workflows():
    """Reaproveita o mesmo validador usado pela task do VS Code e pelo --fix
    manual, em vez de duplicar a lógica de checagem de frontmatter aqui."""
    validate_workflows = load_module(
        "validate_workflows", AGENT_DIR / "scripts" / "infra" / "validate_workflows.py"
    )
    workflows_dir = AGENT_DIR / "workflows"
    failures = {}
    for path in sorted(workflows_dir.glob("*.prompt.md")):
        errors, _ = validate_workflows.validate_file(path, fix=False)
        if errors:
            failures[path.name] = errors
    assert not failures, f"Workflows com frontmatter inválido: {failures}"


def test_skill_registry_matches_existing_skill_files():
    """SKILL-REGISTRY.json referencia paths de SKILL.md — garante que nenhum
    aponta para um arquivo que não existe (fica obsoleto silenciosamente
    quando uma skill é renomeada/removida sem atualizar o índice)."""
    registry_path = AGENT_DIR / "skills" / "SKILL-REGISTRY.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))

    entries = data if isinstance(data, list) else data.get("skills", [])
    missing = []
    for entry in entries:
        rel_path = entry.get("path") if isinstance(entry, dict) else None
        if not rel_path:
            continue
        if not (REPO_ROOT / rel_path).exists():
            missing.append(rel_path)

    assert not missing, f"SKILL-REGISTRY.json referencia paths inexistentes: {missing}"

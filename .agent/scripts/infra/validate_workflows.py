#!/usr/bin/env python3
"""
validate_workflows.py — Valida e auto-corrige os arquivos .prompt.md em .agent/workflows
Garante que as descriptions apareçam no slash command picker do VS Code.

Porte cross-platform de validate-workflows.ps1 (mesma lógica, mesmo comportamento).

Uso:
    python .agent/scripts/infra/validate_workflows.py
    python .agent/scripts/infra/validate_workflows.py --fix
    python .agent/scripts/infra/validate_workflows.py --workspace-root <path>

Problema resolvido:
    O VS Code/Copilot Chat não exibe a descrição dos slash commands quando:
    1. A description não está entre aspas duplas no YAML frontmatter
    2. A description contém caracteres especiais YAML sem estar entre aspas
    3. O frontmatter não começa com '---' na primeira linha
"""

import argparse
import re
import sys
from pathlib import Path

FRONTMATTER_START = re.compile(r"^\s*---", re.DOTALL)
DESCRIPTION_LINE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
FRONTMATTER_BLOCK = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
AT_UNQUOTED_COLON = re.compile(r"(:\s+)@([A-Za-z0-9_-]+)")
AT_UNQUOTED_BRACKET = re.compile(r"\[@([A-Za-z0-9_-]+)")
AT_UNQUOTED_COMMA = re.compile(r",\s*@([A-Za-z0-9_-]+)")


def validate_file(path: Path, fix: bool) -> tuple[list[str], bool]:
    """Retorna (lista de erros, arquivo foi corrigido)."""
    errors: list[str] = []
    fixed = False

    try:
        # utf-8-sig: tolera e descarta um BOM inicial, se presente (comum em
        # arquivos salvos por editores Windows) — sem isso, "﻿---" não
        # bate com o começo esperado do frontmatter.
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        errors.append(
            "Arquivo não está em UTF-8 válido (provavelmente salvo em "
            "cp1252/Latin-1) — corrija a codificação antes de validar o resto"
        )
        return errors, fixed

    if not FRONTMATTER_START.match(content):
        errors.append("Frontmatter ausente (nao comeca com ---)")

    desc_match = DESCRIPTION_LINE.search(content)
    if not desc_match:
        errors.append("Campo 'description' ausente")
    else:
        val = desc_match.group(1).strip()
        is_quoted = val.startswith('"') and val.endswith('"')
        if not is_quoted:
            errors.append(f"description sem aspas duplas: [{val}]")
            if fix:
                escaped = val.replace('"', '\\"')
                new_line = f'description: "{escaped}"'
                content = DESCRIPTION_LINE.sub(new_line, content, count=1)
                path.write_text(content, encoding="utf-8")
                fixed = True
                print(f"  CORRIGIDO (description): {path.name}")

    fm_match = FRONTMATTER_BLOCK.match(content)
    if fm_match:
        fm = fm_match.group(1)
        if re.search(r":\s+@[A-Za-z]", fm) or re.search(r"\[@[A-Za-z]", fm):
            errors.append("Frontmatter tem @ sem aspas (quebra o YAML parser do VS Code)")
            if fix:
                fm_fixed = AT_UNQUOTED_COLON.sub(r'\1"@\2"', fm)
                fm_fixed = AT_UNQUOTED_BRACKET.sub(r'["@\1"', fm_fixed)
                fm_fixed = AT_UNQUOTED_COMMA.sub(r', "@\1"', fm_fixed)
                content = content.replace(fm, fm_fixed)
                path.write_text(content, encoding="utf-8")
                fixed = True
                print(f"  CORRIGIDO (@ no FM): {path.name}")

    return errors, fixed


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida frontmatter dos slash commands do KARE-SPEC")
    parser.add_argument("--fix", action="store_true", help="Auto-corrige os problemas encontrados")
    parser.add_argument("--workspace-root", default=None, help="Raiz do workspace (padrão: auto-detectado)")
    args = parser.parse_args()

    if args.workspace_root:
        workspace_root = Path(args.workspace_root)
    else:
        workspace_root = Path(__file__).resolve().parents[3]

    workflows_dir = workspace_root / ".agent" / "workflows"

    if not workflows_dir.is_dir():
        print(f"ERRO: Pasta nao encontrada: {workflows_dir}", file=sys.stderr)
        return 1

    print()
    print("=" * 68)
    print("  KARE-SPEC: Validacao de Slash Commands")
    print(f"  Pasta: {workflows_dir}")
    print("=" * 68)
    print()

    files = sorted(workflows_dir.glob("*.prompt.md"))
    issues: dict[str, list[str]] = {}
    fixed_count = 0
    ok_count = 0

    for path in files:
        errors, was_fixed = validate_file(path, args.fix)
        if was_fixed:
            fixed_count += 1
        if errors:
            issues[path.name] = errors
            if not args.fix:
                print(f"  PROBLEMA: {path.name}")
                for e in errors:
                    print(f"    -> {e}")
        else:
            ok_count += 1

    print()
    print("=" * 68)
    print("  RESULTADO")
    print("=" * 68)
    print()
    print(f"  Total de arquivos : {len(files)}")
    print(f"  OK (sem problemas): {ok_count}")

    if args.fix and fixed_count > 0:
        print(f"  Corrigidos        : {fixed_count}")
        print()
        print("  ACAO NECESSARIA: Recarregue o VS Code para aplicar as mudancas.")
        print("  Atalho: Ctrl+Shift+P -> 'Developer: Reload Window'")
    elif issues:
        print(f"  Com problemas     : {len(issues)}")
        print()
        print("  Execute com --fix para corrigir automaticamente:")
        print("  python .agent/scripts/infra/validate_workflows.py --fix")
    else:
        print()
        print("  TUDO OK! Se as descriptions ainda nao aparecem no VS Code:")
        print("  Recarregue a janela: Ctrl+Shift+P -> 'Developer: Reload Window'")

    print()

    if issues and not args.fix:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

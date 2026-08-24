#!/usr/bin/env python3
"""
secret_scan.py — Varredura de credenciais em texto plano no repositório.

Reaproveita os mesmos padrões do hook local .agent/scripts/hooks/pre-commit,
mas aplicados a todo o conteúdo versionado (não só a um diff de commit) —
defesa em profundidade para CI, cobrindo quem commitar sem o hook instalado
ou quem fizer push direto.

Uso:
    python .agent/scripts/guards/secret_scan.py            # escaneia git ls-files
    python .agent/scripts/guards/secret_scan.py --path <p> # escaneia um path específico
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]

# Mesmos padrões de .agent/scripts/hooks/pre-commit
CREDENTIAL_PATTERNS = re.compile(
    r"ATATT3x[A-Za-z0-9+/]"
    r"|password\s*=\s*[\"'][^\"']{6,}"
    r"|api_token\s*=\s*[\"'][^\"']{6,}"
    r"|secret\s*=\s*[\"'][^\"']{6,}"
    r"|Bearer [A-Za-z0-9\-_.]{20,}",
    re.IGNORECASE,
)

# Se o "valor" é uma referência de variável (env var), não é uma credencial real
SAFE_VALUE_PATTERN = re.compile(
    r"=\s*['\"]?\$\{?[A-Za-z_][A-Za-z0-9_]*\}?['\"]?"
)

SKIP_SUFFIXES = (
    ".enc", ".key", ".db", ".pdf", ".pptx",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2",
)


def _tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=repo_root, capture_output=True, text=True, check=True,
    )
    return [repo_root / line for line in result.stdout.splitlines() if line]


def scan_file(path: Path) -> list[str]:
    """Retorna as linhas suspeitas encontradas no arquivo (vazia se limpo)."""
    if path.suffix.lower() in SKIP_SUFFIXES:
        return []
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    hits = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        if not CREDENTIAL_PATTERNS.search(line):
            continue
        if SAFE_VALUE_PATTERN.search(line):
            continue  # valor é uma referência de variável, não literal
        hits.append(f"{lineno}: {line.strip()}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=None, help="Escaneia um único arquivo/pasta em vez de git ls-files")
    args = parser.parse_args()

    if args.path:
        target = Path(args.path)
        files = [target] if target.is_file() else sorted(target.rglob("*"))
    else:
        files = _tracked_files(REPO_ROOT)

    blocked = False
    for path in files:
        if not path.is_file():
            continue
        hits = scan_file(path)
        if hits:
            blocked = True
            try:
                rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
            except ValueError:
                rel = path
            print(f"\n⛔ Credencial suspeita em: {rel}")
            for hit in hits[:3]:
                print(f"    {hit}")

    if blocked:
        print("\nCredenciais em texto plano encontradas — ver detalhes acima.")
        return 1

    print("Nenhuma credencial em texto plano encontrada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

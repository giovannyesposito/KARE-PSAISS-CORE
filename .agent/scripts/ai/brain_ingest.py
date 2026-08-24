#!/usr/bin/env python3
"""Brain Ingest Script

Ingesta arquivos de conhecimento para o cofre Obsidian por domínio.
Aceita arquivo ou pasta e cria uma nota de conhecimento com links para anexos.
"""

import argparse
import hashlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


DOMAIN_MAP: Dict[str, Tuple[str, str]] = {
    "arquitetura": ("ARQUITETURA", "Arquitetura"),
    "sistemas": ("SISTEMAS", "Sistemas"),
    "integracoes": ("INTEGRACOES", "Integrações"),
    "apis": ("APIS", "APIs"),
    "observabilidade": ("OBSERVABILIDADE", "Observabilidade"),
    "stakeholders": ("STAKEHOLDERS", "Stakeholders"),
    "projetos": ("PROJETOS_INICIATIVAS", "Projetos/Iniciativas"),
    "projetos-iniciativas": ("PROJETOS_INICIATIVAS", "Projetos/Iniciativas"),
}

ALLOWED_EXT = {
    ".pdf", ".txt", ".md", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".csv", ".json", ".yaml", ".yml"
}


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "entrada"


def gather_files(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]
    files: List[Path] = []
    for p in input_path.rglob("*"):
        if p.is_file():
            files.append(p)
    return sorted(files)


def short_hash(path: Path) -> str:
    h = hashlib.sha1(path.as_posix().encode("utf-8")).hexdigest()
    return h[:8]


def ensure_domain_index(index_path: Path, domain_title: str) -> None:
    if index_path.exists():
        return
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        f"# {index_path.parent.name}\n\n"
        f"Índice de conhecimento do domínio {domain_title}.\n\n"
        "## Entradas\n\n"
        "Nenhuma entrada registrada.\n",
        encoding="utf-8",
    )


def append_entry_to_index(index_path: Path, note_link: str) -> None:
    text = index_path.read_text(encoding="utf-8")
    if note_link in text:
        return
    if "Nenhuma entrada registrada." in text:
        text = text.replace("Nenhuma entrada registrada.", f"- {note_link}")
    else:
        text += f"\n- {note_link}\n"
    index_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta conhecimento para o cofre Obsidian")
    parser.add_argument("project", help="Raiz do projeto")
    parser.add_argument("--input", required=True, help="Arquivo ou pasta de entrada")
    parser.add_argument("--domain", required=True, help="Domínio alvo")
    parser.add_argument("--context", help="Context slug relacionado")
    parser.add_argument("--title", help="Título da nota de conhecimento")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    input_path = Path(args.input).resolve()

    if args.domain.lower() not in DOMAIN_MAP:
        print("ERR Domain inválido. Use: " + ", ".join(sorted(DOMAIN_MAP.keys())))
        sys.exit(1)

    if not input_path.exists():
        print(f"ERR Input não encontrado: {input_path}")
        sys.exit(1)

    domain_folder, domain_title = DOMAIN_MAP[args.domain.lower()]

    vault_dir = root / "_outputs" / "brain-knowledge"
    domain_dir = vault_dir / domain_folder
    index_path = domain_dir / f"{domain_folder}.md"
    base_dir = vault_dir / "base-conhecimento" / domain_folder

    domain_dir.mkdir(parents=True, exist_ok=True)
    base_dir.mkdir(parents=True, exist_ok=True)
    ensure_domain_index(index_path, domain_title)

    files = gather_files(input_path)
    if not files:
        print("ERR Nenhum arquivo encontrado para ingestão")
        sys.exit(2)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    title = args.title or f"ingest-{domain_folder.lower()}-{timestamp}"
    note_name = f"{slugify(title)}.md"
    note_path = domain_dir / note_name

    copied_links: List[str] = []
    ignored: List[str] = []

    for file_path in files:
        ext = file_path.suffix.lower()
        rel_name = f"{slugify(file_path.stem)}-{short_hash(file_path)}{ext}"
        target = base_dir / rel_name
        shutil.copy2(file_path, target)

        rel = target.relative_to(root).as_posix()
        copied_links.append(f"- [{rel}]({rel})")

        if ext not in ALLOWED_EXT:
            ignored.append(file_path.name)

    context_line = f"- Contexto relacionado: {args.context}" if args.context else "- Contexto relacionado: não informado"

    note_content = (
        f"# {title}\n\n"
        f"## Metadados\n\n"
        f"- Domínio: {domain_title}\n"
        f"{context_line}\n"
        f"- Data de ingestão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- Total de arquivos: {len(copied_links)}\n\n"
        f"## Anexos\n\n"
        + "\n".join(copied_links)
        + "\n\n## Observações\n\n"
        + ("- Alguns arquivos têm extensões fora da lista principal e foram anexados como bruto: " + ", ".join(ignored) if ignored else "- Ingestão concluída sem ressalvas.")
        + "\n"
    )

    note_path.write_text(note_content, encoding="utf-8")

    note_rel = note_path.relative_to(vault_dir).as_posix()
    append_entry_to_index(index_path, f"[[{note_rel[:-3]}]]")

    print("OK Brain ingest concluído")
    print(f"Domínio: {domain_title}")
    print(f"Nota: {note_path}")
    print(f"Arquivos anexados: {len(copied_links)}")


if __name__ == "__main__":
    main()

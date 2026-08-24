#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARE — Export Demands to PDF
Converte artefatos markdown das demandas processadas em PDF
e replica estrutura no OneDrive com mesmo layout
"""

import os
import sys
import re
import textwrap
import argparse
from pathlib import Path
from datetime import datetime
import json

try:
    import pypandoc
    has_pypandoc = True
except ImportError:
    has_pypandoc = False

try:
    from weasyprint import HTML, CSS
    has_weasyprint = True
except ImportError:
    has_weasyprint = False

# ────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_DIR = REPO_ROOT / "demandas_processadas"

# Mapeamento: tipo de arquivo → prioridade de conversão
ARTIFACT_PRIORITY = {
    "PRD.md": 1,
    "PRD-REVIEW": 2,
    "BACKLOG.md": 3,
    "USER_STORY_MAP.md": 4,
    "RAID.md": 5,
    "ARCHITECTURE.md": 6,
    "ADR": 7,
    "PROJECT_BRIEF.md": 8,
    "ORCHESTRATION_REPORT.md": 9,
}

# ────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────

def get_artifact_type(filename):
    """Identifica tipo de artefato pelo nome do arquivo"""
    name = filename.lower()
    for artifact, priority in ARTIFACT_PRIORITY.items():
        if artifact.lower() in name or artifact.lower().replace(".md", "") in name:
            return priority, artifact
    return 999, "OTHER"

def sanitize_filename(name):
    """Remove caracteres inválidos de caminho"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def markdown_to_plain_lines(md_content):
    """Converte markdown para linhas de texto legíveis para PDF simples."""
    lines = []
    in_code_block = False

    for raw in md_content.splitlines():
        line = raw.rstrip()

        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                lines.append("[CODE]")
            else:
                lines.append("[/CODE]")
            continue

        if in_code_block:
            lines.append(f"    {line}")
            continue

        if line.startswith("# "):
            lines.append("")
            lines.append(line[2:].strip().upper())
            lines.append("=" * min(80, len(line[2:].strip())))
            lines.append("")
            continue
        if line.startswith("## "):
            lines.append("")
            lines.append(line[3:].strip())
            lines.append("-" * min(80, len(line[3:].strip())))
            lines.append("")
            continue
        if line.startswith("### "):
            lines.append("")
            lines.append(f"* {line[4:].strip()}")
            lines.append("")
            continue

        # Remove marcações markdown simples para legibilidade.
        cleaned = line
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"`(.*?)`", r"\1", cleaned)
        cleaned = cleaned.replace("|", " | ")

        if not cleaned.strip():
            lines.append("")
            continue

        wrapped = textwrap.wrap(
            cleaned,
            width=100,
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.extend(wrapped if wrapped else [cleaned])

    return lines

def _escape_pdf_text_bytes(text):
    """Escapa bytes para string literal PDF (parenteses e barra invertida)."""
    raw = text.encode("cp1252", errors="replace")
    escaped = bytearray()
    for byte in raw:
        if byte in (0x28, 0x29, 0x5C):  # (, ), \\
            escaped.append(0x5C)
        escaped.append(byte)
    return bytes(escaped)

def write_pdf_native(md_content, pdf_file):
    """Gera um PDF válido nativo (sem dependências externas)."""
    page_width = 595
    page_height = 842
    margin_x = 40
    start_y = 800
    line_height = 14
    lines_per_page = 52

    plain_lines = markdown_to_plain_lines(md_content)
    if not plain_lines:
        plain_lines = ["Documento vazio."]

    pages = []
    for idx in range(0, len(plain_lines), lines_per_page):
        pages.append(plain_lines[idx:idx + lines_per_page])

    objects = []

    # 1: Fonte
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # 2: Pages root (placeholder /Kids)
    objects.append(b"<< /Type /Pages /Kids [] /Count 0 >>")

    page_object_ids = []
    for page_index, page_lines in enumerate(pages):
        content_lines = [
            b"BT",
            b"/F1 10 Tf",
            f"1 0 0 1 {margin_x} {start_y} Tm".encode("ascii"),
        ]

        for line in page_lines:
            content_lines.append(b"(" + _escape_pdf_text_bytes(line) + b") Tj")
            content_lines.append(f"0 -{line_height} Td".encode("ascii"))

        footer = f"Pagina {page_index + 1}/{len(pages)} - Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        content_lines.extend([
            f"1 0 0 1 {margin_x} 30 Tm".encode("ascii"),
            b"/F1 8 Tf",
            b"(" + _escape_pdf_text_bytes(footer) + b") Tj",
            b"ET",
        ])

        stream = b"\n".join(content_lines) + b"\n"
        content_obj = b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream"
        objects.append(content_obj)
        content_object_id = len(objects)

        page_obj = (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
            + str(page_width).encode("ascii")
            + b" "
            + str(page_height).encode("ascii")
            + b"] /Resources << /Font << /F1 1 0 R >> >> /Contents "
            + str(content_object_id).encode("ascii")
            + b" 0 R >>"
        )
        objects.append(page_obj)
        page_object_ids.append(len(objects))

    # Atualiza objeto 2 com Kids + Count
    kids_refs = b" ".join(f"{pid} 0 R".encode("ascii") for pid in page_object_ids)
    objects[1] = (
        b"<< /Type /Pages /Kids ["
        + kids_refs
        + b"] /Count "
        + str(len(page_object_ids)).encode("ascii")
        + b" >>"
    )

    # Catálogo
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    catalog_id = len(objects)

    # Serialização PDF
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj_content in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        output.extend(obj_content)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        output.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    output.extend(
        b"trailer\n<< /Size "
        + str(len(objects) + 1).encode("ascii")
        + b" /Root "
        + str(catalog_id).encode("ascii")
        + b" 0 R >>\n"
    )
    output.extend(f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii"))

    pdf_file.write_bytes(bytes(output))
    return True, "Convertido com PDF nativo (sem dependências)"

def markdown_to_html(md_content):
    """Converte markdown para HTML com styling básico"""
    # Adiciona CSS mínimo para formatação
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"/>
    <title>Artefato</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
        }}
        h1 {{ color: #032d60; border-bottom: 3px solid #0176d3; padding-bottom: 10px; }}
        h2 {{ color: #0176d3; margin-top: 25px; }}
        h3 {{ color: #555; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; }}
        a {{ color: #0176d3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .alert {{ padding: 12px; margin: 15px 0; border-left: 4px solid; border-radius: 4px; }}
        .alert-info {{ border-color: #0176d3; background: #e8f4fd; }}
        .alert-warning {{ border-color: #dd7a01; background: #fdf3c8; }}
        .alert-danger {{ border-color: #ba0517; background: #fde9e9; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }}
    </style>
</head>
<body>
{md_content}
</body>
</html>"""
    return html

def convert_md_to_pdf_weasyprint(md_file, pdf_file):
    """Converte MD para PDF usando WeasyPrint"""
    if not md_file.exists():
        return False, "Arquivo não encontrado"
    
    try:
        md_content = md_file.read_text(encoding='utf-8')
        
        # Conversão markdown básica para HTML
        # (em produção, usar markdown library ou pandoc)
        html_content = markdown_to_html(md_content)
        
        # WeasyPrint: HTML → PDF
        HTML(string=html_content).write_pdf(pdf_file)
        return True, "Convertido com WeasyPrint"
    except Exception as e:
        return False, f"Erro WeasyPrint: {str(e)}"

def convert_md_to_pdf_pypandoc(md_file, pdf_file):
    """Converte MD para PDF usando Pandoc (via pypandoc)"""
    if not md_file.exists():
        return False, "Arquivo não encontrado"
    
    try:
        md_content = md_file.read_text(encoding='utf-8')
        output = pypandoc.convert_text(md_content, 'pdf', format='md', 
                                       outputfile=str(pdf_file),
                                       extra_args=['--pdf-engine=wkhtmltopdf'])
        return True, "Convertido com Pandoc"
    except Exception as e:
        return False, f"Erro Pandoc: {str(e)}"

def convert_md_to_pdf_fallback(md_file, pdf_file):
    """Fallback final: gera PDF nativo sem libs externas."""
    if not md_file.exists():
        return False, "Arquivo não encontrado"
    
    try:
        md_content = md_file.read_text(encoding='utf-8')

        # Remove versões antigas de fallback se existirem.
        legacy_txt = pdf_file.with_suffix('.txt')
        legacy_readme = pdf_file.parent / f"_LEIA-ME_{pdf_file.stem}.txt"
        if legacy_txt.exists():
            legacy_txt.unlink()
        if legacy_readme.exists():
            legacy_readme.unlink()

        return write_pdf_native(md_content, pdf_file)
    except Exception as e:
        return False, f"Erro fallback: {str(e)}"

def convert_md_to_pdf(md_file, pdf_file):
    """Tenta converter MD para PDF com suporte a múltiplas estratégias"""
    # Estratégia 1: WeasyPrint
    if has_weasyprint:
        success, msg = convert_md_to_pdf_weasyprint(md_file, pdf_file)
        if success:
            return True, msg
    
    # Estratégia 2: Pandoc
    if has_pypandoc:
        success, msg = convert_md_to_pdf_pypandoc(md_file, pdf_file)
        if success:
            return True, msg
    
    # Estratégia 3: Fallback (cópia como .txt)
    success, msg = convert_md_to_pdf_fallback(md_file, pdf_file)
    return success, msg

def process_initiative(initiative_dir, dest_parent):
    """Processa uma iniciativa: converte todos os .md e replica estrutura"""
    ini_name = initiative_dir.name
    dest_ini_dir = dest_parent / ini_name
    dest_ini_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📋 Processando: {ini_name}")
    
    # Coleta todos os .md da iniciativa
    md_files = list(initiative_dir.rglob("*.md"))
    md_files.sort(key=lambda f: (get_artifact_type(f.name)[0], f.name))
    
    results = []
    
    for md_file in md_files:
        rel_path = md_file.relative_to(initiative_dir)
        
        # Cria estrutura de subdiretório se necessário
        dest_subdir = dest_ini_dir / rel_path.parent
        dest_subdir.mkdir(parents=True, exist_ok=True)
        
        # Gera nome do PDF
        pdf_name = md_file.stem + ".pdf"
        pdf_file = dest_subdir / pdf_name
        
        # Converte
        success, msg = convert_md_to_pdf(md_file, pdf_file)
        
        artifact_type = get_artifact_type(md_file.name)[1]
        status = "✅" if success else "⚠️"
        print(f"  {status} {artifact_type:25} {rel_path} → {pdf_name}")
        
        results.append({
            "source": str(md_file),
            "dest": str(pdf_file),
            "artifact": artifact_type,
            "success": success,
            "message": msg
        })
    
    return results

def generate_report(all_results, dest_dir):
    """Gera relatório de conversão"""
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_conversions": len(all_results),
        "successful": sum(1 for r in all_results if r["success"]),
        "failed": sum(1 for r in all_results if not r["success"]),
        "details": all_results
    }
    
    report_file = dest_dir / "EXPORT_REPORT.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    
    return report

def resolve_initiatives(source_dir, context_filter=None):
    """Resolve as iniciativas que serao exportadas."""
    candidates = [d for d in source_dir.iterdir() if d.is_dir() and d.name.startswith("INI-")]
    candidates.sort()

    if not context_filter:
        return candidates

    needle = context_filter.strip().lower()
    selected = []
    for item in candidates:
        name = item.name.lower()
        if needle in name or name.startswith(needle):
            selected.append(item)
    return selected

def parse_args():
    """Parse de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Exporta artefatos markdown para PDF sob demanda."
    )
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE_DIR),
        help="Diretorio de origem das demandas (default: demandas_processadas do repo).",
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Diretorio de destino para os PDFs (obrigatorio).",
    )
    parser.add_argument(
        "--context",
        help="Filtro opcional para uma iniciativa (ex: INI-001 ou 'Checkout Mobile').",
    )
    return parser.parse_args()

def main():
    """Orquestra conversão de todas as iniciativas"""
    args = parse_args()
    source_dir = Path(args.source).expanduser().resolve()
    dest_dir = Path(args.dest).expanduser().resolve()

    print("="*70)
    print("KARE — Exportação de Artefatos para PDF")
    print("="*70)
    print(f"Origem: {source_dir}")
    print(f"Destino: {dest_dir}")
    
    # Valida diretórios
    if not source_dir.exists():
        print(f"❌ Diretório de origem não encontrado: {source_dir}")
        return 1

    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica libs disponíveis
    print("\n📦 Bibliotecas Disponíveis:")
    print(f"  WeasyPrint: {'✅' if has_weasyprint else '❌'}")
    print(f"  Pandoc/PyPandoc: {'✅' if has_pypandoc else '❌'}")
    
    if not (has_weasyprint or has_pypandoc):
        print("  ⚠️  Nenhuma biblioteca de conversão avançada encontrada.")
        print("     Usando gerador PDF nativo sem dependências externas.")
    
    # Localiza todas as iniciativas
    initiatives = resolve_initiatives(source_dir, args.context)

    if args.context and not initiatives:
        print(f"❌ Nenhuma iniciativa encontrada para o filtro: {args.context}")
        return 1
    
    print(f"\n🔍 Iniciativas encontradas: {len(initiatives)}")
    
    # Processa cada iniciativa
    all_results = []
    for ini_dir in initiatives:
        results = process_initiative(ini_dir, dest_dir)
        all_results.extend(results)
    
    # Gera relatório
    report = generate_report(all_results, dest_dir)
    
    # Sumário final
    print("\n" + "="*70)
    print("📊 SUMÁRIO DA EXPORTAÇÃO")
    print("="*70)
    print(f"Total de conversões: {report['total_conversions']}")
    print(f"Sucesso: {report['successful']}")
    print(f"Falhas/Fallbacks: {report['failed']}")
    print(f"Relatório: {dest_dir / 'EXPORT_REPORT.json'}")
    print("="*70)
    
    return 0 if report['failed'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

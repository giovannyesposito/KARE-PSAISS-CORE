"""
_gen_rso_pdf.py — Exportador oficial de RSO para PDF (KARE Agile Agent)
=======================================================================
TEMPLATE OFICIAL — Não modificar o estilo visual sem aprovação.

USO:
    python .agent/scripts/_gen_rso_pdf.py --src <caminho.md> --dest <caminho.pdf>

    Se --dest for omitido, gera o PDF na mesma pasta do .md com o mesmo nome.

ESTILO PADRÃO (inviolável):
    - Título (#):     Helvetica Bold 16pt, cinza escuro (30,30,30)
    - Seções (##):    Helvetica Bold 13pt, AZUL (20,80,160) — sem fundo/caixa
    - Subseções (###): Helvetica Bold 11pt, cinza (50,50,50)
    - Tabelas (|):    Helvetica 7pt, células com borda, col_w = max(170/n, 10)
    - Citações (>):   Helvetica Itálico 9pt, cinza (80,80,80), fundo (245,245,245)
    - Listas (- / *): Helvetica 9pt, prefixo "  * "
    - Corpo:          Helvetica 9pt, cinza escuro (30,30,30)
    - Sempre pdf.set_x(20) antes de multi_cell()
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("ERRO: fpdf2 não instalado. Execute: pip install fpdf2")
    sys.exit(1)

UNICODE_MAP = {
    '\u2014': '--', '\u2013': '-', '\u2019': "'", '\u2018': "'",
    '\u201c': '"',  '\u201d': '"',  '\u2022': '*',  '\u2026': '...',
    '\u00e9': 'e',  '\u00ea': 'e',  '\u00e3': 'a',  '\u00e7': 'c',
    '\u00e0': 'a',  '\u00e1': 'a',  '\u00ed': 'i',  '\u00f3': 'o',
    '\u00fa': 'u',  '\u00f5': 'o',  '\u00fc': 'u',  '\u00e2': 'a',
    '\u00f4': 'o',  '\u00fb': 'u',  '\u00ee': 'i',  '\u00e8': 'e',
    '\u00c9': 'E',  '\u00c3': 'A',  '\u00c7': 'C',  '\u00d3': 'O',
    '\u00da': 'U',  '\u00d5': 'O',  '\u00c2': 'A',  '\u00d4': 'O',
    '\u2192': '->',  '\u2190': '<-',  '\u2194': '<->',
    '\u00bb': '>>',  '\u00ab': '<<',
}


def clean(s: str) -> str:
    """Remove markdown inline e normaliza para latin-1."""
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', re.sub(r'`(.+?)`', r'\1', s))
    for uni, asc in UNICODE_MAP.items():
        s = s.replace(uni, asc)
    # Remove emojis e demais caracteres não-latin1
    return s.encode('latin-1', errors='replace').decode('latin-1')


def render_md_to_pdf(src: Path, dest: Path) -> None:
    text = src.read_text(encoding='utf-8')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    for line in text.splitlines():
        stripped = line.strip()

        # --- Título principal ---
        if stripped.startswith('# ') and not stripped.startswith('## '):
            pdf.set_x(20)
            pdf.set_font('Helvetica', 'B', 16)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 9, clean(stripped[2:]))
            pdf.ln(3)

        # --- Seção (##) — AZUL, sem fundo ---
        elif stripped.startswith('## ') and not stripped.startswith('### '):
            pdf.set_x(20)
            pdf.set_font('Helvetica', 'B', 13)
            pdf.set_text_color(20, 80, 160)
            pdf.multi_cell(0, 7, clean(stripped[3:]))
            pdf.ln(2)

        # --- Subseção (###) ---
        elif stripped.startswith('### '):
            pdf.set_x(20)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, clean(stripped[4:]))
            pdf.ln(1)

        # --- Tabela (|) ---
        elif stripped.startswith('|'):
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            # Pula linhas separadoras (---)
            if all(set(c.replace('-', '').replace(':', '').replace(' ', '')) == set()
                   for c in cols):
                continue
            n = max(len(cols), 1)
            col_w = max(170 / n, 10)
            pdf.set_x(20)
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(30, 30, 30)
            for col in cols:
                pdf.cell(col_w, 5, clean(col)[:int(col_w / 2.2)], border=1)
            pdf.ln()

        # --- Citação (>) ---
        elif stripped.startswith('> '):
            pdf.set_x(20)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(80, 80, 80)
            pdf.set_fill_color(245, 245, 245)
            pdf.multi_cell(0, 5, clean(stripped[2:]), fill=True)
            pdf.ln(1)

        # --- Lista (- ou *) ---
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_x(20)
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5, '  * ' + clean(stripped[2:]))

        # --- Separador / linha vazia ---
        elif stripped in ('', '---'):
            pdf.set_x(20)
            pdf.ln(2)

        # --- Corpo padrão ---
        else:
            pdf.set_x(20)
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5, clean(stripped))

    pdf.output(str(dest))
    print(f'PDF gerado: {dest}')


def main():
    parser = argparse.ArgumentParser(
        description='Exporta RSO Markdown → PDF no template oficial KARE.')
    parser.add_argument('--src', required=True, help='Caminho do arquivo .md de entrada')
    parser.add_argument('--dest', default=None, help='Caminho do .pdf de saída (opcional)')
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f'ERRO: arquivo não encontrado: {src}')
        sys.exit(1)

    dest = Path(args.dest) if args.dest else src.with_suffix('.pdf')
    render_md_to_pdf(src, dest)


if __name__ == '__main__':
    main()

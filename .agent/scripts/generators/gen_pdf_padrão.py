#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARE — gen_pdf_padrao.py
========================
Exporta Markdown → PDF com visual fiel ao preview VS Code / GitHub (tema claro).

Stack (zero dependências externas além das já instaladas):
  - fpdf2   2.8+  → renderização PDF
  - Markdown 3+   → conversão MD → HTML
  - Pygments 2+   → destaque de sintaxe em code blocks

Visual replicado:
  - GitHub Light: tipografia hierárquica, bordas em H1/H2, code blocks cinza,
    tabelas com header sombreado, blockquotes com barra lateral, listas, HR.

Uso:
  python .agent/scripts/gen_pdf_padrao.py --src README.md
  python .agent/scripts/gen_pdf_padrao.py --src README.md --dest C:/saida/README.pdf
  python .agent/scripts/gen_pdf_padrao.py --src README.md --dest "C:/path/"   # pasta

  # Modo estampagem (substitui rodapé de PDF existente):
  python .agent/scripts/gen_pdf_padrao.py --stamp --src documento.pdf
  python .agent/scripts/gen_pdf_padrao.py --stamp --src documento.pdf --dest assinado.pdf
  python .agent/scripts/gen_pdf_padrao.py --stamp --src documento.pdf --footer-text "Gerado pelo KARE KARE Agile Agent  •  Maio/26"

Saída padrão (sem --dest): mesmo diretório e nome do arquivo fonte.
"""

import sys
import re
import argparse
import html as html_module
from pathlib import Path
from datetime import datetime

# Windows: garante saída UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────── DEPENDÊNCIAS ────────────────
try:
    from fpdf import FPDF
    from fpdf.fonts import FontFace
except ImportError:
    print("❌ fpdf2 não instalado. Execute: pip install fpdf2", file=sys.stderr)
    sys.exit(1)

try:
    import markdown
    from markdown.extensions.tables import TableExtension          # noqa: F401
    from markdown.extensions.fenced_code import FencedCodeExtension  # noqa: F401
    from markdown.extensions.toc import TocExtension                 # noqa: F401
except ImportError:
    print("❌ Markdown não instalado. Execute: pip install Markdown", file=sys.stderr)
    sys.exit(1)

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_OK = True
except ImportError:
    PYGMENTS_OK = False

# ──────────────────────────────────────────────── TEMA GITHUB LIGHT ──────────
C_TEXT       = (36,  41,  47)    # #24292f — corpo
C_MUTED      = (110, 119, 129)   # #6e7781 — subtítulos, blockquote
C_LINK       = (9,   105, 218)   # #0969da — links
C_CODE_BG    = (246, 248, 250)   # #f6f8fa — fundo code block
C_TABLE_HDR  = (246, 248, 250)   # mesmo que code bg
C_HR         = (208, 215, 222)   # #d0d7de — linhas divisórias
C_QUOTE_BAR  = (223, 226, 229)   # #dfe2e5 — barra lateral blockquote
C_WHITE      = (255, 255, 255)

FONT_BODY    = "Calibri"
FONT_MONO    = "Consolas"
SIZE_BODY    = 9.5
SIZE_SMALL   = 8.5
SIZE_FOOTER  = 8.0

# Mapeamento fontes TTF do sistema Windows (Unicode completo)
_WIN_FONTS = {
    "Calibri":  {
        "": "C:/Windows/Fonts/calibri.ttf",
        "B": "C:/Windows/Fonts/calibrib.ttf",
        "I": "C:/Windows/Fonts/calibrii.ttf",
        "BI": "C:/Windows/Fonts/calibriz.ttf",
    },
    "Consolas": {
        "": "C:/Windows/Fonts/consola.ttf",
        "B": "C:/Windows/Fonts/consolab.ttf",
        "I": "C:/Windows/Fonts/consolai.ttf",
        "BI": "C:/Windows/Fonts/consolaz.ttf",
    },
}

# Tamanhos de heading
H_SIZES = {1: 22, 2: 17, 3: 14, 4: 12, 5: 11, 6: 10}

# ──────────────────────────────────────────────── FPDF CLASS ─────────────────
def _load_fonts(pdf: "GithubMarkdownPDF") -> str:
    """
    Carrega fontes TTF do sistema. Retorna o nome base que foi carregado.
    Se não encontrar Calibri/Consolas, usa built-in Helvetica/Courier com
    sanitização agressiva de Unicode.
    """
    import os
    body_ok = all(os.path.exists(p) for p in _WIN_FONTS["Calibri"].values())
    mono_ok = all(os.path.exists(p) for p in _WIN_FONTS["Consolas"].values())

    if body_ok:
        for style, path in _WIN_FONTS["Calibri"].items():
            pdf.add_font("Calibri", style, path)
    if mono_ok:
        for style, path in _WIN_FONTS["Consolas"].items():
            pdf.add_font("Consolas", style, path)

    return "Calibri" if body_ok else "Helvetica", "Consolas" if mono_ok else "Courier"


class GithubMarkdownPDF(FPDF):
    """FPDF2 com header/footer estilo GitHub preview e helpers visuais."""

    def __init__(self, src_path: Path):
        super().__init__()
        self.src_path = src_path
        # Carrega fontes TTF para suporte Unicode completo (Δ, →, emojis, etc.)
        self._font_body, self._font_mono = _load_fonts(self)
        self.set_margins(left=20, top=18, right=20)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font(self._font_body, "I", SIZE_FOOTER)
        self.set_text_color(*C_MUTED)
        self.cell(0, 5, self.src_path.name, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*C_TEXT)
        self.ln(1)

    def footer(self):
        self.set_y(-13)
        self.set_font(self._font_body, "I", SIZE_FOOTER)
        self.set_text_color(*C_MUTED)
        ts = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 5, f"Gerado em {ts}  •  Página {self.page_no()}/{{nb}}", align="C")
        self.set_text_color(*C_TEXT)

    def draw_hr(self, thin: bool = False):
        """Linha divisória horizontal estilo GitHub."""
        self.ln(2)
        x1, x2 = self.l_margin, self.w - self.r_margin
        y = self.get_y()
        lw = 0.15 if thin else 0.2
        self.set_draw_color(*C_HR)
        self.set_line_width(lw)
        self.line(x1, y, x2, y)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.ln(3)

    def draw_code_block(self, code_text: str, lang: str = ""):
        """Renderiza bloco de código com fundo cinza e fonte monospace."""
        self.ln(2)
        lines = code_text.split("\n")
        # Remove trailing empty line
        while lines and lines[-1].strip() == "":
            lines.pop()

        padding = 3
        line_h  = 4.2
        font_sz = 7.8
        page_w  = self.w - self.l_margin - self.r_margin
        block_h = padding * 2 + len(lines) * line_h

        # Page break prevention: draw on next page if block doesn't fit
        if self.get_y() + block_h > self.h - self.b_margin - 10:
            self.add_page()

        y_start = self.get_y()
        # Fundo
        self.set_fill_color(*C_CODE_BG)
        self.set_draw_color(*C_HR)
        self.set_line_width(0.15)
        self.rect(self.l_margin, y_start, page_w, block_h, style="FD")
        self.set_line_width(0.2)
        self.set_draw_color(0, 0, 0)

        # Lang label (canto superior direito)
        if lang:
            self.set_xy(self.l_margin, y_start + 1)
            self.set_font(self._font_body, "I", 6.5)
            self.set_text_color(*C_MUTED)
            self.cell(page_w - 2, line_h, lang, align="R")

        # Linhas de código
        self.set_font(self._font_mono, "", font_sz)
        self.set_text_color(*C_TEXT)
        self.set_xy(self.l_margin + padding, y_start + padding)
        for line in lines:
            # Substitui tabs por espaços
            line = line.replace("\t", "    ")
            # Remove chars de controle não imprimíveis
            line = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", line)
            # Trunca linhas muito longas usando largura real da fonte
            available_w = page_w - padding * 2
            if self.get_string_width(line) > available_w:
                while len(line) > 0 and self.get_string_width(line + "…") > available_w:
                    line = line[:-1]
                line = line + "…"
            self.set_x(self.l_margin + padding)
            self.cell(0, line_h, line, new_x="LMARGIN", new_y="NEXT")

        self.set_y(y_start + block_h)
        self.ln(3)
        self.set_font(self._font_body, "", SIZE_BODY)
        self.set_text_color(*C_TEXT)

    def draw_blockquote(self, text: str):
        """Renderiza blockquote com barra lateral esquerda e texto itálico."""
        self.ln(1)
        indent  = 5
        bar_w   = 2.5
        padding = 3
        page_w  = self.w - self.l_margin - self.r_margin - indent - padding
        y_start = self.get_y()

        self.set_font(self._font_body, "I", SIZE_BODY - 0.5)
        self.set_text_color(*C_MUTED)

        # Calcula altura do texto
        lines_needed = self.get_string_width(text) / page_w + 1
        approx_h = lines_needed * 5.5 + 4

        # Barra lateral
        self.set_fill_color(*C_QUOTE_BAR)
        self.rect(self.l_margin, y_start, bar_w, approx_h, style="F")

        # Texto
        self.set_xy(self.l_margin + indent + padding, y_start + 2)
        self.multi_cell(page_w, 5.5, text, align="L")
        self.ln(2)
        self.set_font(self._font_body, "", SIZE_BODY)
        self.set_text_color(*C_TEXT)

    def draw_table_from_html(self, rows: list, headers: list = None):
        """Renderiza tabela com colunas proporcionais ao conteúdo máximo de cada coluna."""
        page_w = self.w - self.l_margin - self.r_margin
        all_content = ([headers] if headers else []) + rows
        n_cols = max((len(r) for r in all_content), default=1)
        if n_cols == 0:
            return

        # Calcula larguras proporcionais: mede o texto mais largo de cada coluna
        font_sz = 8.0
        self.set_font(self._font_body, "", font_sz)
        col_weights = []
        for col_idx in range(n_cols):
            max_w = 0.0
            for row in all_content:
                if col_idx < len(row):
                    txt = _clean_text(str(row[col_idx]))
                    max_w = max(max_w, self.get_string_width(txt))
            col_weights.append(max(max_w, 8.0))   # mínimo 8 mm

        total_w = sum(col_weights)
        col_widths = [page_w * w / total_w for w in col_weights]
        # Re-normaliza se ultrapassou a largura disponível
        if sum(col_widths) > page_w:
            scale = page_w / sum(col_widths)
            col_widths = [w * scale for w in col_widths]

        cell_h = 5.5

        def _fit_cell(text: str, max_w: float) -> str:
            """Trunca texto para caber em max_w mm usando largura real da fonte."""
            if self.get_string_width(text) <= max_w - 1:
                return text
            while text and self.get_string_width(text + "…") > max_w - 1:
                text = text[:-1]
            return (text + "…") if text else ""

        # Cabeçalho
        if headers:
            self.set_fill_color(*C_TABLE_HDR)
            self.set_draw_color(*C_HR)
            self.set_font(self._font_body, "B", font_sz)
            self.set_text_color(*C_TEXT)
            for i, h in enumerate(headers):
                cw = col_widths[i] if i < len(col_widths) else col_widths[-1]
                self.cell(cw, cell_h, _fit_cell(_clean_text(h), cw),
                          border=1, fill=True, align="C")
            self.ln()

        # Linhas de dados
        self.set_fill_color(*C_WHITE)
        self.set_font(self._font_body, "", font_sz)
        for row in rows:
            for i, cell_val in enumerate(row):
                cw = col_widths[i] if i < len(col_widths) else col_widths[-1]
                self.cell(cw, cell_h, _fit_cell(_clean_text(str(cell_val)), cw),
                          border=1, fill=False, align="L")
            self.ln()

        self.set_draw_color(0, 0, 0)
        self.set_text_color(*C_TEXT)
        self.ln(2)


# ──────────────────────────────────────────────── HTML PARSER ────────────────
from html.parser import HTMLParser

class _MarkdownHTMLWalker(HTMLParser):
    """
    Percorre o HTML gerado pelo Python-Markdown e chama os métodos
    do GithubMarkdownPDF para cada elemento.
    """

    def __init__(self, pdf: GithubMarkdownPDF):
        super().__init__(convert_charrefs=True)
        self.pdf = pdf

        # Estado
        self._tag_stack: list[str] = []
        self._text_buf: str = ""

        # Flags de contexto
        self._in_heading: int = 0       # 1-6 se dentro de <h1>…<h6>
        self._in_code_block: bool = False
        self._code_lang: str = ""
        self._in_blockquote: bool = False
        self._in_table: bool = False
        self._in_thead: bool = False
        self._in_tbody: bool = False
        self._in_tr: bool = False
        self._in_th: bool = False
        self._in_td: bool = False
        self._in_li: bool = False
        self._in_pre: bool = False
        self._in_bold: bool = False
        self._in_italic: bool = False
        self._in_code_inline: bool = False
        self._in_del: bool = False
        self._list_depth: int = 0
        self._ordered: list[bool] = []
        self._order_counters: list[int] = []
        self._skip: int = 0             # ignora tags de nível _skip

        # Buffers de tabela
        self._tbl_headers: list[str] = []
        self._tbl_rows: list[list[str]] = []
        self._tbl_row_buf: list[str] = []
        self._tbl_cell_buf: str = ""

        # Configura fonte padrão
        self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)
        self.pdf.set_text_color(*C_TEXT)
        self._line_h = 5.8

    # ─── helpers ───────────────────────────────────────────────────────────

    def _flush_text(self):
        """Escreve texto acumulado em _text_buf no PDF com estilo atual."""
        t = self._text_buf
        self._text_buf = ""
        if not t:
            return
        t = re.sub(r"\s+", " ", t)
        if self._in_blockquote or self._in_code_block or self._in_pre:
            return  # gerenciado por métodos dedicados
        if self._in_table:
            self._tbl_cell_buf += t
            return

        # Aplica ênfase
        style = ""
        if self._in_bold:
            style += "B"
        if self._in_italic:
            style += "I"
        if self._in_code_inline:
            self.pdf.set_font(self.pdf._font_mono, "", SIZE_SMALL)
            self.pdf.set_fill_color(*C_CODE_BG)
            self.pdf.set_text_color(*C_TEXT)
            # Padding visual inline
            self.pdf.cell(0.5, self._line_h, "")
            self.pdf.multi_cell(0, self._line_h, _clean_text(t), fill=True, new_x="LMARGIN", new_y="NEXT")
            self.pdf.set_font(self.pdf._font_body, style or "", SIZE_BODY)
            self.pdf.set_fill_color(*C_WHITE)
            return
        if self._in_del:
            style += "U"  # aproximação — fpdf não tem tachado nativo

        self.pdf.set_font(self.pdf._font_body, style, SIZE_BODY)
        self.pdf.multi_cell(0, self._line_h, _clean_text(t), align="L",
                            new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)

    def _current_tag(self) -> str:
        return self._tag_stack[-1] if self._tag_stack else ""

    # ─── HTMLParser callbacks ──────────────────────────────────────────────

    def handle_starttag(self, tag: str, attrs):
        if self._skip > 0:
            self._skip += 1
            return

        self._tag_stack.append(tag)
        attr = dict(attrs)

        # ── Ignorados ──────────────────────────────────────────────────────
        if tag in ("html", "body", "head", "meta", "style", "script", "img",
                   "input", "button", "form", "nav", "details", "summary",
                   "sup", "sub"):
            self._skip = 1
            return

        # ── Headings ───────────────────────────────────────────────────────
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            self.pdf.ln(4)
            level = int(tag[1])
            self._in_heading = level
            sz = H_SIZES.get(level, 10)
            color = C_MUTED if level >= 5 else C_TEXT
            self.pdf.set_font(self.pdf._font_body, "B", sz)
            self.pdf.set_text_color(*color)
            return

        # ── Parágrafo ──────────────────────────────────────────────────────
        if tag == "p":
            self._flush_text()
            if not self._in_li and not self._in_blockquote:
                self.pdf.ln(1.5)
            return

        # ── HR ─────────────────────────────────────────────────────────────
        if tag == "hr":
            self._flush_text()
            self.pdf.draw_hr()
            return

        # ── Listas ─────────────────────────────────────────────────────────
        if tag in ("ul", "ol"):
            self._list_depth += 1
            self._ordered.append(tag == "ol")
            self._order_counters.append(0)
            self.pdf.ln(1)
            return

        if tag == "li":
            self._flush_text()
            self._in_li = True
            indent = self._list_depth * 5
            self.pdf.set_x(self.pdf.l_margin + indent)
            is_ord = self._ordered[-1] if self._ordered else False
            if is_ord:
                self._order_counters[-1] += 1
                bullet = f"{self._order_counters[-1]}."
            else:
                bullet = "•"
            self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)
            self.pdf.cell(5, self._line_h, bullet)
            return

        # ── Blockquote ─────────────────────────────────────────────────────
        if tag == "blockquote":
            self._flush_text()
            self._in_blockquote = True
            self._text_buf = ""
            return

        # ── Tabela ─────────────────────────────────────────────────────────
        if tag == "table":
            self._flush_text()
            self._in_table = True
            self._tbl_headers = []
            self._tbl_rows = []
            return
        if tag == "thead":
            self._in_thead = True
            return
        if tag == "tbody":
            self._in_tbody = True
            return
        if tag == "tr":
            self._in_tr = True
            self._tbl_row_buf = []
            return
        if tag in ("th", "td"):
            self._tbl_cell_buf = ""
            self._in_th = (tag == "th")
            self._in_td = (tag == "td")
            return

        # ── Code ───────────────────────────────────────────────────────────
        if tag == "pre":
            self._flush_text()
            self._in_pre = True
            self._text_buf = ""
            return
        if tag == "code":
            if self._in_pre:
                self._in_code_block = True
                # Extrai lang de class="language-xxx" ou "hljs xxx"
                cls = attr.get("class", "")
                m = re.search(r"language-(\w+)", cls)
                if m:
                    self._code_lang = m.group(1)
                else:
                    self._code_lang = ""
                self._text_buf = ""
            else:
                self._in_code_inline = True
            return

        # ── Ênfases ────────────────────────────────────────────────────────
        if tag in ("b", "strong"):
            self._flush_text()
            self._in_bold = True
            return
        if tag in ("i", "em"):
            self._flush_text()
            self._in_italic = True
            return
        if tag in ("s", "del", "strike"):
            self._flush_text()
            self._in_del = True
            return

        # ── Links ──────────────────────────────────────────────────────────
        if tag == "a":
            self._flush_text()
            self.pdf.set_text_color(*C_LINK)
            return

        # ── Quebra de linha ────────────────────────────────────────────────
        if tag == "br":
            self._flush_text()
            self.pdf.ln(self._line_h)
            return

        # ── div/span: apenas continua o fluxo ──────────────────────────────
        # (div aparece em codehilite wrapping, ignoramos silenciosamente)

    def handle_endtag(self, tag: str):
        if self._skip > 0:
            self._skip -= 1
            return

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        # ── Headings ───────────────────────────────────────────────────────
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            heading_text = _clean_text(self._text_buf)
            self._text_buf = ""
            self._in_heading = 0

            self.pdf.multi_cell(0, H_SIZES[level] * 0.6,
                                heading_text, align="L",
                                new_x="LMARGIN", new_y="NEXT")
            # Borda inferior em H1 e H2 (estilo GitHub)
            if level <= 2:
                self.pdf.draw_hr(thin=True)
            else:
                self.pdf.ln(2)
            self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)
            self.pdf.set_text_color(*C_TEXT)
            return

        # ── Parágrafo ──────────────────────────────────────────────────────
        if tag == "p":
            if self._in_blockquote:
                return
            self._flush_text()
            self.pdf.ln(2)
            return

        # ── Listas ─────────────────────────────────────────────────────────
        if tag in ("ul", "ol"):
            self._list_depth = max(0, self._list_depth - 1)
            if self._ordered:
                self._ordered.pop()
            if self._order_counters:
                self._order_counters.pop()
            self.pdf.ln(1)
            return
        if tag == "li":
            self._flush_text()
            self._in_li = False
            self.pdf.set_x(self.pdf.l_margin)
            self.pdf.ln(1)
            return

        # ── Blockquote ─────────────────────────────────────────────────────
        if tag == "blockquote":
            bq_text = _clean_text(self._text_buf)
            self._text_buf = ""
            self._in_blockquote = False
            if bq_text:
                self.pdf.draw_blockquote(bq_text)
            return

        # ── Tabela ─────────────────────────────────────────────────────────
        if tag == "table":
            self._in_table = False
            self.pdf.draw_table_from_html(self._tbl_rows, self._tbl_headers or None)
            return
        if tag == "thead":
            self._in_thead = False
            return
        if tag == "tbody":
            self._in_tbody = False
            return
        if tag == "tr":
            self._in_tr = False
            if self._in_thead:
                self._tbl_headers = list(self._tbl_row_buf)
            else:
                self._tbl_rows.append(list(self._tbl_row_buf))
            self._tbl_row_buf = []
            return
        if tag in ("th", "td"):
            self._tbl_row_buf.append(self._tbl_cell_buf.strip())
            self._tbl_cell_buf = ""
            self._in_th = False
            self._in_td = False
            return

        # ── Code ───────────────────────────────────────────────────────────
        if tag == "pre":
            code_text = self._text_buf
            self._text_buf = ""
            self._in_pre = False
            self._in_code_block = False
            self.pdf.draw_code_block(code_text, self._code_lang)
            self._code_lang = ""
            return
        if tag == "code":
            if not self._in_pre:
                self._in_code_inline = False
                self.pdf.set_font(FONT_BODY, "", SIZE_BODY)
                self.pdf.set_text_color(*C_TEXT)
            return

        # ── Ênfases ────────────────────────────────────────────────────────
        if tag in ("b", "strong"):
            self._flush_text()
            self._in_bold = False
            self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)
            return
        if tag in ("i", "em"):
            self._flush_text()
            self._in_italic = False
            self.pdf.set_font(self.pdf._font_body, "", SIZE_BODY)
            return
        if tag in ("s", "del", "strike"):
            self._flush_text()
            self._in_del = False
            return

        # ── Links ──────────────────────────────────────────────────────────
        if tag == "a":
            self._flush_text()
            self.pdf.set_text_color(*C_TEXT)
            return

    def handle_data(self, data: str):
        if self._skip > 0:
            return

        # Dentro de code block: acumula raw
        if self._in_code_block or self._in_pre:
            self._text_buf += data
            return

        # Dentro de blockquote: acumula raw
        if self._in_blockquote:
            self._text_buf += data
            return

        # Dentro de heading: acumula raw
        if self._in_heading:
            self._text_buf += data
            return

        # Dentro de célula de tabela: acumula no buffer da célula
        if self._in_table and (self._in_th or self._in_td):
            self._tbl_cell_buf += data
            return

        # Resto: acumula e faz flush imediato para evitar truncamento
        self._text_buf += data
        if "\n" in data or len(self._text_buf) > 200:
            self._flush_text()


# ──────────────────────────────────────────────── UTILITÁRIOS ─────────────────
def _clean_text(text: str) -> str:
    """Remove chars problemáticos para FPDF e normaliza espaços."""
    if not text:
        return ""
    # Remove chars de controle exceto \n
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    # Remove emojis e símbolos fora do range Calibri/Consolas
    text = re.sub(r"[\U0001F000-\U0001FFFF]", "", text)   # emojis (misc pictographs)
    text = re.sub(r"[\U00020000-\U0010FFFF]", "", text)   # CJK ext / other
    text = re.sub(r"[\u2300-\u23FF]", "", text)           # misc technical symbols
    text = re.sub(r"[\u2600-\u27BF]", "", text)           # misc symbols & dingbats
    text = re.sub(r"[\uFE00-\uFE0F]", "", text)           # variation selectors
    # Substitui caracteres unicode que FPDF não consegue renderizar
    REPLACEMENTS = {
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2014": "--", "\u2013": "-",
        "\u2026": "...",
        "\u00b7": "-", "\u2022": "*",
        "\u2192": "->", "\u2190": "<-",
        "\u21d2": "=>", "\u2260": "!=",
        "\u2264": "<=", "\u2265": ">=",
        "\u00d7": "x", "\u00f7": "/",
        "\u2713": "v", "\u2714": "v",
        "\u274c": "x", "\u26a0": "!",
        "\u23f3": "~", "\u2705": "[OK]",
        "\u26a0\ufe0f": "[!]",
    }
    for k, v in REPLACEMENTS.items():
        text = text.replace(k, v)
    # Normaliza espaço múltiplo preservando \n intencional
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _md_to_html(md_path: Path) -> str:
    """Converte arquivo Markdown para HTML usando Python-Markdown."""
    content = md_path.read_text(encoding="utf-8", errors="replace")

    # Extensões disponíveis no Python-Markdown padrão
    extensions = [
        "tables",
        "fenced_code",
        "toc",
        "attr_list",
        "def_list",
        "footnotes",
        "abbr",
        "meta",
    ]
    try:
        md_obj = markdown.Markdown(
            extensions=extensions,
            extension_configs={
                "toc": {"baselevel": 1, "permalink": False},
            },
        )
    except Exception:
        # Fallback com extensões mínimas caso alguma falhe
        md_obj = markdown.Markdown(extensions=["tables", "fenced_code"])

    return md_obj.convert(content)


# ──────────────────────────────────────────────── GERAÇÃO PRINCIPAL ──────────
def generate_pdf(src_path: Path, dest_path: Path) -> None:
    """Pipeline completo: Markdown → HTML → PDF."""
    print(f"📄 Fonte : {src_path}")
    print(f"📁 Destino: {dest_path}")

    # 1. MD → HTML
    html_body = _md_to_html(src_path)

    # 2. Criar PDF
    pdf = GithubMarkdownPDF(src_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font(FONT_BODY, "", SIZE_BODY)
    pdf.set_text_color(*C_TEXT)

    # 3. Walk HTML → renderiza
    walker = _MarkdownHTMLWalker(pdf)
    walker.feed(html_body)
    walker.close()
    walker._flush_text()   # garante flush de qualquer texto residual
    pdf.set_font(pdf._font_body, "", SIZE_BODY)  # reset final

    # 4. Salvar
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        pdf.output(str(dest_path))
        size_kb = dest_path.stat().st_size / 1024
        print(f"✅ PDF gerado: {dest_path}  ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"❌ Erro ao salvar PDF: {e}", file=sys.stderr)
        sys.exit(1)


# ──────────────────────────────────────────────── ESTAMPAGEM DE RODAPÉ ──────────
def stamp_pdf_footer(src_path: Path, new_text: str, dest_path: Path = None) -> None:
    """
    Substitui o rodapé de um PDF existente usando PyMuPDF (fitz).

    Busca por 'Gerado em' (rodapé padrão deste script) ou qualquer texto
    anterior no rodapé e sobrepõe com o novo texto centralizado.

    Args:
        src_path:  PDF de entrada (arquivo existente)
        new_text:  Texto base do novo rodapé (número de página adicionado automaticamente)
        dest_path: PDF de saída (padrão: <nome>_assinado.pdf no mesmo diretório)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("\u274c PyMuPDF nao instalado. Execute: pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    if dest_path is None:
        dest_path = src_path.with_name(src_path.stem + "_assinado.pdf")

    print(f"\U0001f4c4 Fonte  : {src_path}")
    print(f"\U0001f4c1 Destino: {dest_path}")

    doc = fitz.open(str(src_path))
    total_pages = len(doc)
    pages_stamped = 0

    for page_num, page in enumerate(doc, 1):
        # Tenta localizar o rodapé por termos conhecidos
        hits = []
        for search_term in ("Gerado em", "Gerado pelo KARE", "Pagina ", "Pagina"):
            hits = page.search_for(search_term)
            if hits:
                break

        if not hits:
            continue

        for rect in hits:
            page_w = page.rect.width

            # Retângulo branco cobrindo toda a faixa do rodapé
            cover = fitz.Rect(0, rect.y0 - 3, page_w, rect.y1 + 4)
            page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

            # Monta novo texto com número de página
            footer_line = f"{new_text}  \u2022  Pag {page_num}/{total_pages}"

            # Centraliza o texto na página
            fontsize = 8.0
            try:
                text_w = fitz.get_text_length(footer_line, fontname="helv", fontsize=fontsize)
            except Exception:
                text_w = len(footer_line) * fontsize * 0.45  # fallback estimado
            x_center = max(10, (page_w - text_w) / 2)
            y_pos = rect.y1 + 1

            # Cor equivalente a C_MUTED (cinza suave)
            gray = (110 / 255, 119 / 255, 129 / 255)
            page.insert_text(
                (x_center, y_pos),
                footer_line,
                fontname="helv",
                fontsize=fontsize,
                color=gray,
                overlay=True,
            )
            pages_stamped += 1
            break  # uma ocorrência por página é suficiente

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dest_path), garbage=4, deflate=True)
    doc.close()

    if pages_stamped == 0:
        print("\u26a0\ufe0f  Nenhum rodapé 'Gerado em' encontrado nas páginas. PDF salvo sem alterações.")
    else:
        size_kb = dest_path.stat().st_size / 1024
        print(f"\u2705 Rodapé substituído em {pages_stamped}/{total_pages} página(s)")
        print(f"\u2705 PDF assinado: {dest_path}  ({size_kb:.1f} KB)")


# ──────────────────────────────────────────────── CLI ─────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="KARE — Exporta Markdown → PDF  |  Estampa rodapé em PDF existente"
    )
    parser.add_argument("--src",  required=True,
                        help="Arquivo de origem: .md (geração) ou .pdf (estampagem com --stamp)")
    parser.add_argument("--dest", default=None,
                        help="Arquivo .pdf de destino ou pasta de saída")
    parser.add_argument("--stamp", action="store_true",
                        help="Modo estampagem: substitui o rodapé de um PDF existente")
    parser.add_argument("--footer-text", default="Gerado pelo KARE KARE Agile Agent  \u2022  Maio/26",
                        help="Texto do novo rodapé (modo --stamp). Número de página adicionado automaticamente.")
    args = parser.parse_args()

    src_path = Path(args.src).resolve()
    if not src_path.exists():
        print(f"\u274c Arquivo não encontrado: {src_path}", file=sys.stderr)
        sys.exit(1)

    # ── Modo estampagem ──────────────────────────────────────────────────────
    if args.stamp:
        if src_path.suffix.lower() != ".pdf":
            print(f"\u274c --stamp requer um arquivo .pdf como --src (recebeu '{src_path.suffix}')",
                  file=sys.stderr)
            sys.exit(1)
        if args.dest:
            dest_path = Path(args.dest).resolve()
            if dest_path.suffix.lower() != ".pdf":
                dest_path = dest_path.with_suffix(".pdf")
        else:
            dest_path = None  # stamp_pdf_footer define o padrão (_assinado)
        stamp_pdf_footer(src_path, args.footer_text, dest_path)
        return

    # ── Modo geração MD → PDF ────────────────────────────────────────────────
    if src_path.suffix.lower() not in (".md", ".markdown", ".txt"):
        print(f"\u26a0\ufe0f  Extensão incomum '{src_path.suffix}'. Processando assim mesmo…")

    if args.dest:
        dest_path = Path(args.dest)
        if dest_path.is_dir() or str(args.dest).endswith(("/", "\\")):
            dest_path = dest_path / src_path.with_suffix(".pdf").name
        elif dest_path.suffix.lower() != ".pdf":
            dest_path = dest_path.with_suffix(".pdf")
    else:
        dest_path = src_path.with_suffix(".pdf")

    dest_path = dest_path.resolve()
    generate_pdf(src_path, dest_path)


if __name__ == "__main__":
    main()

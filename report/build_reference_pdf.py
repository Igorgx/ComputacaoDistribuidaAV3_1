from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "GUIA_DE_REFERENCIA.md"
OUTPUT = ROOT / "GUIA_DE_REFERENCIA.pdf"


def register_fonts() -> tuple[str, str, str]:
    arial = Path("C:/Windows/Fonts/arial.ttf")
    arial_bold = Path("C:/Windows/Fonts/arialbd.ttf")
    consolas = Path("C:/Windows/Fonts/consola.ttf")
    if arial.exists():
        pdfmetrics.registerFont(TTFont("Arial", str(arial)))
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(arial_bold)))
        if consolas.exists():
            pdfmetrics.registerFont(TTFont("Consolas", str(consolas)))
            pdfmetrics.registerFont(TTFont("Code", str(consolas)))
            return "Arial", "Arial-Bold", "Consolas"
        return "Arial", "Arial-Bold", "Courier"
    return "Helvetica", "Helvetica-Bold", "Courier"


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("`", "")
    )


def inline_code(text: str) -> str:
    return re.sub(r"`([^`]+)`", r"<font name='Code'>\1</font>", escape(text))


def make_styles():
    body_font, bold_font, code_font = register_fonts()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            fontName=bold_font,
            fontSize=22,
            leading=26,
            spaceAfter=14,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Custom",
            fontName=bold_font,
            fontSize=15,
            leading=19,
            spaceBefore=12,
            spaceAfter=7,
            textColor=colors.HexColor("#1f2937"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3Custom",
            fontName=bold_font,
            fontSize=12,
            leading=15,
            spaceBefore=9,
            spaceAfter=5,
            textColor=colors.HexColor("#374151"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            fontName=body_font,
            fontSize=9.6,
            leading=13,
            spaceAfter=6,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            fontName=body_font,
            fontSize=9.4,
            leading=12.5,
            leftIndent=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            fontName=code_font,
            fontSize=7.5,
            leading=9.2,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=4,
            spaceAfter=8,
            backColor=colors.HexColor("#f3f4f6"),
            borderColor=colors.HexColor("#d1d5db"),
            borderWidth=0.5,
            borderPadding=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            fontName=body_font,
            fontSize=8.5,
            leading=11,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHead",
            fontName=bold_font,
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
        )
    )
    pdfmetrics.registerFontFamily(
        body_font,
        normal=body_font,
        bold=bold_font,
    )
    return styles


def table_from(lines: list[str], styles):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return []
    data = []
    for row_index, row in enumerate(rows):
        style_name = "TableHead" if row_index == 0 else "TableCell"
        data.append([Paragraph(inline_code(cell), styles[style_name]) for cell in row])
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return [table, Spacer(1, 7)]


def build_story(markdown: str):
    styles = make_styles()
    story = []
    lines = markdown.splitlines()
    i = 0
    bullets: list[str] = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            story.append(
                ListFlowable(
                    [
                        ListItem(Paragraph(inline_code(item), styles["BulletCustom"]))
                        for item in bullets
                    ],
                    bulletType="bullet",
                    start="circle",
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 4))
            bullets = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_bullets()
            i += 1
            continue

        if stripped.startswith("```"):
            flush_bullets()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            story.append(Preformatted("\n".join(code_lines), styles["CodeBlock"], maxLineLength=110))
            i += 1
            continue

        if stripped.startswith("|"):
            flush_bullets()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.extend(table_from(table_lines, styles))
            continue

        if stripped.startswith("- "):
            bullets.append(stripped[2:])
            i += 1
            continue

        flush_bullets()
        if stripped.startswith("# "):
            story.append(Paragraph(inline_code(stripped[2:]), styles["TitleCustom"]))
        elif stripped.startswith("## "):
            if len(story) > 35 and stripped in {"## CRUD Completo com REST", "## Testes de Carga"}:
                story.append(PageBreak())
            story.append(Paragraph(inline_code(stripped[3:]), styles["H2Custom"]))
        elif stripped.startswith("### "):
            story.append(Paragraph(inline_code(stripped[4:]), styles["H3Custom"]))
        else:
            story.append(Paragraph(inline_code(stripped), styles["BodyCustom"]))
        i += 1

    flush_bullets()
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(2 * cm, 1.15 * cm, "Servico Fake de Streaming de Musicas - Guia de Referencia")
    canvas.drawRightString(A4[0] - 2 * cm, 1.15 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.55 * cm,
        leftMargin=1.55 * cm,
        topMargin=1.45 * cm,
        bottomMargin=1.7 * cm,
        title="Guia de Referencia do Sistema",
        author="Computacao Distribuida",
    )
    doc.build(build_story(markdown), onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()

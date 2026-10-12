"""Render the six-page editable report with external ReportLab authoring tools.

Install reportlab only in a separate document-tool environment, not the app runtime.
Run from any directory; the source remains docs/technical-report.md.
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]


def main():
    font_dir = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("ReportSans", str(font_dir / "segoeui.ttf")))
    pdfmetrics.registerFont(TTFont("ReportBold", str(font_dir / "segoeuib.ttf")))
    body = ParagraphStyle(
        "body",
        fontName="ReportSans",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#202824"),
        spaceAfter=10,
        alignment=TA_LEFT,
        splitLongWords=True,
    )
    heading = ParagraphStyle(
        "heading",
        parent=body,
        fontName="ReportBold",
        fontSize=17,
        leading=22,
        spaceBefore=10,
        spaceAfter=15,
    )
    title = ParagraphStyle(
        "title",
        parent=heading,
        fontSize=28,
        leading=32,
        spaceAfter=6,
    )
    output = ROOT / "output/pdf/taketwo-technical-report.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    source = (ROOT / "docs/technical-report.md").read_text(encoding="utf-8")
    story = []
    for block in re.split(r"\n\s*\n", source.strip()):
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif block.startswith("# "):
            story.append(Paragraph(escape(block[2:]), title))
        elif block.startswith("## "):
            story.append(Paragraph(escape(block[3:]), heading))
        else:
            story.append(Paragraph(escape(block.replace("\n", " ")), body))
    story.append(Spacer(1, 2))

    def frame(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D1D5CF"))
        canvas.line(42, height - 35, width - 42, height - 35)
        canvas.line(42, 35, width - 42, 35)
        canvas.setFont("ReportSans", 8)
        canvas.setFillColor(colors.HexColor("#4D5B54"))
        canvas.drawString(42, height - 27, "TAKETWO / SPEECH ANALYSIS WORKSPACE")
        canvas.drawString(42, 22, "TRACK C  |  TECHNICAL REPORT DRAFT  |  12 OCT 2026")
        canvas.drawRightString(width - 42, 22, str(doc.page))
        canvas.restoreState()

    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=42,
        rightMargin=42,
        topMargin=48,
        bottomMargin=46,
        title="TakeTwo - Speech analysis workspace: technical report draft",
        author="TakeTwo project",
    )
    document.build(story, onFirstPage=frame, onLaterPages=frame)
    print(output.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()

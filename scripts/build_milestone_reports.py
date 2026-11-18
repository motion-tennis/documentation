"""Build anonymous, self-contained M3/Mx PDFs from the reviewed report sources."""

from pathlib import Path
import re
import shutil
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, LongTable, TableStyle, KeepTogether


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "output" / "pdf" / "2026-11-18"
NAVY = colors.HexColor("#15334B")
TEAL = colors.HexColor("#087F8C")
GRAY = colors.HexColor("#566675")
PALE = colors.HexColor("#EEF4F7")
WIDTH = A4[0] - 36 * mm


def register_fonts():
    fonts = Path("C:/Windows/Fonts")
    for name, file in (("Body", "arial.ttf"), ("BodyBold", "arialbd.ttf"), ("BodyItalic", "ariali.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="BodyItalic", boldItalic="BodyBold")


def clean(value):
    return value.translate(str.maketrans({"–": "-", "—": "-", "‑": "-", "−": "-", "→": " -> ", "↔": " <-> ", "≤": "<=", "≥": ">="}))


def inline(value):
    value = clean(value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    pieces = re.split(r"(\*\*.*?\*\*|`[^`]+`)", value)
    result = []
    for piece in pieces:
        if piece.startswith("**") and piece.endswith("**"):
            result.append("<b>" + escape(piece[2:-2]) + "</b>")
        elif piece.startswith("`") and piece.endswith("`"):
            result.append('<font color="#175D72">' + escape(piece[1:-1]) + "</font>")
        else:
            result.append(escape(piece))
    return "".join(result)


def styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("ReportBody", fontName="Body", fontSize=9.2, leading=12.8, textColor=NAVY, spaceAfter=7),
        "h2": ParagraphStyle("Section", fontName="BodyBold", fontSize=16, leading=20, textColor=TEAL, spaceBefore=4, spaceAfter=13, keepWithNext=True),
        "h3": ParagraphStyle("Subsection", fontName="BodyBold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=7, keepWithNext=True),
        "cell": ParagraphStyle("Cell", fontName="Body", fontSize=8, leading=10.7, textColor=NAVY),
        "head": ParagraphStyle("HeadCell", fontName="BodyBold", fontSize=8, leading=10.6, textColor=colors.white),
        "small": ParagraphStyle("Small", fontName="Body", fontSize=8, leading=11, textColor=GRAY, spaceAfter=6),
        "cover": ParagraphStyle("Cover", fontName="BodyBold", fontSize=30, leading=36, textColor=NAVY, spaceAfter=18),
        "subtitle": ParagraphStyle("Subtitle", fontName="Body", fontSize=16, leading=22, textColor=TEAL, spaceAfter=22),
    }


def box(draw, x, y, w, h, lines, fill=PALE):
    draw.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=fill, strokeColor=TEAL, strokeWidth=0.8))
    for index, label in enumerate(lines):
        draw.add(String(x+w/2, y+h/2+(len(lines)-1)*5.2-index*10.4, label,
                        fontName="BodyBold" if index == 0 else "Body", fontSize=8, fillColor=NAVY, textAnchor="middle"))


def arrow(draw, x1, y1, x2, y2, label=None, dashed=False):
    import math
    line = Line(x1, y1, x2, y2, strokeColor=GRAY, strokeWidth=0.9)
    if dashed:
        line.strokeDashArray = [3, 3]
    draw.add(line)
    angle = math.atan2(y2-y1, x2-x1)
    size = 5
    points = [x2, y2, x2-size*math.cos(angle-.5), y2-size*math.sin(angle-.5),
              x2-size*math.cos(angle+.5), y2-size*math.sin(angle+.5)]
    draw.add(Polygon(points, fillColor=GRAY, strokeColor=GRAY))
    if label:
        draw.add(String((x1+x2)/2, (y1+y2)/2+6, label, fontName="Body", fontSize=7, textAnchor="middle", fillColor=GRAY))


def architecture(bench=False):
    d = Drawing(WIDTH, 290 if bench else 250)
    box(d, 2, 196, 105, 42, ["4 battery handhelds", "ESP32 / Zephyr", "MPU-6050 via I2C"])
    box(d, 2, 119, 105, 35, ["Electrical outputs", "LED / motor driver"])
    box(d, 158, 196, 130, 42, ["External AP + switch", "Wi-Fi to controllers", "Ethernet to Pi / PC"])
    box(d, 350, 196, 138, 42, ["Raspberry Pi 3 B", "Fusion / ordered physics", "Sole match calculation"])
    box(d, 158, 78, 330, 72, ["Windows laptop (one physical node)", "USB camera -> tracking -> pose to Pi", "C# committed-state service | Unity two-view client", "Separate asynchronous diagnostics"])
    box(d, 350, 12, 138, 32, ["Display", "Two team views / photons"])
    arrow(d, 107, 219, 158, 219, "UDP")
    arrow(d, 288, 219, 350, 219, "LAN")
    arrow(d, 54, 196, 54, 154)
    arrow(d, 223, 196, 223, 150, "Ethernet")
    arrow(d, 419, 196, 419, 150)
    d.add(String(430, 174, "Query / response", fontName="Body", fontSize=7, fillColor=GRAY))
    d.add(String(430, 164, "Update / commit", fontName="Body", fontSize=7, fillColor=GRAY))
    arrow(d, 419, 78, 419, 44)
    arrow(d, 350, 207, 288, 207)
    arrow(d, 158, 207, 107, 207, "feedback")
    if bench:
        box(d, 2, 12, 278, 48, ["Common-timebase acquisition", "t0 / tr markers + actual drive + two photodiodes", "Capture stops with Windows host; incomplete run"])
        arrow(d, 54, 119, 54, 60, dashed=True)
        arrow(d, 350, 28, 280, 28, dashed=True)
        d.add(String(2, 268, "APPLICATION NETWORK AND MEASUREMENT", fontName="BodyBold", fontSize=9, fillColor=TEAL))
    return d


def sequence():
    d = Drawing(WIDTH, 302)
    lanes = [(28, "Controller"), (144, "Tracking"), (258, "Pi physics"), (374, "State service"), (476, "Unity")]
    for x, name in lanes:
        d.add(String(x, 288, name, fontName="BodyBold", fontSize=8, fillColor=NAVY, textAnchor="middle"))
        d.add(Line(x, 12, x, 275, strokeColor=colors.HexColor("#CED9E1")))
    for y, source, target, text in [
        (258, 144, 258, "Continuous pose"), (227, 28, 258, "t0: identified controller_input"),
        (194, 258, 374, "ball_state_request"), (166, 374, 258, "ball_state_response"),
        (130, 258, 374, "state_update"), (102, 374, 258, "state_commit_result"),
        (70, 258, 28, "feedback_result -> tr -> eligible t1"),
        (40, 374, 476, "publication")]:
        arrow(d, source, y, target, y, text)
    d.add(String(28, 7, "Failure paths terminate explicitly; controller and display outputs are independent after commit.", fontName="Body", fontSize=8, fillColor=GRAY))
    return d


def table(rows, st):
    n = len(rows[0])
    if n == 7:
        ratios = [0.34] + [0.11]*6
    elif n == 5:
        if rows[0][0] == "Requirement":
            ratios = [.13, .40, .12, .10, .25]
        elif rows[0][0] == "Transaction":
            ratios = [.20, .17, .24, .26, .13]
        else:
            ratios = [.22, .15, .12, .14, .37]
    elif n == 4:
        ratios = [.18, .18, .39, .25] if rows[0][0] == "Link" else [.22, .33, .17, .28]
    elif n == 3:
        ratios = [.23, .42, .35]
    else:
        ratios = [.29, .71]
    total = sum(ratios)
    cells = [[Paragraph(inline(cell), st["head" if i == 0 else "cell"]) for cell in row] for i, row in enumerate(rows)]
    t = LongTable(cells, colWidths=[WIDTH*x/total for x in ratios], repeatRows=1, hAlign="LEFT", splitByRow=1, splitInRow=0)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]),
        ("LINEBELOW", (0,0), (-1,0), 1, TEAL),
        ("LINEBELOW", (0,1), (-1,-1), .3, colors.HexColor("#D5DFE6")),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t


def build(milestone, source, revision):
    st = styles()
    if milestone == "Mx":
        st["body"].fontSize = 9
        st["body"].leading = 12
        st["cell"].fontSize = 7.8
        st["cell"].leading = 10.2
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"DRS_{milestone}_MotionTennis.pdf"
    title = "System Design Report\nincluding Integration Tests" if milestone == "M3" else "Integration Test\nDebugging Concept"
    story = [Spacer(1, 32*mm), Paragraph("MOTION TENNIS / DISTRIBUTED REAL-TIME SYSTEM", st["small"]),
             Spacer(1, 8*mm), Paragraph(title.replace("\n", "<br/>"), st["cover"]),
             Paragraph("Milestone " + milestone + " | Gate 2 design package", st["subtitle"]),
             table([["Submission field", "Value"], ["Team", "Motion Tennis"], ["Milestone / revision", milestone + " / " + revision],
                    ["Report date", "18 November 2026"], ["Submission deadline", "19 November 2026, 23:59 Europe/Vienna"],
                    ["Responsible role", "Integration support" if milestone == "Mx" else "System design with integration support"],
                    ["Status", "Team acceptance confirmed on 18 November 2026; hardware validation pending." if milestone == "Mx" else "M3 and Mx accepted on 18 November 2026; Gate 2 complete."]], st),
             Spacer(1, 9*mm), Paragraph("Anonymous, self-contained report. Requirement identifiers follow the M2 baseline: F-01-F-21 and NF-01-NF-15. Tests and tool-readiness dates are specifications or proposals, not invented execution results. [NF-04, NF-05, NF-08, NF-10]", st["body"]),
             Paragraph("The team accepted M3 and Mx on 18 November 2026. Gate 2 is complete; hardware validation and course submission remain separate. [NF-05, NF-07]", st["body"])]
    lines = source.read_text(encoding="utf-8").splitlines()
    first = next(i for i,line in enumerate(lines) if line.startswith("## "))
    i = first
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("## "):
            if milestone == "M3" or i == first:
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 8))
            story.append(Paragraph(inline(line[3:]), st["h2"]))
            i += 1
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), st["h3"]))
            i += 1
        elif line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            story.append(sequence() if any("sequenceDiagram" in x for x in block) else architecture(milestone == "Mx"))
            story.append(Spacer(1, 8))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", c) for c in cells):
                    rows.append(cells)
                i += 1
            if len(rows) > 1:
                story.extend([table(rows, st), Spacer(1, 9)])
        elif re.match(r"\d+\. ", line):
            story.append(Paragraph(inline(line), st["body"]))
            i += 1
        else:
            chunk = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "```")):
                chunk.append(lines[i].strip()); i += 1
            story.append(Paragraph(inline(" ".join(chunk)), st["body"]))

    def furniture(canvas, doc):
        canvas.saveState()
        canvas.setTitle("Motion Tennis - " + milestone + " - " + title.replace("\n", " "))
        canvas.setAuthor("Motion Tennis - integration support")
        canvas.setSubject("Mx team acceptance confirmed; hardware validation pending" if milestone == "Mx" else "M3 and Mx accepted; Gate 2 complete")
        canvas.setFont("Body", 8)
        canvas.setFillColor(GRAY)
        if doc.page > 1:
            canvas.drawString(18*mm, A4[1]-13*mm, "MOTION TENNIS  /  " + milestone + "  /  " + revision)
            canvas.setStrokeColor(TEAL)
            canvas.line(18*mm, A4[1]-16*mm, A4[0]-18*mm, A4[1]-16*mm)
        canvas.drawString(18*mm, 12*mm, "18 November 2026 | " + ("Mx accepted; hardware validation pending" if milestone == "Mx" else "Gate 2 complete; hardware validation pending"))
        canvas.drawRightString(A4[0]-18*mm, 12*mm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=23*mm, bottomMargin=22*mm, title=title, author="Motion Tennis")
    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)
    shutil.copyfile(path, ROOT / "docs" / path.name)
    print(path)


if __name__ == "__main__":
    register_fonts()
    build("M3", ROOT / "docs/m3-system-design-integration-tests.md", "R7")
    build("Mx", ROOT / "docs/mx-integration-test-debugging-concept.md", "R3")


import io
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


def register_fonts():
    font_path = r"C:\Windows\Fonts\Nirmala.ttf"

    if os.path.exists(font_path):
        if "Nirmala" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("Nirmala", font_path))
        return "Nirmala"

    return "Helvetica"


def generate_pdf(data, language="English"):
    buffer = io.BytesIO()
    font_name = register_fonts()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="FormDecoder Report",
        author="FormDecoder"
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Brand",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=30,
        textColor=colors.HexColor("#635BFF"),
        alignment=TA_CENTER,
        spaceAfter=5 * mm
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_CENTER,
        spaceAfter=8 * mm
    ))

    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=19,
        textColor=colors.HexColor("#4338CA"),
        spaceBefore=7 * mm,
        spaceAfter=3 * mm
    ))

    styles.add(ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10,
        leading=16,
        spaceAfter=3 * mm,
        wordWrap="CJK"
    ))

    styles.add(ParagraphStyle(
        name="FieldTitle",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4338CA"),
        spaceAfter=2 * mm
    ))

    styles.add(ParagraphStyle(
        name="SmallNote",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#64748B")
    ))

    story = [
        Paragraph("FormDecoder", styles["Brand"]),
        Paragraph(
            "Your AI-powered form explanation report",
            styles["Subtitle"]
        ),
        Paragraph(
            escape(str(data.get("form_type", "Form Analysis"))),
            styles["Heading1"]
        ),
        Paragraph(
            "Language: " + escape(str(language)),
            styles["SmallNote"]
        ),
        Spacer(1, 5 * mm),
        Paragraph("Field Explanations", styles["Section"])
    ]

    fields = data.get("fields", [])

    if isinstance(fields, list) and fields:
        for index, field in enumerate(fields, start=1):
            if not isinstance(field, dict):
                continue

            name = escape(str(field.get("name", "Field")))
            explanation = escape(str(field.get("explanation", "")))

            content = [
                Paragraph(f"{index}. {name}", styles["FieldTitle"]),
                Paragraph(explanation or "No explanation provided.",
                          styles["BodyCustom"])
            ]

            example = field.get("example")
            if example:
                content.append(Paragraph(
                    "<b>Example:</b> " + escape(str(example)),
                    styles["BodyCustom"]
                ))

            story.append(KeepTogether(content))
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(Paragraph(
            "No fields were identified.",
            styles["BodyCustom"]
        ))

    story.append(Paragraph("Documents to Prepare", styles["Section"]))

    documents = data.get("documents_needed", [])

    if isinstance(documents, list) and documents:
        checklist_data = [
            [Paragraph(
                "&#9744;  " + escape(str(document)),
                styles["BodyCustom"]
            )]
            for document in documents
        ]

        table = Table(checklist_data, colWidths=[170 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1),
             colors.HexColor("#F3F4FF")),
            ("BOX", (0, 0), (-1, -1), 0.5,
             colors.HexColor("#D8D5FF")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3,
             colors.HexColor("#E0E7FF")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
    else:
        story.append(Paragraph(
            "No specific documents were identified. Confirm requirements "
            "with the relevant institution.",
            styles["BodyCustom"]
        ))

    warnings = data.get("warnings", [])

    if isinstance(warnings, list) and warnings:
        story.append(Paragraph(
            "Important Information", styles["Section"]
        ))

        for warning in warnings:
            story.append(Paragraph(
                "&#8226;  " + escape(str(warning)),
                styles["BodyCustom"]
            ))

    story.extend([
        Spacer(1, 8 * mm),
        Paragraph(
            "Important: AI-generated explanations may contain mistakes. "
            "Verify form instructions and document requirements with the "
            "relevant institution.",
            styles["SmallNote"]
        )
    ])

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawCentredString(
            A4[0] / 2,
            10 * mm,
            f"FormDecoder | Page {document.page}"
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    buffer.seek(0)
    return buffer.getvalue()

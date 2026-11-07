
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# EduAnalytics theme
SAGE = colors.HexColor("#52745A")
LIGHT_SAGE = colors.HexColor("#E9EEE6")
CREAM = colors.HexColor("#F7F7F2")
DARK = colors.HexColor("#252923")
MUTED = colors.HexColor("#777D73")


def safe_text(value):
    """Safely format values for PDF paragraphs."""
    return escape(str(value))


def generate_student_pdf(
    student,
    recommendations,
    risk_assessment,
    predicted_average=None
):
    """
    Generate a personalized student performance PDF.

    Returns:
        PDF document as bytes.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=SAGE,
        alignment=TA_CENTER,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=SAGE,
        spaceBefore=12,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=DARK
    ))

    styles.add(ParagraphStyle(
        name="SmallMuted",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MUTED,
        leading=11
    ))

    elements = []

    # Report heading
    elements.append(Paragraph(
        "EduAnalytics",
        styles["ReportTitle"]
    ))

    elements.append(Paragraph(
        "STUDENT PERFORMANCE REPORT",
        styles["Subtitle"]
    ))

    elements.append(HRFlowable(
        width="100%",
        thickness=1.2,
        color=SAGE,
        spaceAfter=15
    ))

    # Student information
    elements.append(Paragraph(
        "Student Information",
        styles["SectionHeading"]
    ))

    student_data = [
        ["Student Name", str(student["name"]),
         "Student ID", str(student["student_id"])],
        ["Class", str(student["class_name"]),
         "Gender", str(student["gender"])],
    ]

    student_table = Table(
        student_data,
        colWidths=[30*mm, 55*mm, 25*mm, 55*mm]
    )

    student_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_SAGE),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_SAGE),
        ("TEXTCOLOR", (0, 0), (0, -1), SAGE),
        ("TEXTCOLOR", (2, 0), (2, -1), SAGE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9DED5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(student_table)
    elements.append(Spacer(1, 12))

    # Academic overview
    elements.append(Paragraph(
        "Academic Overview",
        styles["SectionHeading"]
    ))

    overview_data = [
        ["Overall Average", "Attendance", "Daily Study Hours"],
        [
            f"{float(student['average_marks']):.1f}%",
            f"{float(student['attendance']):.1f}%",
            f"{float(student['study_hours']):.1f} hours"
        ]
    ]

    if predicted_average is not None:
        overview_data[0].append("Predicted Average")
        overview_data[1].append(f"{float(predicted_average):.1f}%")

    overview_table = Table(
        overview_data,
        colWidths=[42*mm] * len(overview_data[0])
    )

    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_SAGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), SAGE),
        ("TEXTCOLOR", (0, 1), (-1, 1), DARK),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9DED5")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(overview_table)

    # Subject-wise marks
    elements.append(Paragraph(
        "Subject-wise Performance",
        styles["SectionHeading"]
    ))

    subjects = [
        ("Mathematics", "math_marks"),
        ("Science", "science_marks"),
        ("English", "english_marks"),
        ("Social Science", "social_science_marks"),
        ("Computer", "computer_marks")
    ]

    subject_data = [["Subject", "Marks", "Performance"]]

    for subject_name, column in subjects:
        marks = float(student[column])

        if marks >= 70:
            performance = "Strong"
        elif marks >= 40:
            performance = "Needs Improvement"
        else:
            performance = "Below 40"

        subject_data.append([
            subject_name,
            f"{marks:.1f}/100",
            performance
        ])

    subject_table = Table(
        subject_data,
        colWidths=[65*mm, 40*mm, 65*mm]
    )

    subject_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SAGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9DED5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white, CREAM
        ]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(subject_table)

    # Risk assessment
    elements.append(Paragraph(
        "Student Risk Assessment",
        styles["SectionHeading"]
    ))

    risk_level = safe_text(risk_assessment["risk_level"])
    risk_score = risk_assessment["risk_score"]

    risk_text = (
        f"<b>Risk Level:</b> {risk_level}<br/>"
        f"<b>Risk Score:</b> {risk_score}"
    )

    elements.append(Paragraph(
        risk_text,
        styles["BodyTextCustom"]
    ))

    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        "<b>Identified Risk Factors:</b>",
        styles["BodyTextCustom"]
    ))

    for factor in risk_assessment["risk_factors"]:
        elements.append(Paragraph(
            f"&bull; {safe_text(factor)}",
            styles["BodyTextCustom"]
        ))

    # Personalized recommendations
    elements.append(Paragraph(
        "Personalized Recommendations",
        styles["SectionHeading"]
    ))

    if recommendations:
        for index, item in enumerate(recommendations, start=1):
            category = safe_text(item["category"])
            priority = safe_text(item["priority"])
            observation = safe_text(item["observation"])
            recommendation = safe_text(item["recommendation"])

            elements.append(Paragraph(
                f"<b>{index}. {category} ({priority} Priority)</b>",
                styles["BodyTextCustom"]
            ))

            elements.append(Paragraph(
                f"Observation: {observation}",
                styles["SmallMuted"]
            ))

            elements.append(Paragraph(
                f"Action: {recommendation}",
                styles["BodyTextCustom"]
            ))

            elements.append(Spacer(1, 7))
    else:
        elements.append(Paragraph(
            "No specific recommendations are currently available.",
            styles["BodyTextCustom"]
        ))

    # Disclaimer
    elements.append(Spacer(1, 15))

    elements.append(HRFlowable(
        width="100%",
        thickness=0.6,
        color=colors.HexColor("#D9DED5"),
        spaceAfter=8
    ))

    elements.append(Paragraph(
        "This report is generated by EduAnalytics. "
        "Performance predictions are estimates, while recommendations "
        "and risk classifications are based on initial rule-based "
        "thresholds. Results should support, not replace, teacher judgement.",
        styles["SmallMuted"]
    ))

    # Footer
    def add_footer(canvas, document):
        canvas.saveState()

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            18 * mm,
            10 * mm,
            "EduAnalytics | Student Performance Intelligence"
        )

        canvas.drawRightString(
            A4[0] - 18 * mm,
            10 * mm,
            f"Page {document.page}"
        )

        canvas.restoreState()

    doc.build(
        elements,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes

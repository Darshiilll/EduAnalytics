from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


# --------------------------------------------------
# EduAnalytics Theme
# --------------------------------------------------

PRIMARY = colors.HexColor("#5C7CFA")
DARK_BLUE = colors.HexColor("#4263D5")
NAVY = colors.HexColor("#243451")

LIGHT_BLUE = colors.HexColor("#E8F1FC")
LIGHT_LAVENDER = colors.HexColor("#EEF0FF")
PALE_BACKGROUND = colors.HexColor("#F4F6FC")

DARK = colors.HexColor("#26334D")
MUTED = colors.HexColor("#7C879C")
BORDER = colors.HexColor("#E3E8F2")

WHITE = colors.white

RISK_HIGH = colors.HexColor("#E36D70")
RISK_MODERATE = colors.HexColor("#E5A94B")
RISK_LOW = colors.HexColor("#39A879")


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def safe_text(value):
    """Escape dynamic text before inserting it into a ReportLab Paragraph."""
    return escape(str(value))


def get_risk_color(risk_level):
    level = str(risk_level).strip().lower()

    if level == "high":
        return RISK_HIGH
    elif level == "moderate":
        return RISK_MODERATE
    else:
        return RISK_LOW


def make_table(data, col_widths, header=True):
    """Create a consistently styled report table."""

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1 if header else 0,
    )

    commands = [
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]

    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_LAVENDER),
            ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])

        if len(data) > 1:
            commands.append(
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_BACKGROUND])
            )

    table.setStyle(TableStyle(commands))
    return table


# --------------------------------------------------
# Main PDF Generator
# --------------------------------------------------

def generate_student_pdf(
    student,
    recommendations,
    risk_assessment,
    predicted_average=None,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Student Performance Report",
        author="EduAnalytics",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Subtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=DARK_BLUE,
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=DARK,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=MUTED,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=DARK,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=NAVY,
        )
    )

    elements = []

    # --------------------------------------------------
    # Report Header
    # --------------------------------------------------

    elements.append(
        Paragraph("EduAnalytics", styles["ReportTitle"])
    )

    elements.append(
        Paragraph(
            "STUDENT PERFORMANCE REPORT",
            styles["Subtitle"],
        )
    )

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=PRIMARY,
            spaceAfter=14,
        )
    )

    # --------------------------------------------------
    # Student Information
    # --------------------------------------------------

    elements.append(
        Paragraph("Student Information", styles["SectionHeading"])
    )

    student_name = safe_text(student.get("name", "N/A"))
    student_id = safe_text(student.get("student_id", "N/A"))
    class_name = safe_text(student.get("class_name", "N/A"))
    gender = safe_text(student.get("gender", "N/A"))

    student_data = [
        [
            Paragraph("Student Name", styles["TableLabel"]),
            Paragraph(student_name, styles["TableCell"]),
            Paragraph("Student ID", styles["TableLabel"]),
            Paragraph(student_id, styles["TableCell"]),
        ],
        [
            Paragraph("Class", styles["TableLabel"]),
            Paragraph(class_name, styles["TableCell"]),
            Paragraph("Gender", styles["TableLabel"]),
            Paragraph(gender, styles["TableCell"]),
        ],
    ]

    elements.append(
        make_table(
            student_data,
            [30 * mm, 55 * mm, 25 * mm, 55 * mm],
            header=False,
        )
    )

    elements.append(Spacer(1, 8))

    # --------------------------------------------------
    # Academic Overview
    # --------------------------------------------------

    elements.append(
        Paragraph("Academic Overview", styles["SectionHeading"])
    )

    average_marks = float(student.get("average_marks", 0))
    attendance = float(student.get("attendance", 0))
    study_hours = float(student.get("study_hours", 0))

    overview_data = [
        [
            Paragraph("Overall Average", styles["TableLabel"]),
            Paragraph("Attendance", styles["TableLabel"]),
            Paragraph("Daily Study Hours", styles["TableLabel"]),
        ],
        [
            Paragraph(f"{average_marks:.2f}%", styles["TableCell"]),
            Paragraph(f"{attendance:.1f}%", styles["TableCell"]),
            Paragraph(f"{study_hours:.1f} hours", styles["TableCell"]),
        ],
    ]

    if predicted_average is not None:
        overview_data[0].append(
            Paragraph("Predicted Average", styles["TableLabel"])
        )
        overview_data[1].append(
            Paragraph(f"{float(predicted_average):.2f}%", styles["TableCell"])
        )

        overview_widths = [43.5 * mm] * 4
    else:
        overview_widths = [58 * mm] * 3

    elements.append(
        make_table(
            overview_data,
            overview_widths,
            header=True,
        )
    )

    elements.append(Spacer(1, 8))

    # --------------------------------------------------
    # Subject-wise Performance
    # --------------------------------------------------

    elements.append(
        Paragraph("Subject-wise Performance", styles["SectionHeading"])
    )

    subjects = [
        ("Mathematics", "math_marks"),
        ("Science", "science_marks"),
        ("English", "english_marks"),
        ("Social Science", "social_science_marks"),
        ("Computer", "computer_marks"),
    ]

    subject_data = [
        [
            Paragraph("Subject", styles["TableLabel"]),
            Paragraph("Marks", styles["TableLabel"]),
            Paragraph("Performance", styles["TableLabel"]),
        ]
    ]

    for subject_name, column in subjects:
        marks = float(student.get(column, 0))

        if marks >= 75:
            performance = "Excellent"
        elif marks >= 60:
            performance = "Good"
        elif marks >= 40:
            performance = "Needs Improvement"
        else:
            performance = "Critical"

        subject_data.append([
            Paragraph(safe_text(subject_name), styles["TableCell"]),
            Paragraph(f"{marks:.1f}%", styles["TableCell"]),
            Paragraph(performance, styles["TableCell"]),
        ])

    elements.append(
        make_table(
            subject_data,
            [65 * mm, 40 * mm, 65 * mm],
        )
    )

    elements.append(Spacer(1, 8))

    # --------------------------------------------------
    # Risk Assessment
    # --------------------------------------------------

    elements.append(
        Paragraph("Student Risk Assessment", styles["SectionHeading"])
    )

    risk_level = str(risk_assessment.get("risk_level", "Low"))
    risk_score = risk_assessment.get("risk_score", 0)
    risk_color = get_risk_color(risk_level)

    risk_summary = Table(
        [[
            Paragraph(
                f"<b>Risk Level:</b> {safe_text(risk_level)}",
                styles["BodyTextCustom"],
            ),
            Paragraph(
                f"<b>Risk Score:</b> {safe_text(risk_score)}",
                styles["BodyTextCustom"],
            ),
        ]],
        colWidths=[87 * mm, 87 * mm],
    )

    risk_summary.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), LIGHT_LAVENDER),
            ("BACKGROUND", (1, 0), (1, 0), PALE_BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TEXTCOLOR", (0, 0), (0, 0), risk_color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ])
    )

    elements.append(risk_summary)
    elements.append(Spacer(1, 8))

    risk_factors = risk_assessment.get("risk_factors", [])

    if risk_factors:
        elements.append(
            Paragraph("Identified Risk Factors", styles["BodyTextCustom"])
        )
        elements.append(Spacer(1, 4))

        for factor in risk_factors:
            elements.append(
                Paragraph(
                    f"- {safe_text(factor)}",
                    styles["SmallMuted"],
                )
            )
            elements.append(Spacer(1, 3))
    else:
        elements.append(
            Paragraph(
                "No significant risk factors were identified.",
                styles["SmallMuted"],
            )
        )

    elements.append(Spacer(1, 6))

    # --------------------------------------------------
    # Personalized Recommendations
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "Personalized Recommendations",
            styles["SectionHeading"],
        )
    )

    if recommendations:
        for index, recommendation in enumerate(recommendations, start=1):
            category = safe_text(
                recommendation.get("category", "General")
            )
            priority = safe_text(
                recommendation.get("priority", "Low")
            )
            observation = safe_text(
                recommendation.get("observation", "")
            )
            action = safe_text(
                recommendation.get("recommendation", "")
            )

            elements.append(
                Paragraph(
                    f"<b>{index}. {category}</b> "
                    f"<font color='#7C879C'>({priority} Priority)</font>",
                    styles["BodyTextCustom"],
                )
            )

            if observation:
                elements.append(
                    Paragraph(
                        f"<b>Observation:</b> {observation}",
                        styles["SmallMuted"],
                    )
                )

            if action:
                elements.append(
                    Paragraph(
                        f"<b>Recommended Action:</b> {action}",
                        styles["BodyTextCustom"],
                    )
                )

            elements.append(Spacer(1, 8))

    else:
        elements.append(
            Paragraph(
                "No personalized recommendations are available.",
                styles["SmallMuted"],
            )
        )

    # --------------------------------------------------
    # Disclaimer
    # --------------------------------------------------

    elements.append(Spacer(1, 8))

    disclaimer_data = [[
        Paragraph(
            "<b>Disclaimer</b><br/>"
            "This report is generated using the student data available "
            "in EduAnalytics. Risk classifications and predictions are "
            "indicative assessments intended to support educational "
            "decision-making. They should not replace professional "
            "academic evaluation.",
            styles["SmallMuted"],
        )
    ]]

    disclaimer_table = Table(
        disclaimer_data,
        colWidths=[174 * mm],
    )

    disclaimer_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PALE_BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ])
    )

    elements.append(disclaimer_table)

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------

    def add_footer(canvas, document):
        canvas.saveState()

        page_width, _ = A4

        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)
        canvas.line(
            18 * mm,
            13 * mm,
            page_width - 18 * mm,
            13 * mm,
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            18 * mm,
            8 * mm,
            "EduAnalytics | Student Performance Intelligence",
        )

        canvas.drawRightString(
            page_width - 18 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        elements,
        onFirstPage=add_footer,
        onLaterPages=add_footer,
    )

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
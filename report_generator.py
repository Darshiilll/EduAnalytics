
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
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
    KeepTogether,
)


# ==========================================================
# EDUANALYTICS - ACADEMIC REPORT DESIGN
# ==========================================================

NAVY = colors.HexColor("#243451")
BLUE = colors.HexColor("#526FCB")
LIGHT_BLUE = colors.HexColor("#EDF2FC")
LAVENDER = colors.HexColor("#F1F2FA")

DARK = colors.HexColor("#303B50")
MUTED = colors.HexColor("#778197")
BORDER = colors.HexColor("#DDE3ED")
BACKGROUND = colors.HexColor("#F7F8FB")
WHITE = colors.white

RISK_HIGH = colors.HexColor("#C75C63")
RISK_MODERATE = colors.HexColor("#C18A37")
RISK_LOW = colors.HexColor("#37866B")

PAGE_WIDTH, PAGE_HEIGHT = A4

SUBJECTS = [
    ("Mathematics", "math_marks"),
    ("Science", "science_marks"),
    ("English", "english_marks"),
    ("Social Science", "social_science_marks"),
    ("Computer", "computer_marks"),
]


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def safe_text(value):
    """Safely format dynamic values for ReportLab paragraphs."""
    if value is None:
        return "N/A"

    return escape(str(value))


def number_value(value, default=0):
    """Convert a value to a number without breaking PDF generation."""
    try:
        if value is None:
            return default

        return float(value)
    except (ValueError, TypeError):
        return default


def get_risk_color(risk_level):
    level = str(risk_level).strip().lower()

    if level == "high":
        return RISK_HIGH

    if level == "moderate":
        return RISK_MODERATE

    return RISK_LOW


def get_performance_label(marks):
    if marks >= 75:
        return "Strong"

    if marks >= 60:
        return "Satisfactory"

    if marks >= 40:
        return "Below target"

    return "Needs attention"


def make_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Brand",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=BLUE,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="ReportHeading",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=NAVY,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="ReportSubheading",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=MUTED,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="Section",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=NAVY,
        spaceBefore=13,
        spaceAfter=7,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="BodyCustom",
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=DARK,
    ))

    styles.add(ParagraphStyle(
        name="SmallCustom",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=NAVY,
    ))

    styles.add(ParagraphStyle(
        name="TableBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=DARK,
    ))

    styles.add(ParagraphStyle(
        name="TableBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=NAVY,
    ))

    styles.add(ParagraphStyle(
        name="RecommendationTitle",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=NAVY,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="RecommendationBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=13,
        textColor=DARK,
    ))

    styles.add(ParagraphStyle(
        name="RightSmall",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
        alignment=TA_RIGHT,
    ))

    return styles


def make_table(data, widths, header=True, row_padding=7):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT",
    )

    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), row_padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), row_padding),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDER),
    ]

    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, BLUE),
        ])

        if len(data) > 1:
            commands.append(
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BACKGROUND])
            )

    else:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, -1), WHITE),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ])

    table.setStyle(TableStyle(commands))
    return table


def section_heading(title, styles):
    return Paragraph(safe_text(title), styles["Section"])


def make_score_bar(score, width=45 * mm):
    """A restrained visual indicator for a score out of 100."""
    score = max(0, min(100, number_value(score)))

    filled_width = width * score / 100
    remaining_width = width - filled_width

    bar = Table(
        [["", ""]],
        colWidths=[filled_width, remaining_width],
        rowHeights=[4],
    )

    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BACKGROUND", (1, 0), (1, 0), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0, WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    return bar


# ==========================================================
# MAIN PDF GENERATOR
# ==========================================================

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
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=22 * mm,
        bottomMargin=21 * mm,
        title="Student Academic Performance Report",
        author="EduAnalytics",
    )

    styles = make_styles()
    elements = []

    # ------------------------------------------------------
    # Extract student information
    # ------------------------------------------------------

    student_name = safe_text(student.get("name", "N/A"))
    student_id = safe_text(student.get("student_id", "N/A"))
    class_name = safe_text(student.get("class_name", "N/A"))
    gender = safe_text(student.get("gender", "N/A"))

    average_marks = number_value(student.get("average_marks", 0))
    attendance = number_value(student.get("attendance", 0))
    study_hours = number_value(student.get("study_hours", 0))

    risk_level = str(risk_assessment.get("risk_level", "Low"))
    risk_score = risk_assessment.get("risk_score", 0)
    risk_color = get_risk_color(risk_level)

    report_date = datetime.now().strftime("%d %B %Y")

    # ------------------------------------------------------
    # Report heading
    # ------------------------------------------------------

    elements.append(Paragraph("EduAnalytics", styles["Brand"]))

    elements.append(Spacer(1, 5))

    elements.append(
        Paragraph(
            "Student Performance Report",
            styles["ReportHeading"],
        )
    )

    elements.append(
        Paragraph(
            "Academic record and individual performance review",
            styles["ReportSubheading"],
        )
    )

    header_details = Table(
        [[
            Paragraph(
                f"<b>STUDENT ID</b><br/>{student_id}",
                styles["TableBody"],
            ),
            Paragraph(
                f"<b>CLASS</b><br/>{class_name}",
                styles["TableBody"],
            ),
            Paragraph(
                f"<b>REPORT DATE</b><br/>{report_date}",
                styles["TableBody"],
            ),
        ]],
        colWidths=[57 * mm, 57 * mm, 57 * mm],
    )

    header_details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BACKGROUND),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(header_details)

    # ------------------------------------------------------
    # Student profile
    # ------------------------------------------------------

    elements.append(section_heading("Student Details", styles))

    profile_data = [
        [
            Paragraph("Student name", styles["TableHeader"]),
            Paragraph("Class", styles["TableHeader"]),
            Paragraph("Gender", styles["TableHeader"]),
        ],
        [
            Paragraph(student_name, styles["TableBody"]),
            Paragraph(class_name, styles["TableBody"]),
            Paragraph(gender, styles["TableBody"]),
        ],
    ]

    elements.append(
        make_table(
            profile_data,
            [63 * mm, 54 * mm, 54 * mm],
            row_padding=8,
        )
    )

    # ------------------------------------------------------
    # Academic summary
    # ------------------------------------------------------

    elements.append(section_heading("Academic Summary", styles))

    overview_data = [
        [
            Paragraph("OVERALL AVERAGE", styles["TableHeader"]),
            Paragraph("ATTENDANCE", styles["TableHeader"]),
            Paragraph("DAILY STUDY", styles["TableHeader"]),
        ],
        [
            Paragraph(
                f"<b>{average_marks:.1f}%</b>",
                styles["TableBold"],
            ),
            Paragraph(
                f"<b>{attendance:.1f}%</b>",
                styles["TableBold"],
            ),
            Paragraph(
                f"<b>{study_hours:.1f} hours</b>",
                styles["TableBold"],
            ),
        ],
    ]

    if predicted_average is not None:
        overview_data[0].append(
            Paragraph("PREDICTED AVERAGE", styles["TableHeader"])
        )
        overview_data[1].append(
            Paragraph(
                f"<b>{number_value(predicted_average):.1f}%</b>",
                styles["TableBold"],
            )
        )

        overview_widths = [43 * mm] * 4
    else:
        overview_widths = [57 * mm] * 3

    elements.append(
        make_table(
            overview_data,
            overview_widths,
            row_padding=9,
        )
    )

    # ------------------------------------------------------
    # Subject performance
    # ------------------------------------------------------

    elements.append(section_heading("Subject-wise Results", styles))

    subject_data = [[
        Paragraph("Subject", styles["TableHeader"]),
        Paragraph("Marks", styles["TableHeader"]),
        Paragraph("Assessment", styles["TableHeader"]),
        Paragraph("Score", styles["TableHeader"]),
    ]]

    for subject_name, column in SUBJECTS:
        marks = number_value(student.get(column, 0))
        performance = get_performance_label(marks)

        subject_data.append([
            Paragraph(safe_text(subject_name), styles["TableBody"]),
            Paragraph(f"{marks:.1f}%", styles["TableBold"]),
            Paragraph(performance, styles["TableBody"]),
            make_score_bar(marks, width=40 * mm),
        ])

    elements.append(
        make_table(
            subject_data,
            [42 * mm, 25 * mm, 43 * mm, 44 * mm],
            row_padding=8,
        )
    )

    # ------------------------------------------------------
    # Performance observation
    # ------------------------------------------------------

    marks_list = [
        number_value(student.get(column, 0))
        for _, column in SUBJECTS
    ]

    strongest_score = max(marks_list) if marks_list else 0
    weakest_score = min(marks_list) if marks_list else 0

    strongest_subject = next(
        (
            name for name, column in SUBJECTS
            if number_value(student.get(column, 0)) == strongest_score
        ),
        "N/A",
    )

    weakest_subject = next(
        (
            name for name, column in SUBJECTS
            if number_value(student.get(column, 0)) == weakest_score
        ),
        "N/A",
    )

    elements.append(section_heading("Performance Observations", styles))

    observation_text = (
        f"The highest subject score is in <b>{safe_text(strongest_subject)}</b> "
        f"at {strongest_score:.1f}%. "
        f"The lowest subject score is in <b>{safe_text(weakest_subject)}</b> "
        f"at {weakest_score:.1f}%. "
    )

    if attendance >= 85:
        observation_text += (
            "Attendance is currently strong. Maintaining this consistency "
            "will support continued academic progress."
        )
    elif attendance >= 70:
        observation_text += (
            "Attendance is moderate. Improving regularity may help provide "
            "more consistent learning time."
        )
    else:
        observation_text += (
            "Attendance is below the preferred level. Regular attendance "
            "should be a priority."
        )

    observation_box = Table(
        [[Paragraph(observation_text, styles["BodyCustom"])]],
        colWidths=[171 * mm],
    )

    observation_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BACKGROUND),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LINEBEFORE", (0, 0), (0, 0), 2.5, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(observation_box)

    # ------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------

    elements.append(section_heading("Academic Risk Assessment", styles))

    risk_summary = Table(
        [[
            Paragraph(
                f"<b>Risk classification</b><br/>"
                f"<font color='{risk_color.hexval()}' size='12'>"
                f"<b>{safe_text(risk_level)}</b></font>",
                styles["BodyCustom"],
            ),
            Paragraph(
                f"<b>Risk score</b><br/>"
                f"<font size='12'><b>{safe_text(risk_score)}</b></font>",
                styles["BodyCustom"],
            ),
        ]],
        colWidths=[85.5 * mm, 85.5 * mm],
    )

    risk_summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BACKGROUND),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LINEBEFORE", (0, 0), (0, 0), 2.5, risk_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(risk_summary)

    risk_factors = risk_assessment.get("risk_factors", [])

    if risk_factors:
        elements.append(Spacer(1, 7))

        elements.append(
            Paragraph(
                "<b>Factors requiring attention</b>",
                styles["BodyCustom"],
            )
        )

        for factor in risk_factors:
            elements.append(
                Paragraph(
                    f"•  {safe_text(factor)}",
                    styles["SmallCustom"],
                )
            )
    else:
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(
                "No significant risk factors were recorded in this assessment.",
                styles["SmallCustom"],
            )
        )

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    elements.append(section_heading("Recommendations", styles))

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

            recommendation_content = []

            recommendation_content.append(
                Paragraph(
                    f"{index:02d}  {category} "
                    f"<font color='#778197'>| {priority} priority</font>",
                    styles["RecommendationTitle"],
                )
            )

            if observation and observation != "N/A":
                recommendation_content.append(
                    Paragraph(
                        f"<b>Observation:</b> {observation}",
                        styles["RecommendationBody"],
                    )
                )

            if action and action != "N/A":
                recommendation_content.append(
                    Paragraph(
                        f"<b>Suggested action:</b> {action}",
                        styles["RecommendationBody"],
                    )
                )

            recommendation_content.append(Spacer(1, 5))

            elements.append(
                KeepTogether(recommendation_content)
            )

            elements.append(
                HRFlowable(
                    width="100%",
                    thickness=0.4,
                    color=BORDER,
                    spaceBefore=2,
                    spaceAfter=7,
                )
            )

    else:
        elements.append(
            Paragraph(
                "No individual recommendations are available for this report.",
                styles["SmallCustom"],
            )
        )

    # ------------------------------------------------------
    # Report note
    # ------------------------------------------------------

    elements.append(Spacer(1, 8))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=0.7,
            color=BORDER,
            spaceBefore=3,
            spaceAfter=8,
        )
    )

    elements.append(
        Paragraph(
            "<b>Report note</b>",
            styles["BodyCustom"],
        )
    )

    elements.append(
        Paragraph(
            "This report is based on the student information available in "
            "EduAnalytics at the time of generation. Predicted results and "
            "risk classifications are indicative and should be considered "
            "alongside teacher observations and academic records.",
            styles["SmallCustom"],
        )
    )

    # ------------------------------------------------------
    # Header and footer
    # ------------------------------------------------------

    def draw_page(canvas, document):
        canvas.saveState()

        page_width, page_height = A4

        # Top brand line
        canvas.setFillColor(BLUE)
        canvas.rect(
            0,
            page_height - 3 * mm,
            page_width,
            3 * mm,
            fill=1,
            stroke=0,
        )

        # Footer divider
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)

        canvas.line(
            19 * mm,
            14 * mm,
            page_width - 19 * mm,
            14 * mm,
        )

        # Footer text
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            19 * mm,
            9 * mm,
            "EduAnalytics  |  Student Academic Record",
        )

        canvas.drawRightString(
            page_width - 19 * mm,
            9 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        elements,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data

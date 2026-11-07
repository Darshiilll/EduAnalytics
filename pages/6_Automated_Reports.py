
import streamlit as st
import joblib
import pandas as pd
import html

from pathlib import Path

from data_utils import load_data, apply_styles, show_sidebar
from recommendation_engine import generate_recommendations
from risk_engine import assess_student_risk
from report_generator import generate_student_pdf

st.set_page_config(
    page_title="Automated Reports | EduAnalytics",
    page_icon="E",
    layout="wide",
)

apply_styles()
show_sidebar()

st.markdown("""
<style>
.stApp { background:#F4F6FC; color:#243451; }
h1,h2,h3 { color:#243451 !important; font-family:Manrope,sans-serif; }
.page-eyebrow {
    color:#5C7CFA; font-size:.68rem; font-weight:800;
    letter-spacing:1.5px; margin-bottom:7px;
}
.page-subtitle { color:#8792A5; font-size:.86rem; margin-bottom:18px; }
.panel-title { color:#243451; font-size:1rem; font-weight:750; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:14px; box-shadow:0 3px 12px rgba(36,52,81,.035);
}
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:13px; padding:15px;
}
[data-testid="stMetricLabel"] { color:#73819A; }
[data-testid="stMetricValue"] { color:#243451; font-family:Manrope,sans-serif; }
.report-item {
    display:flex; align-items:center; gap:10px;
    padding:9px 0; border-bottom:1px solid #EDF0F5;
    color:#52617A; font-size:.8rem;
}
.report-check {
    width:21px; height:21px; border-radius:7px;
    display:flex; align-items:center; justify-content:center;
    color:#328B69; background:#E5F6EE; font-weight:800;
}
.risk-label {
    display:inline-block; border-radius:20px;
    padding:5px 10px; font-size:.68rem; font-weight:750;
}
.risk-high { color:#C34E5B; background:#FCEBED; }
.risk-moderate { color:#A97822; background:#FFF4DD; }
.risk-low { color:#328B69; background:#E5F6EE; }
.stButton button,.stDownloadButton button {
    background:#5C7CFA; color:white; border:1px solid #5C7CFA;
    border-radius:9px; font-weight:650;
}
.stButton button:hover,.stDownloadButton button:hover {
    background:#4969E6; color:white; border-color:#4969E6;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">REPORTS / DOCUMENT GENERATION</div>',
    unsafe_allow_html=True,
)
st.title("Automated Student Reports")
st.markdown(
    '<div class="page-subtitle">Create detailed student reports '
    'combining academic performance, risk assessment and '
    'personalized recommendations.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# STUDENT SELECTION
# ------------------------------------------------------------

with st.container(border=True):
    st.markdown(
        '<div class="panel-title">Select a Student</div>',
        unsafe_allow_html=True,
    )

    student_options = {
        f"{row['name']} ({row['student_id']})": row["student_id"]
        for _, row in df.iterrows()
    }

    selected_student = st.selectbox(
        "Choose a student for the report",
        list(student_options.keys()),
    )

student_id = student_options[selected_student]

student = df[
    df["student_id"] == student_id
].iloc[0]


# ------------------------------------------------------------
# STUDENT OVERVIEW
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">REPORT PREVIEW</div>',
    unsafe_allow_html=True,
)
st.subheader("Student Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Student", student["name"])
c2.metric("Class", student["class_name"])
c3.metric("Average Marks", f"{student['average_marks']:.1f}%")
c4.metric("Attendance", f"{student['attendance']:.1f}%")


# ------------------------------------------------------------
# GENERATE RECOMMENDATIONS AND RISK
# ------------------------------------------------------------

recommendations = generate_recommendations(student)
risk_assessment = assess_student_risk(student)


# ------------------------------------------------------------
# OPTIONAL MODEL PREDICTION
# ------------------------------------------------------------

predicted_average = None

project_root = Path(__file__).resolve().parent.parent

model_path = (
    project_root
    / "models"
    / "student_performance_model.joblib"
)

if model_path.exists():
    try:
        model = joblib.load(model_path)

        prediction_input = pd.DataFrame(
            [{
                "attendance": float(student["attendance"]),
                "study_hours": float(student["study_hours"]),
            }]
        )

        predicted_average = float(
            model.predict(prediction_input)[0]
        )

        predicted_average = max(
            0,
            min(100, predicted_average),
        )

    except Exception:
        st.info(
            "Performance prediction is unavailable. "
            "The report can still be generated without it."
        )
else:
    st.info(
        "Prediction model not found. "
        "The report will be generated without predicted marks."
    )


# ------------------------------------------------------------
# REPORT CONTENTS AND PREDICTION
# ------------------------------------------------------------

left, right = st.columns([1.2, 1], gap="medium")

with left:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Report Contents</div>',
            unsafe_allow_html=True,
        )
        st.caption("The PDF report will contain the following sections.")

        report_items = [
            "Student information",
            "Academic overview",
            "Subject-wise performance",
            "Student risk assessment",
            "Identified risk factors",
            "Personalized recommendations",
        ]

        if predicted_average is not None:
            report_items.append("Estimated performance prediction")

        for item in report_items:
            st.markdown(
                f"""
                <div class="report-item">
                    <span class="report-check">✓</span>
                    <span>{html.escape(item)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

with right:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Performance Estimate</div>',
            unsafe_allow_html=True,
        )

        if predicted_average is not None:
            st.metric(
                "Predicted Average",
                f"{predicted_average:.1f}%",
            )
            st.progress(predicted_average / 100)
            st.caption(
                "Estimated by the trained regression model using "
                "attendance and study hours."
            )
        else:
            st.info(
                "No prediction is available. The PDF can still be "
                "generated with the remaining report sections."
            )


# ------------------------------------------------------------
# RISK PREVIEW
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">STUDENT SUPPORT INDICATORS</div>',
    unsafe_allow_html=True,
)
st.subheader("Risk Assessment Preview")

risk_level = risk_assessment["risk_level"]

risk_classes = {
    "High": "risk-high",
    "Moderate": "risk-moderate",
    "Low": "risk-low",
}

with st.container(border=True):
    a, b, c = st.columns([1, 1, 2])

    a.metric("Risk Score", risk_assessment["risk_score"])

    with b:
        st.markdown("**Risk Classification**")
        st.markdown(
            f'<span class="risk-label {risk_classes[risk_level]}">'
            f'{risk_level} Risk</span>',
            unsafe_allow_html=True,
        )

    with c:
        st.markdown("**Identified Risk Factors**")
        if risk_assessment["risk_factors"]:
            for factor in risk_assessment["risk_factors"]:
                st.markdown(
                    f'<div style="color:#73819A;font-size:.76rem;">'
                    f'• {html.escape(str(factor))}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No risk factors were identified.")


# ------------------------------------------------------------
# RECOMMENDATION PREVIEW
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">PERSONALIZED GUIDANCE</div>',
    unsafe_allow_html=True,
)
st.subheader("Recommendation Preview")

if recommendations:
    preview_items = recommendations[:3]

    for item in preview_items:
        with st.container(border=True):
            st.markdown(f"**{item['category']}**")
            st.caption(
                f"{item['priority']} priority · {item['observation']}"
            )
            st.write(item["recommendation"])

    if len(recommendations) > 3:
        st.caption(
            f"The PDF will also include {len(recommendations) - 3} "
            "additional recommendations."
        )
else:
    st.success("No specific recommendations are currently available.")


# ------------------------------------------------------------
# PDF GENERATION
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">EXPORT / PDF DOCUMENT</div>',
    unsafe_allow_html=True,
)
st.subheader("Generate Student Report")

with st.container(border=True):
    st.markdown("**Ready to generate?**")
    st.caption(
        "Create a PDF containing the selected student's academic profile, "
        "subject results, risk assessment and personalized recommendations."
    )

    if st.button(
        "Generate Student Report",
        type="primary",
        use_container_width=True,
    ):
        try:
            pdf_data = generate_student_pdf(
                student=student,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                predicted_average=predicted_average,
            )

            st.session_state["student_pdf"] = pdf_data
            st.session_state["student_pdf_id"] = str(student_id)

            st.success("Student report generated successfully.")

        except Exception as error:
            st.error(f"Unable to generate report: {error}")


# ------------------------------------------------------------
# DOWNLOAD BUTTON
# ------------------------------------------------------------

if (
    "student_pdf" in st.session_state
    and st.session_state.get("student_pdf_id") == str(student_id)
):
    safe_student_id = "".join(
        character
        for character in str(student_id)
        if character.isalnum() or character in ("-", "_")
    )

    st.download_button(
        label="Download PDF Report",
        data=st.session_state["student_pdf"],
        file_name=f"EduAnalytics_Report_{safe_student_id}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


st.caption(
    "Reports contain estimated predictions and rule-based "
    "recommendations. They should support teacher judgement."
)

st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Automated Academic Reporting
</div>
""", unsafe_allow_html=True)

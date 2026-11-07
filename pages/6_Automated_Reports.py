
import streamlit as st
import joblib
import pandas as pd

from pathlib import Path

from data_utils import load_data, apply_styles, show_sidebar
from recommendation_engine import generate_recommendations
from risk_engine import assess_student_risk
from report_generator import generate_student_pdf


# Page configuration
st.set_page_config(
    page_title="Automated Reports | EduAnalytics",
    page_icon=":material/description:",
    layout="wide"
)

# Shared design
apply_styles()
show_sidebar()


# Page heading
st.title("Automated Student Reports")

st.caption(
    "Generate detailed academic performance reports "
    "with personalized recommendations and risk assessments."
)

st.divider()


# Load student data
df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()


# Student selection
st.subheader("Select Student")

student_options = {
    f"{row['name']} ({row['student_id']})": row["student_id"]
    for _, row in df.iterrows()
}

selected_student = st.selectbox(
    "Choose a student for the report",
    list(student_options.keys())
)

student_id = student_options[selected_student]

student = df[
    df["student_id"] == student_id
].iloc[0]


# Student overview
st.divider()
st.subheader("Report Preview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Student", student["name"])

with col2:
    st.metric("Class", student["class_name"])

with col3:
    st.metric(
        "Average Marks",
        f"{student['average_marks']:.1f}%"
    )

with col4:
    st.metric(
        "Attendance",
        f"{student['attendance']:.1f}%"
    )


# Generate recommendations and risk assessment
recommendations = generate_recommendations(student)

risk_assessment = assess_student_risk(student)


# Optional performance prediction
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
                "study_hours": float(student["study_hours"])
            }]
        )

        predicted_average = float(
            model.predict(prediction_input)[0]
        )

        predicted_average = max(
            0,
            min(100, predicted_average)
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


# Report contents
st.divider()
st.subheader("Report Contents")

st.write("Your PDF report will include:")

report_items = [
    "Student information",
    "Academic overview",
    "Subject-wise performance",
    "Student risk assessment",
    "Identified risk factors",
    "Personalized recommendations"
]

if predicted_average is not None:
    report_items.append("Estimated performance prediction")

for item in report_items:
    st.write(f"✓ {item}")


# Risk preview
st.divider()
st.subheader("Student Risk Overview")

risk_colors = {
    "High": "#B85C5C",
    "Moderate": "#C49A45",
    "Low": "#52745A"
}

risk_level = risk_assessment["risk_level"]

st.markdown(
    f"""
    <div style="
        padding: 16px;
        border-radius: 8px;
        background-color: rgba(128,128,128,0.07);
        border-left: 5px solid {risk_colors[risk_level]};
    ">
        <strong>Risk Level: </strong>
        <span style="color:{risk_colors[risk_level]};">
            {risk_level}
        </span>
        <br/>
        <strong>Risk Score:</strong>
        {risk_assessment['risk_score']}
    </div>
    """,
    unsafe_allow_html=True
)


# PDF generation
st.divider()
st.subheader("Generate PDF Report")

if st.button(
    "Generate Student Report",
    type="primary",
    use_container_width=True
):

    try:
        pdf_data = generate_student_pdf(
            student=student,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            predicted_average=predicted_average
        )

        st.session_state["student_pdf"] = pdf_data
        st.session_state["student_pdf_id"] = str(student_id)

        st.success("Student report generated successfully!")

    except Exception as error:
        st.error(f"Unable to generate report: {error}")


# Download button
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
        use_container_width=True
    )


st.caption(
    "Reports contain estimated predictions and rule-based "
    "recommendations. They should support teacher judgement."
)

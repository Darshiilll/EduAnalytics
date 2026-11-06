
import streamlit as st
import pandas as pd

from data_utils import load_data, apply_styles, show_sidebar
from risk_engine import assess_student_risk

# Page configuration
st.set_page_config(
    page_title="Student Risk Detection | EduAnalytics",
    page_icon=":material/warning:",
    layout="wide"
)

# Shared design and navigation
apply_styles()
show_sidebar()

# Page heading
st.title("Student Risk Detection")
st.caption(
    "Identify students who may benefit from additional academic support."
)

st.divider()

# Load student data
df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()

# Assess risk for every student
risk_results = []

for _, student in df.iterrows():
    result = assess_student_risk(student)

    risk_results.append({
        "student_id": student["student_id"],
        "name": student["name"],
        "class_name": student["class_name"],
        "average_marks": student["average_marks"],
        "attendance": student["attendance"],
        "study_hours": student["study_hours"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "risk_factors": result["risk_factors"],
        "weak_subjects": result["weak_subjects"]
    })

risk_df = pd.DataFrame(risk_results)

# Summary metrics
st.subheader("Risk Overview")

high_count = (risk_df["risk_level"] == "High").sum()
moderate_count = (risk_df["risk_level"] == "Moderate").sum()
low_count = (risk_df["risk_level"] == "Low").sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", len(risk_df))

with col2:
    st.metric("High Risk", int(high_count))

with col3:
    st.metric("Moderate Risk", int(moderate_count))

with col4:
    st.metric("Low Risk", int(low_count))

st.divider()

# Risk distribution
st.subheader("Risk Distribution")

distribution = (
    risk_df["risk_level"]
    .value_counts()
    .reindex(["High", "Moderate", "Low"], fill_value=0)
)

chart_data = pd.DataFrame({
    "Risk Level": distribution.index,
    "Students": distribution.values
})

st.bar_chart(
    chart_data,
    x="Risk Level",
    y="Students",
    color="#52745A"
)

st.divider()

# Student filters
st.subheader("Find Students by Risk Level")

col1, col2 = st.columns(2)

with col1:
    selected_risk = st.selectbox(
        "Filter by risk level",
        ["All", "High", "Moderate", "Low"]
    )

with col2:
    selected_class = st.selectbox(
        "Filter by class",
        ["All"] + sorted(
            risk_df["class_name"].dropna().astype(str).unique().tolist()
        )
    )

filtered_df = risk_df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_level"] == selected_risk
    ]

if selected_class != "All":
    filtered_df = filtered_df[
        filtered_df["class_name"].astype(str) == selected_class
    ]

# Student table
st.subheader("Student Risk Register")

display_df = filtered_df[
    [
        "student_id",
        "name",
        "class_name",
        "average_marks",
        "attendance",
        "study_hours",
        "risk_score",
        "risk_level"
    ]
].copy()

display_df.columns = [
    "Student ID",
    "Student Name",
    "Class",
    "Average Marks",
    "Attendance (%)",
    "Study Hours",
    "Risk Score",
    "Risk Level"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

if filtered_df.empty:
    st.info("No students match the selected filters.")

st.divider()

# Individual risk details
st.subheader("Individual Risk Assessment")

if not filtered_df.empty:
    student_options = {
        f"{row['name']} ({row['student_id']})": row["student_id"]
        for _, row in filtered_df.iterrows()
    }

    selected_student = st.selectbox(
        "Select a student to inspect risk factors",
        list(student_options.keys()),
        key="risk_student"
    )

    selected_id = student_options[selected_student]

    selected_record = filtered_df[
        filtered_df["student_id"] == selected_id
    ].iloc[0]

    risk_level = selected_record["risk_level"]

    risk_colors = {
        "High": "#B85C5C",
        "Moderate": "#C49A45",
        "Low": "#52745A"
    }

    color = risk_colors[risk_level]

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            padding: 15px 18px;
            background-color: rgba(128, 128, 128, 0.07);
            border-radius: 8px;
            margin-bottom: 15px;
        ">
            <h4 style="margin: 0;">{selected_record['name']}</h4>
            <p style="margin: 5px 0;">
                Risk Level:
                <strong style="color: {color};">{risk_level}</strong>
            </p>
            <p style="margin: 0;">
                Risk Score: {selected_record['risk_score']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("**Identified Risk Factors**")

    for factor in selected_record["risk_factors"]:
        st.write(f"- {factor}")

    if selected_record["weak_subjects"]:
        st.markdown("**Subjects Requiring Attention**")
        st.write(", ".join(selected_record["weak_subjects"]))

    else:
        st.success("No subjects are currently below 40 marks.")

# Download report
st.divider()
st.subheader("Download Risk Assessment Report")

report_df = risk_df[
    [
        "student_id",
        "name",
        "class_name",
        "average_marks",
        "attendance",
        "study_hours",
        "risk_score",
        "risk_level"
    ]
].copy()

report_df["risk_factors"] = risk_df["risk_factors"].apply(
    lambda factors: "; ".join(factors)
)

csv_data = report_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Risk Report (.csv)",
    data=csv_data,
    file_name="student_risk_assessment.csv",
    mime="text/csv"
)

st.caption(
    "Risk classifications use initial rule-based thresholds. "
    "They are indicators for teacher review, not definitive "
    "judgements or validated predictions of student outcomes."
)

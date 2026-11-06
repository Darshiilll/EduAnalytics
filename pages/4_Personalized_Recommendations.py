
import streamlit as st
import pandas as pd

from data_utils import load_data, apply_styles, show_sidebar
from recommendation_engine import (
    generate_recommendations,
    get_recommendation_summary
)

# Page configuration
st.set_page_config(
    page_title="Personalized Recommendations | EduAnalytics",
    page_icon="🎯",
    layout="wide"
)

# Shared design and navigation
apply_styles()
show_sidebar()

# Page heading
st.title("Personalized Recommendations")
st.caption(
    "Individual academic guidance based on student performance, "
    "attendance and study habits."
)

st.divider()

# Load student data
df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()

# Student selection
st.subheader("Select a Student")

student_options = {
    f"{row['name']} ({row['student_id']})": row["student_id"]
    for _, row in df.iterrows()
}

selected_student = st.selectbox(
    "Choose a student to view personalized recommendations",
    options=list(student_options.keys())
)

student_id = student_options[selected_student]
student = df[df["student_id"] == student_id].iloc[0]

# Student overview
st.divider()
st.subheader("Student Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Student", student["name"])

with col2:
    st.metric("Class", student["class_name"])

with col3:
    st.metric("Average Marks", f"{student['average_marks']:.1f}%")

with col4:
    st.metric("Attendance", f"{student['attendance']:.1f}%")

# Generate recommendations
recommendations = generate_recommendations(student)
summary = get_recommendation_summary(recommendations)

# Recommendation summary
st.divider()
st.subheader("Recommendation Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Recommendations", summary["total"])

with col2:
    st.metric("High Priority", summary["high"])

with col3:
    st.metric("Medium Priority", summary["medium"])

with col4:
    st.metric("Low Priority", summary["low"])

# Recommendation cards
st.divider()
st.subheader("Personalized Action Plan")

if not recommendations:
    st.success(
        "No specific recommendations at this time. "
        "Continue monitoring the student's progress."
    )
else:
    priority_colors = {
        "High": "#B85C5C",
        "Medium": "#C49A45",
        "Low": "#52745A"
    }

    for index, item in enumerate(recommendations, start=1):
        priority = item["priority"]
        color = priority_colors.get(priority, "#777D73")

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**{index}. {item['category']}**")
                st.write(item["observation"])
                st.write(item["recommendation"])

            with col2:
                st.markdown(
                    f"""
                    <div style="
                        background-color: {color};
                        color: white;
                        padding: 7px 10px;
                        border-radius: 6px;
                        text-align: center;
                        font-weight: 600;
                        margin-top: 8px;
                    ">
                        {priority} Priority
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Downloadable report
st.divider()
st.subheader("Download Recommendation Report")

report_lines = [
    "EduAnalytics - Personalized Recommendation Report",
    f"Student: {student['name']}",
    f"Student ID: {student['student_id']}",
    f"Class: {student['class_name']}",
    f"Average Marks: {student['average_marks']:.1f}%",
    f"Attendance: {student['attendance']:.1f}%",
    f"Study Hours: {student['study_hours']}",
    "",
    "PERSONALIZED RECOMMENDATIONS",
    ""
]

for index, item in enumerate(recommendations, start=1):
    report_lines.extend([
        f"{index}. {item['category']} - {item['priority']} Priority",
        f"Observation: {item['observation']}",
        f"Recommendation: {item['recommendation']}",
        ""
    ])

report_text = "\n".join(report_lines)

safe_student_id = "".join(
    character for character in str(student_id)
    if character.isalnum() or character in ("-", "_")
)

st.download_button(
    label="Download Report (.txt)",
    data=report_text,
    file_name=f"recommendations_{safe_student_id}.txt",
    mime="text/plain"
)

st.caption(
    "Note: Recommendations are rule-based guidance using configurable "
    "thresholds. They should support teacher judgement, not replace it."
)


import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Academic Analytics | EduAnalytics",
    page_icon="📊",
    layout="wide"
)

apply_styles()

show_sidebar()

df = load_data()


# ==================================================
# 2. SUBJECT CONFIGURATION
# ==================================================

subject_columns = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]

subject_names = {
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English",
    "social_science_marks": "Social Science",
    "computer_marks": "Computer"
}

chart_colors = [
    "#52745A",
    "#91A68A",
    "#C4A779",
    "#758B9B",
    "#B58B83"
]


# ==================================================
# 3. PAGE HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">WORKSPACE / ANALYTICS</div>',
    unsafe_allow_html=True
)

st.title("Academic Analytics")

st.markdown(
    '<p class="subtitle">Understand academic performance, '
    'attendance patterns and classroom trends.</p>',
    unsafe_allow_html=True
)

st.caption(
    "Explore meaningful insights from student performance "
    "across all five academic subjects."
)

st.divider()


# ==================================================
# 4. ACADEMIC OVERVIEW
# ==================================================

st.markdown(
    '<div class="eyebrow">AT A GLANCE</div>',
    unsafe_allow_html=True
)

st.subheader("Academic Overview")

total_students = len(df)

average_score = (
    df["average_marks"].mean()
    if total_students > 0 else 0
)

pass_rate = (
    (df["average_marks"] >= 40).mean() * 100
    if total_students > 0 else 0
)

average_attendance = (
    df["attendance"].mean()
    if total_students > 0 else 0
)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.metric(
        "Total Students",
        f"{total_students:,}"
    )

with col2:
    st.metric(
        "Average Score",
        f"{average_score:.1f}%"
    )

with col3:
    st.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )

with col4:
    st.metric(
        "Average Attendance",
        f"{average_attendance:.1f}%"
    )


st.divider()


# ==================================================
# 5. SUBJECT-WISE PERFORMANCE
# ==================================================

st.markdown(
    '<div class="eyebrow">SUBJECT ANALYSIS</div>',
    unsafe_allow_html=True
)

st.subheader("Subject-wise Performance")

st.caption(
    "Compare average marks across Mathematics, Science, English, "
    "Social Science and Computer."
)

subject_data = pd.DataFrame({
    "Subject": [
        subject_names[column]
        for column in subject_columns
    ],
    "Average Marks": [
        df[column].mean()
        for column in subject_columns
    ]
})

subject_fig = px.bar(
    subject_data,
    x="Subject",
    y="Average Marks",
    color="Subject",
    text_auto=".1f",
    color_discrete_sequence=chart_colors
)

subject_fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family="DM Sans, sans-serif",
        size=12,
        color="#252923"
    ),
    showlegend=False,
    yaxis_range=[0, 100],
    xaxis_title="",
    yaxis_title="Average Marks",
    margin=dict(l=15, r=15, t=25, b=15),
    bargap=0.4
)

subject_fig.update_traces(
    textposition="outside",
    cliponaxis=False
)

st.plotly_chart(
    subject_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.divider()


# ==================================================
# 6. STUDENT MARKS DISTRIBUTION
# ==================================================

st.markdown(
    '<div class="eyebrow">PERFORMANCE DISTRIBUTION</div>',
    unsafe_allow_html=True
)

st.subheader("Student Marks Distribution")

st.caption(
    "Understand how students are distributed across different "
    "average-score ranges."
)

marks_fig = px.histogram(
    df,
    x="average_marks",
    nbins=15,
    color_discrete_sequence=["#52745A"],
    labels={
        "average_marks": "Average Marks",
        "count": "Number of Students"
    }
)

marks_fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family="DM Sans, sans-serif",
        size=12,
        color="#252923"
    ),
    xaxis_title="Average Marks",
    yaxis_title="Number of Students",
    margin=dict(l=15, r=15, t=25, b=15)
)

st.plotly_chart(
    marks_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.divider()


# ==================================================
# 7. ATTENDANCE DISTRIBUTION
# ==================================================

st.markdown(
    '<div class="eyebrow">ATTENDANCE ANALYSIS</div>',
    unsafe_allow_html=True
)

st.subheader("Attendance Distribution")

st.caption(
    "Explore student attendance patterns and identify "
    "how frequently different attendance levels occur."
)

attendance_fig = px.histogram(
    df,
    x="attendance",
    nbins=15,
    color_discrete_sequence=["#C4A779"],
    labels={
        "attendance": "Attendance Percentage",
        "count": "Number of Students"
    }
)

attendance_fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family="DM Sans, sans-serif",
        size=12,
        color="#252923"
    ),
    xaxis_title="Attendance (%)",
    yaxis_title="Number of Students",
    margin=dict(l=15, r=15, t=25, b=15)
)

st.plotly_chart(
    attendance_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.divider()


# ==================================================
# 8. CLASS-WISE SUBJECT PERFORMANCE
# ==================================================

st.markdown(
    '<div class="eyebrow">CLASS COMPARISON</div>',
    unsafe_allow_html=True
)

st.subheader("Class-wise Subject Performance")

st.caption(
    "Compare the average marks obtained by each class "
    "across all five subjects."
)

class_subject_data = df.melt(
    id_vars=["class_name"],
    value_vars=subject_columns,
    var_name="Subject",
    value_name="Marks"
)

class_subject_data["Subject"] = (
    class_subject_data["Subject"].map(subject_names)
)

class_performance = (
    class_subject_data
    .groupby(
        ["class_name", "Subject"],
        as_index=False
    )["Marks"]
    .mean()
)

class_fig = px.bar(
    class_performance,
    x="class_name",
    y="Marks",
    color="Subject",
    barmode="group",
    text_auto=".1f",
    color_discrete_sequence=chart_colors,
    labels={
        "class_name": "Class",
        "Marks": "Average Marks",
        "Subject": "Subject"
    }
)

class_fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family="DM Sans, sans-serif",
        size=12,
        color="#252923"
    ),
    yaxis_range=[0, 100],
    xaxis_title="Class",
    yaxis_title="Average Marks",
    legend_title="Subject",
    margin=dict(l=15, r=15, t=25, b=15),
    bargap=0.2
)

st.plotly_chart(
    class_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.divider()


# ==================================================
# 9. CLASS PERFORMANCE SUMMARY
# ==================================================

st.markdown(
    '<div class="eyebrow">CLASS INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Class Performance Summary")

st.caption(
    "Review student counts, average marks and attendance "
    "for each class."
)

class_summary = (
    df.groupby("class_name")
    .agg(
        Total_Students=("student_id", "count"),
        Average_Score=("average_marks", "mean"),
        Average_Attendance=("attendance", "mean")
    )
    .reset_index()
)

class_summary = class_summary.rename(
    columns={
        "class_name": "Class",
        "Total_Students": "Total Students",
        "Average_Score": "Average Score (%)",
        "Average_Attendance": "Average Attendance (%)"
    }
)

st.dataframe(
    class_summary.style.format({
        "Average Score (%)": "{:.1f}",
        "Average Attendance (%)": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True,
    height=220
)


# ==================================================
# 10. FOOTER
# ==================================================

st.divider()

st.caption(
    "EduAnalytics | Academic Analytics & Performance Insights"
)

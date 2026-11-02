
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EduAnalytics | Dashboard",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA AND APPLY DESIGN
# --------------------------------------------------

apply_styles()

df = load_data()

show_sidebar()


# --------------------------------------------------
# SUBJECT CONFIGURATION
# --------------------------------------------------

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


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("EduAnalytics Dashboard")

st.markdown(
    "### Student Performance Analysis & Prediction System"
)

st.caption(
    "Monitor academic performance, attendance, and student progress."
)

st.divider()


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

total_students = len(df)

average_marks = df["average_marks"].mean()

pass_rate = (
    (df["average_marks"] >= 40).mean() * 100
    if total_students > 0 else 0
)

average_attendance = df["attendance"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Students Enrolled",
        total_students
    )

with col2:
    st.metric(
        "Average Score",
        f"{average_marks:.1f}%"
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


# --------------------------------------------------
# ACADEMIC PERFORMANCE
# --------------------------------------------------

st.subheader("Academic Performance")

left, right = st.columns(2)

# Subject-wise performance
with left:

    subject_average = (
        df[subject_columns]
        .mean()
        .reset_index()
    )

    subject_average.columns = [
        "Subject",
        "Average Marks"
    ]

    subject_average["Subject"] = (
        subject_average["Subject"]
        .map(subject_names)
    )

    fig_subjects = px.bar(
        subject_average,
        x="Subject",
        y="Average Marks",
        title="Average Marks by Subject",
        text_auto=".1f"
    )

    fig_subjects.update_layout(
        yaxis_range=[0, 100],
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_subjects,
        use_container_width=True
    )


# Class-wise performance
with right:

    class_average = (
        df.groupby("class_name")["average_marks"]
        .mean()
        .reset_index()
    )

    fig_classes = px.bar(
        class_average,
        x="class_name",
        y="average_marks",
        title="Class-wise Average Performance",
        labels={
            "class_name": "Class",
            "average_marks": "Average Marks"
        },
        text_auto=".1f"
    )

    fig_classes.update_layout(
        yaxis_range=[0, 100],
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_classes,
        use_container_width=True
    )


st.divider()


# --------------------------------------------------
# STUDENT PERFORMANCE OVERVIEW
# --------------------------------------------------

st.subheader("Student Performance Overview")

col1, col2 = st.columns(2)

with col1:

    performance_df = pd.DataFrame({
        "Performance": ["Passed", "Needs Improvement"],
        "Students": [
            (df["average_marks"] >= 40).sum(),
            (df["average_marks"] < 40).sum()
        ]
    })

    fig_pass = px.pie(
        performance_df,
        names="Performance",
        values="Students",
        title="Pass and Improvement Distribution",
        hole=0.45
    )

    st.plotly_chart(
        fig_pass,
        use_container_width=True
    )


with col2:

    fig_attendance = px.histogram(
        df,
        x="attendance",
        nbins=10,
        title="Student Attendance Distribution",
        labels={
            "attendance": "Attendance (%)"
        }
    )

    fig_attendance.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_attendance,
        use_container_width=True
    )


st.divider()


# --------------------------------------------------
# RECENT STUDENT RECORDS
# --------------------------------------------------

st.subheader("Student Records Preview")

st.dataframe(
    df[
        [
            "student_id",
            "name",
            "class_name",
            "average_marks",
            "attendance"
        ]
    ].head(10),
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "EduAnalytics | Student Performance Analysis System"
)

st.caption(
    "Academic insights powered by Python, Pandas, "
    "Plotly and Streamlit."
)

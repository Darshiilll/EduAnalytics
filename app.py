
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EduAnalytics | Dashboard",
    page_icon="🎓",
    layout="wide"
)

apply_styles()

df = load_data()

show_sidebar()


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
# 3. DASHBOARD HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">EDUCATION / OVERVIEW</div>',
    unsafe_allow_html=True
)

st.title("Dashboard")

st.markdown(
    '<p class="subtitle">Student Performance Analysis & Prediction System</p>',
    unsafe_allow_html=True
)

st.caption(
    "Monitor academic performance, attendance and student progress "
    "through meaningful insights."
)

st.divider()


# ==================================================
# 4. CALCULATE DASHBOARD METRICS
# ==================================================

total_students = len(df)

average_marks = (
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


# ==================================================
# 5. KEY PERFORMANCE INDICATORS
# ==================================================

st.markdown(
    '<div class="eyebrow">AT A GLANCE</div>',
    unsafe_allow_html=True
)

st.subheader("Academic Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Students Enrolled",
        value=f"{total_students:,}"
    )

with col2:
    st.metric(
        label="Average Score",
        value=f"{average_marks:.1f}%"
    )

with col3:
    st.metric(
        label="Pass Rate",
        value=f"{pass_rate:.1f}%"
    )

with col4:
    st.metric(
        label="Average Attendance",
        value=f"{average_attendance:.1f}%"
    )

st.divider()


# ==================================================
# 6. ACADEMIC PERFORMANCE
# ==================================================

st.markdown(
    '<div class="eyebrow">PERFORMANCE INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Academic Performance")

st.caption(
    "Compare subject averages and understand how different classes perform."
)

left, right = st.columns(2, gap="large")


# ---------- SUBJECT-WISE PERFORMANCE ----------

with left:

    subject_average = pd.DataFrame({
        "Subject": [
            subject_names[column]
            for column in subject_columns
        ],
        "Average Marks": [
            df[column].mean()
            for column in subject_columns
        ]
    })

    fig_subjects = px.bar(
        subject_average,
        x="Subject",
        y="Average Marks",
        color="Subject",
        text_auto=".1f",
        color_discrete_sequence=chart_colors,
        title="Average Marks by Subject"
    )

    fig_subjects.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="DM Sans, sans-serif",
            color="#252923",
            size=12
        ),
        title_font=dict(
            family="Manrope, sans-serif",
            size=17,
            color="#252923"
        ),
        showlegend=False,
        yaxis_range=[0, 100],
        xaxis_title="",
        yaxis_title="Average Marks",
        margin=dict(l=15, r=15, t=55, b=15),
        bargap=0.4
    )

    fig_subjects.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig_subjects,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ---------- CLASS-WISE PERFORMANCE ----------

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
        color_discrete_sequence=["#52745A"],
        text_auto=".1f",
        title="Class-wise Average Performance",
        labels={
            "class_name": "Class",
            "average_marks": "Average Marks"
        }
    )

    fig_classes.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="DM Sans, sans-serif",
            color="#252923",
            size=12
        ),
        title_font=dict(
            family="Manrope, sans-serif",
            size=17,
            color="#252923"
        ),
        showlegend=False,
        yaxis_range=[0, 100],
        xaxis_title="Class",
        yaxis_title="Average Marks",
        margin=dict(l=15, r=15, t=55, b=15),
        bargap=0.4
    )

    fig_classes.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig_classes,
        use_container_width=True,
        config={"displayModeBar": False}
    )


st.divider()


# ==================================================
# 7. STUDENT PERFORMANCE OVERVIEW
# ==================================================

st.markdown(
    '<div class="eyebrow">STUDENT INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Student Performance Overview")

st.caption(
    "Understand the overall pass distribution and attendance patterns."
)

col1, col2 = st.columns(2, gap="large")


# ---------- PASS DISTRIBUTION ----------

with col1:

    performance_df = pd.DataFrame({
        "Performance": [
            "Passed",
            "Needs Improvement"
        ],
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
        hole=0.55,
        color="Performance",
        color_discrete_map={
            "Passed": "#52745A",
            "Needs Improvement": "#C4A779"
        }
    )

    fig_pass.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="DM Sans, sans-serif",
            color="#252923",
            size=12
        ),
        title_font=dict(
            family="Manrope, sans-serif",
            size=17
        ),
        legend_title_text="",
        margin=dict(l=15, r=15, t=55, b=15)
    )

    st.plotly_chart(
        fig_pass,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ---------- ATTENDANCE DISTRIBUTION ----------

with col2:

    fig_attendance = px.histogram(
        df,
        x="attendance",
        nbins=12,
        title="Student Attendance Distribution",
        color_discrete_sequence=["#91A68A"],
        labels={
            "attendance": "Attendance (%)",
            "count": "Number of Students"
        }
    )

    fig_attendance.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="DM Sans, sans-serif",
            color="#252923",
            size=12
        ),
        title_font=dict(
            family="Manrope, sans-serif",
            size=17
        ),
        xaxis_title="Attendance (%)",
        yaxis_title="Number of Students",
        margin=dict(l=15, r=15, t=55, b=15)
    )

    st.plotly_chart(
        fig_attendance,
        use_container_width=True,
        config={"displayModeBar": False}
    )


st.divider()


# ==================================================
# 8. RECENT STUDENT RECORDS
# ==================================================

st.markdown(
    '<div class="eyebrow">STUDENT DIRECTORY</div>',
    unsafe_allow_html=True
)

st.subheader("Student Records Preview")

st.caption(
    "A quick look at the latest records available in the dataset."
)

preview_columns = [
    "student_id",
    "name",
    "class_name",
    "average_marks",
    "attendance"
]

preview_df = (
    df[preview_columns]
    .head(10)
    .copy()
)

preview_df = preview_df.rename(
    columns={
        "student_id": "Student ID",
        "name": "Student Name",
        "class_name": "Class",
        "average_marks": "Average Marks",
        "attendance": "Attendance (%)"
    }
)

st.dataframe(
    preview_df.style.format({
        "Average Marks": "{:.1f}",
        "Attendance (%)": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True,
    height=390
)


# ==================================================
# 9. FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        padding: 12px 0 4px 0;
        color: #777D73;
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        line-height: 1.8;
    ">
        <strong style="color: #52745A;">EduAnalytics</strong>
        &nbsp; | &nbsp; Student Performance Analysis System
        <br>
        Academic insights powered by Python, Pandas,
        Plotly and Streamlit.
    </div>
    """,
    unsafe_allow_html=True
)

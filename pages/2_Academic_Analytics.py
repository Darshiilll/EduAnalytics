
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Academic Analytics | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()

df = load_data()
show_sidebar()


# ==================================================
# 2. CONSTANTS
# ==================================================

SUBJECT_COLUMNS = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]

SUBJECT_NAMES = {
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English",
    "social_science_marks": "Social Science",
    "computer_marks": "Computer"
}

CHART_COLORS = [
    "#52745A",
    "#91A68A",
    "#C4A779",
    "#AAB9A1",
    "#D7C8A8"
]

TEXT_COLOR = "#252923"
MUTED_COLOR = "#777D73"
GRID_COLOR = "#E5E7DF"


# ==================================================
# 3. CHART STYLING
# ==================================================

def style_chart(fig, height=350):

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color=TEXT_COLOR,
            size=12
        ),
        margin=dict(
            l=15,
            r=25,
            t=25,
            b=20
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="DM Sans"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID_COLOR,
        tickfont=dict(color=MUTED_COLOR)
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(color=MUTED_COLOR)
    )

    return fig


# ==================================================
# 4. PAGE HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">WORKSPACE / ANALYTICS</div>',
    unsafe_allow_html=True
)

st.title("Academic Analytics")

st.markdown(
    """
    <p class="subtitle">
        Understand academic performance, attendance patterns,
        and classroom trends.
    </p>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Explore meaningful insights from student performance "
    "across all five academic subjects."
)

st.markdown("<br>", unsafe_allow_html=True)


# ==================================================
# 5. ACADEMIC OVERVIEW
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
        f"{average_score:.1f}/100"
    )

with col3:
    st.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )

with col4:
    st.metric(
        "Attendance",
        f"{average_attendance:.1f}%"
    )


# ==================================================
# 6. SUBJECT-WISE PERFORMANCE
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">SUBJECT ANALYSIS</div>',
    unsafe_allow_html=True
)

st.subheader("Subject-wise Performance")

st.caption(
    "Compare average marks across all five academic subjects."
)

subject_data = pd.DataFrame({
    "Subject": [
        SUBJECT_NAMES[column]
        for column in SUBJECT_COLUMNS
    ],
    "Average Marks": [
        df[column].mean()
        for column in SUBJECT_COLUMNS
    ]
})

subject_fig = px.bar(
    subject_data,
    x="Average Marks",
    y="Subject",
    orientation="h",
    color="Subject",
    text_auto=".1f",
    color_discrete_sequence=CHART_COLORS
)

subject_fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    marker_line_width=0
)

subject_fig.update_layout(
    showlegend=False,
    xaxis=dict(
        title="Average Marks",
        range=[0, 112]
    ),
    yaxis=dict(
        title=None,
        categoryorder="array",
        categoryarray=[
            "Computer",
            "Social Science",
            "English",
            "Science",
            "Mathematics"
        ]
    ),
    bargap=0.35
)

subject_fig = style_chart(subject_fig, height=370)

subject_fig.update_xaxes(
    title="Average Marks",
    range=[0, 112],
    showgrid=True,
    gridcolor=GRID_COLOR
)

subject_fig.update_yaxes(
    title=None,
    showgrid=False
)

st.plotly_chart(
    subject_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==================================================
# 7. STUDENT MARKS DISTRIBUTION
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">PERFORMANCE DISTRIBUTION</div>',
    unsafe_allow_html=True
)

st.subheader("Student Marks Distribution")

st.caption(
    "Understand how students are distributed across "
    "different average-score ranges."
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

marks_fig.update_traces(
    marker_line_color="white",
    marker_line_width=1
)

marks_fig.update_layout(
    xaxis_title="Average Marks",
    yaxis_title="Number of Students"
)

marks_fig = style_chart(marks_fig, height=350)

marks_fig.update_xaxes(
    title="Average Marks",
    showgrid=False
)

marks_fig.update_yaxes(
    title="Number of Students",
    showgrid=True,
    gridcolor=GRID_COLOR
)

st.plotly_chart(
    marks_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==================================================
# 8. ATTENDANCE DISTRIBUTION
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

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

attendance_fig.update_traces(
    marker_line_color="white",
    marker_line_width=1
)

attendance_fig.update_layout(
    xaxis_title="Attendance (%)",
    yaxis_title="Number of Students"
)

attendance_fig = style_chart(attendance_fig, height=350)

attendance_fig.update_xaxes(
    title="Attendance (%)",
    showgrid=False
)

attendance_fig.update_yaxes(
    title="Number of Students",
    showgrid=True,
    gridcolor=GRID_COLOR
)

st.plotly_chart(
    attendance_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==================================================
# 9. CLASS-WISE SUBJECT PERFORMANCE
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

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
    value_vars=SUBJECT_COLUMNS,
    var_name="Subject",
    value_name="Marks"
)

class_subject_data["Subject"] = (
    class_subject_data["Subject"].map(SUBJECT_NAMES)
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
    color_discrete_sequence=CHART_COLORS,
    labels={
        "class_name": "Class",
        "Marks": "Average Marks",
        "Subject": "Subject"
    }
)

class_fig.update_traces(
    marker_line_width=0,
    textposition="outside",
    cliponaxis=False
)

class_fig.update_layout(
    yaxis=dict(
        title="Average Marks",
        range=[0, 115]
    ),
    xaxis=dict(title="Class"),
    legend=dict(
        title=None,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    bargap=0.2,
    bargroupgap=0.08
)

class_fig = style_chart(class_fig, height=440)

class_fig.update_xaxes(
    title="Class",
    showgrid=False
)

class_fig.update_yaxes(
    title="Average Marks",
    range=[0, 115],
    showgrid=True,
    gridcolor=GRID_COLOR
)

st.plotly_chart(
    class_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==================================================
# 10. CLASS PERFORMANCE SUMMARY
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">CLASS INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Class Performance Summary")

st.caption(
    "Review student counts, average marks, and attendance "
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

class_summary["Average Score (%)"] = (
    class_summary["Average Score (%)"].round(1)
)

class_summary["Average Attendance (%)"] = (
    class_summary["Average Attendance (%)"].round(1)
)

st.dataframe(
    class_summary,
    use_container_width=True,
    hide_index=True,
    height=220
)


# ==================================================
# 11. FOOTER
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        text-align:center;
        padding:30px 0 10px 0;
        color:#777D73;
        font-size:12px;
        border-top:1px solid #E5E7DF;
        margin-top:30px;
    ">
        EduAnalytics · Academic Analytics & Performance Insights
    </div>
    """,
    unsafe_allow_html=True
)

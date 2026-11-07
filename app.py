
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_utils import (
    load_data,
    apply_styles,
    show_sidebar,
    SUBJECT_COLUMNS,
    SUBJECT_NAMES,
    CHART_COLORS,
    LOGO_PATH
)
from risk_engine import assess_student_risk


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EduAnalytics | Dashboard",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📊",
    layout="wide"
)

apply_styles()

# Dashboard-specific metric adjustment
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    [data-testid="stMetric"] {
        min-width: 0 !important;
        overflow: visible !important;
    }

    [data-testid="stMetricLabel"] {
        white-space: normal !important;
    }
</style>
""", unsafe_allow_html=True)

df = load_data()
show_sidebar()


# =========================================================
# CONSTANTS
# =========================================================

TEXT_COLOR = "#252923"
MUTED_COLOR = "#777D73"
GRID_COLOR = "#E5E7DF"


# =========================================================
# CHART STYLING
# =========================================================

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
        margin=dict(l=15, r=25, t=25, b=15),
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


# =========================================================
# DATA VALIDATION
# =========================================================

if df is None or df.empty:

    st.warning(
        "No student records are available. "
        "Please check data/students.csv."
    )

    st.stop()


required_columns = [
    "student_id",
    "name",
    "class_name",
    "gender",
    "average_marks",
    "attendance",
    "study_hours",
    *SUBJECT_COLUMNS
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        "Missing required dataset columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <div class="eyebrow">OVERVIEW</div>
    <h1>Dashboard</h1>
    <p class="subtitle">
        Monitor student performance, academic progress,
        and attendance across all classes.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# STUDENT RISK ASSESSMENT
# =========================================================

risk_records = []

for _, student in df.iterrows():

    result = assess_student_risk(student)

    risk_records.append({
        "student_id": student["student_id"],
        "name": student["name"],
        "class_name": student["class_name"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "risk_factors": result["risk_factors"]
    })


risk_df = pd.DataFrame(risk_records)


# =========================================================
# KEY PERFORMANCE INDICATORS
# =========================================================

total_students = len(df)

average_score = float(
    df["average_marks"].mean()
)

pass_count = int(
    (df["average_marks"] >= 40).sum()
)

pass_rate = (
    pass_count / total_students * 100
    if total_students else 0
)

average_attendance = float(
    df["attendance"].mean()
)

high_risk_count = int(
    (risk_df["risk_level"] == "High").sum()
)

moderate_risk_count = int(
    (risk_df["risk_level"] == "Moderate").sum()
)

low_risk_count = int(
    (risk_df["risk_level"] == "Low").sum()
)


st.markdown(
    '<div class="eyebrow">KEY PERFORMANCE INDICATORS</div>',
    unsafe_allow_html=True
)

# Give the Average Score card slightly more width.
k1, k2, k3, k4 = st.columns(
    [1, 1.15, 1, 1],
    gap="medium"
)

with k1:
    st.metric(
        "Total Students",
        f"{total_students:,}"
    )

with k2:
    st.metric(
        "Average Score",
        f"{average_score:.1f}/100"
    )

with k3:
    st.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )

with k4:
    st.metric(
        "Attendance",
        f"{average_attendance:.1f}%"
    )


# =========================================================
# SUBJECT-WISE PERFORMANCE
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">ACADEMIC PERFORMANCE</div>',
    unsafe_allow_html=True
)

st.subheader("Subject-wise Performance")


subject_averages = (
    df[SUBJECT_COLUMNS]
    .mean()
    .rename(index=SUBJECT_NAMES)
    .reset_index()
)

subject_averages.columns = [
    "Subject",
    "Average Marks"
]

subject_order = [
    "Computer",
    "Social Science",
    "English",
    "Science",
    "Mathematics"
]

fig_subjects = px.bar(
    subject_averages,
    x="Average Marks",
    y="Subject",
    orientation="h",
    color="Subject",
    color_discrete_sequence=CHART_COLORS,
    text_auto=".1f"
)

fig_subjects.update_traces(
    marker_line_width=0,
    textposition="outside",
    textfont=dict(
        family="DM Sans",
        size=12,
        color=TEXT_COLOR
    ),
    cliponaxis=False
)

fig_subjects.update_layout(
    yaxis=dict(
        categoryorder="array",
        categoryarray=subject_order,
        title=None
    ),
    xaxis=dict(
        title=None,
        range=[
            0,
            max(
                100,
                float(subject_averages["Average Marks"].max()) + 12
            )
        ]
    ),
    showlegend=False
)

fig_subjects = style_chart(
    fig_subjects,
    height=370
)

fig_subjects.update_xaxes(
    title=None,
    range=[
        0,
        max(
            100,
            float(subject_averages["Average Marks"].max()) + 12
        )
    ],
    showgrid=True,
    gridcolor=GRID_COLOR
)

fig_subjects.update_yaxes(
    title=None,
    showgrid=False,
    categoryorder="array",
    categoryarray=subject_order
)

st.plotly_chart(
    fig_subjects,
    use_container_width=True,
    config={"displayModeBar": False}
)


# =========================================================
# CLASS-WISE PERFORMANCE AND PASS DISTRIBUTION
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns(
    2,
    gap="large"
)


# CLASS-WISE PERFORMANCE

with left_col:

    st.subheader("Class-wise Performance")

    class_average = (
        df.groupby("class_name")["average_marks"]
        .mean()
        .reset_index()
        .sort_values("class_name")
    )

    fig_class = px.bar(
        class_average,
        x="class_name",
        y="average_marks",
        color_discrete_sequence=["#52745A"],
        text_auto=".1f"
    )

    fig_class.update_traces(
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False
    )

    fig_class = style_chart(
        fig_class,
        height=330
    )

    fig_class.update_xaxes(
        title=None
    )

    fig_class.update_yaxes(
        title=None,
        range=[
            0,
            max(
                100,
                float(class_average["average_marks"].max()) + 12
            )
        ]
    )

    st.plotly_chart(
        fig_class,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# PASS DISTRIBUTION

with right_col:

    st.subheader("Pass Distribution")

    passed = int(
        (df["average_marks"] >= 40).sum()
    )

    failed = total_students - passed

    fig_pass = go.Figure(
        data=[
            go.Pie(
                labels=["Passed", "Below Pass Mark"],
                values=[passed, failed],
                hole=0.68,
                marker=dict(
                    colors=[
                        "#52745A",
                        "#C4A779"
                    ],
                    line=dict(
                        color="white",
                        width=4
                    )
                ),
                textinfo="none",
                hovertemplate=(
                    "%{label}<br>"
                    "Students: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                ),
                sort=False
            )
        ]
    )

    fig_pass.update_layout(
        annotations=[
            dict(
                text=f"<b>{total_students}</b><br>Students",
                x=0.5,
                y=0.5,
                font=dict(
                    size=19,
                    color=TEXT_COLOR,
                    family="Manrope"
                ),
                showarrow=False
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                family="DM Sans",
                size=13,
                color=TEXT_COLOR
            )
        ),
        margin=dict(
            l=15,
            r=15,
            t=25,
            b=45
        )
    )

    fig_pass = style_chart(
        fig_pass,
        height=350
    )

    fig_pass.update_layout(
        showlegend=True,
        annotations=[
            dict(
                text=f"<b>{total_students}</b><br>Students",
                x=0.5,
                y=0.5,
                font=dict(
                    size=19,
                    color=TEXT_COLOR,
                    family="Manrope"
                ),
                showarrow=False
            )
        ],
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top"
        ),
        margin=dict(
            l=15,
            r=15,
            t=25,
            b=45
        )
    )

    st.plotly_chart(
        fig_pass,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# =========================================================
# STUDENT RISK DISTRIBUTION
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">STUDENT SUPPORT INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Student Risk Distribution")


risk_left, risk_right = st.columns(
    [1.1, 1],
    gap="large"
)


# RISK DONUT CHART

with risk_left:

    risk_counts = (
        risk_df["risk_level"]
        .value_counts()
        .reindex(
            ["High", "Moderate", "Low"],
            fill_value=0
        )
    )

    risk_chart_data = pd.DataFrame({
        "Risk Level": risk_counts.index,
        "Students": risk_counts.values
    })

    fig_risk = px.pie(
        risk_chart_data,
        names="Risk Level",
        values="Students",
        hole=0.65,
        color="Risk Level",
        color_discrete_map={
            "High": "#B85C5C",
            "Moderate": "#C49A45",
            "Low": "#52745A"
        }
    )

    fig_risk.update_traces(
        textinfo="percent",
        marker=dict(
            line=dict(
                color="white",
                width=3
            )
        ),
        hovertemplate=(
            "%{label}<br>"
            "Students: %{value}"
            "<extra></extra>"
        )
    )

    fig_risk.update_layout(
        annotations=[
            dict(
                text=f"<b>{total_students}</b><br>Students",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(
                    size=18,
                    color=TEXT_COLOR,
                    family="Manrope"
                )
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08
        ),
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=45
        )
    )

    fig_risk = style_chart(
        fig_risk,
        height=340
    )

    fig_risk.update_layout(
        showlegend=True
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# RISK METRICS

with risk_right:

    st.metric(
        "High Risk Students",
        high_risk_count
    )

    st.metric(
        "Moderate Risk Students",
        moderate_risk_count
    )

    st.metric(
        "Low Risk Students",
        low_risk_count
    )

    st.caption(
        "Risk categories are based on the initial "
        "rule-based indicators used in Student Risk Detection."
    )


# =========================================================
# ATTENDANCE ANALYSIS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">ATTENDANCE INSIGHTS</div>',
    unsafe_allow_html=True
)

st.subheader("Student Attendance Distribution")


fig_attendance = px.histogram(
    df,
    x="attendance",
    nbins=15,
    color_discrete_sequence=["#91A68A"],
    labels={
        "attendance": "Attendance (%)",
        "count": "Number of Students"
    }
)

fig_attendance.update_traces(
    marker_line_color="white",
    marker_line_width=1
)

fig_attendance.update_xaxes(
    title="Attendance (%)"
)

fig_attendance.update_yaxes(
    title="Number of Students"
)

fig_attendance = style_chart(
    fig_attendance,
    height=320
)

st.plotly_chart(
    fig_attendance,
    use_container_width=True,
    config={"displayModeBar": False}
)


# =========================================================
# TOP PERFORMING STUDENTS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">STUDENT ACHIEVEMENT</div>',
    unsafe_allow_html=True
)

st.subheader("Top Performing Students")


top_students = (
    df.sort_values(
        "average_marks",
        ascending=False
    )[
        [
            "student_id",
            "name",
            "class_name",
            "average_marks",
            "attendance"
        ]
    ]
    .head(5)
    .copy()
    .reset_index(drop=True)
)

top_students.insert(
    0,
    "Rank",
    range(1, len(top_students) + 1)
)

top_students = top_students.rename(
    columns={
        "student_id": "Student ID",
        "name": "Student Name",
        "class_name": "Class",
        "average_marks": "Average Score",
        "attendance": "Attendance (%)"
    }
)

top_students["Average Score"] = (
    top_students["Average Score"].round(1)
)

top_students["Attendance (%)"] = (
    top_students["Attendance (%)"].round(1)
)

st.dataframe(
    top_students,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# STUDENT RECORDS PREVIEW
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">STUDENT DIRECTORY</div>',
    unsafe_allow_html=True
)

st.subheader("Student Records Preview")


display_columns = [
    "student_id",
    "name",
    "class_name",
    "gender",
    "average_marks",
    "attendance"
]

recent_students = df[
    display_columns
].head(8).copy()


recent_students = recent_students.rename(
    columns={
        "student_id": "Student ID",
        "name": "Student Name",
        "class_name": "Class",
        "gender": "Gender",
        "average_marks": "Average Score",
        "attendance": "Attendance (%)"
    }
)

recent_students["Average Score"] = (
    recent_students["Average Score"].round(1)
)

recent_students["Attendance (%)"] = (
    recent_students["Attendance (%)"].round(1)
)

st.dataframe(
    recent_students,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# QUICK ACTIONS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">WORKSPACE</div>',
    unsafe_allow_html=True
)

st.subheader("Quick Actions")


actions = [
    (
        "Student Records",
        "Browse and manage student information.",
        "pages/1_Student_Records.py",
        ":material/school:"
    ),
    (
        "Academic Analytics",
        "Explore subject and class performance.",
        "pages/2_Academic_Analytics.py",
        ":material/analytics:"
    ),
    (
        "Performance Prediction",
        "Estimate student academic performance.",
        "pages/3_Performance_Prediction.py",
        ":material/psychology:"
    ),
    (
        "Personalized Recommendations",
        "View individual academic guidance.",
        "pages/4_Personalized_Recommendations.py",
        ":material/lightbulb:"
    ),
    (
        "Student Risk Detection",
        "Identify students who may need support.",
        "pages/5_Student_Risk_Detection.py",
        ":material/health_and_safety:"
    ),
    (
        "Automated Reports",
        "Generate downloadable student reports.",
        "pages/6_Automated_Reports.py",
        ":material/description:"
    )
]


action_columns = st.columns(
    3,
    gap="large"
)

for index, action in enumerate(actions):

    with action_columns[index % 3]:

        with st.container(border=True):

            st.markdown(
                f"**{action[0]}**"
            )

            st.caption(
                action[1]
            )

            st.page_link(
                action[2],
                label=f"Open {action[0]}",
                icon=action[3]
            )


# =========================================================
# FOOTER
# =========================================================

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
        EduAnalytics · Student Performance Intelligence
    </div>
    """,
    unsafe_allow_html=True
)

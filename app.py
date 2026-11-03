
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_utils import load_data, apply_styles, show_sidebar


# PAGE CONFIGURATION

st.set_page_config(
    page_title="EduAnalytics | Dashboard",
    page_icon="E",
    layout="wide"
)

apply_styles()

df = load_data()
show_sidebar()


# CONSTANTS

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


# CHART STYLING

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
        showlegend=False,
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


# DASHBOARD HEADER

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


# KEY PERFORMANCE INDICATORS

total_students = len(df)

average_score = df["average_marks"].mean()

pass_rate = (
    (df["average_marks"] >= 40).sum() / total_students * 100
    if total_students > 0 else 0
)

average_attendance = df["attendance"].mean()

st.markdown(
    '<div class="eyebrow">KEY PERFORMANCE INDICATORS</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Students", f"{total_students:,}")

with k2:
    st.metric("Average Score", f"{average_score:.1f}/100")

with k3:
    st.metric("Pass Rate", f"{pass_rate:.1f}%")

with k4:
    st.metric("Attendance", f"{average_attendance:.1f}%")


st.markdown("<br>", unsafe_allow_html=True)


# SUBJECT-WISE PERFORMANCE

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

subject_averages.columns = ["Subject", "Average Marks"]

# Horizontal bar chart for better readability
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
        categoryarray=[
            "Computer",
            "Social Science",
            "English",
            "Science",
            "Mathematics"
        ],
        title=None
    ),
    xaxis=dict(
        title=None,
        range=[
            0,
            max(100, subject_averages["Average Marks"].max() + 12)
        ]
    ),
    showlegend=False
)

fig_subjects = style_chart(fig_subjects, height=370)

# Reapply axis settings after common styling
fig_subjects.update_xaxes(
    title=None,
    range=[
        0,
        max(100, subject_averages["Average Marks"].max() + 12)
    ],
    showgrid=True,
    gridcolor=GRID_COLOR
)

fig_subjects.update_yaxes(
    title=None,
    showgrid=False,
    categoryorder="array",
    categoryarray=[
        "Computer",
        "Social Science",
        "English",
        "Science",
        "Mathematics"
    ]
)

st.plotly_chart(
    fig_subjects,
    use_container_width=True,
    config={"displayModeBar": False}
)


# CLASS PERFORMANCE AND PASS DISTRIBUTION

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns(2, gap="large")


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

    fig_class.update_xaxes(title=None)

    fig_class.update_yaxes(
        title=None,
        range=[
            0,
            max(100, class_average["average_marks"].max() + 12)
        ]
    )

    fig_class = style_chart(fig_class, height=330)

    st.plotly_chart(
        fig_class,
        use_container_width=True,
        config={"displayModeBar": False}
    )


with right_col:

    st.subheader("Pass Distribution")

    pass_counts = df["average_marks"].apply(
        lambda score: "Passed" if score >= 40 else "Failed"
    ).value_counts()

    passed = int(pass_counts.get("Passed", 0))
    failed = int(pass_counts.get("Failed", 0))

    fig_pass = go.Figure(
        data=[
            go.Pie(
                labels=["Passed", "Failed"],
                values=[passed, failed],
                hole=0.68,
                marker=dict(
                    colors=["#52745A", "#C4A779"],
                    line=dict(color="white", width=4)
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
        margin=dict(l=15, r=15, t=25, b=45)
    )

    fig_pass = style_chart(fig_pass, height=350)

    # Restore donut legend after common chart styling
    fig_pass.update_layout(
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
        margin=dict(l=15, r=15, t=25, b=45)
    )

    st.plotly_chart(
        fig_pass,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ATTENDANCE ANALYSIS

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

fig_attendance.update_xaxes(title="Attendance (%)")
fig_attendance.update_yaxes(title="Number of Students")

fig_attendance = style_chart(fig_attendance, height=320)

st.plotly_chart(
    fig_attendance,
    use_container_width=True,
    config={"displayModeBar": False}
)


# RECENT STUDENT RECORDS

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

recent_students = df[display_columns].head(8).copy()

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


# FOOTER

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
        EduAnalytics · Student Performance Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

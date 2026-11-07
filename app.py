import html
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
    LOGO_PATH,
)
from risk_engine import assess_student_risk


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EduAnalytics | Dashboard",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "E",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
show_sidebar()


# ============================================================
# DASHBOARD STYLING
# ============================================================

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.15rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 1800px !important;
}

.topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #243451;
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.35rem 0 1rem 0;
    border-bottom: 1px solid #E3E8F2;
    margin-bottom: 1.25rem;
}

.page-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: #243451;
    letter-spacing: -0.8px;
    margin: 0 0 0.25rem 0;
}

.page-description {
    color: #7C879C;
    font-size: 0.82rem;
    margin-bottom: 1.2rem;
}

.section-heading {
    color: #243451;
    font-family: 'Manrope', sans-serif;
    font-size: 1rem;
    font-weight: 750;
    margin-bottom: 0.75rem;
}

.section-caption {
    color: #8792A5;
    font-size: 0.72rem;
    margin-top: -0.45rem;
    margin-bottom: 0.8rem;
}

.metric-card {
    min-height: 112px;
    padding: 15px 16px;
    border-radius: 15px;
    border: 1px solid #E3E8F2;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-label {
    font-size: 0.75rem;
    color: #52617A;
    font-weight: 600;
}

.metric-value {
    color: #243451;
    font-family: 'Manrope', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    letter-spacing: -0.7px;
    margin-top: 9px;
}

.metric-note {
    font-size: 0.69rem;
    color: #73819A;
    margin-top: 3px;
}

.insight-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 11px 10px;
    border: 1px solid #E7EBF3;
    border-radius: 11px;
    margin-bottom: 9px;
    background: #FAFBFE;
}

.insight-marker {
    width: 29px;
    height: 29px;
    min-width: 29px;
    border-radius: 9px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.75rem;
    font-weight: 800;
}

.insight-title {
    color: #26334D;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 1.4;
}

.insight-description {
    color: #8792A5;
    font-size: 0.67rem;
    margin-top: 3px;
    line-height: 1.4;
}

.student-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    align-items: center;
    padding: 10px 2px;
    border-bottom: 1px solid #EDF0F5;
}

.student-name {
    color: #26334D;
    font-size: 0.75rem;
    font-weight: 650;
}

.student-detail {
    color: #8792A5;
    font-size: 0.66rem;
    margin-top: 2px;
}

.risk-pill {
    font-size: 0.63rem;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 20px;
    white-space: nowrap;
}

.risk-high {
    color: #C34E5B;
    background: #FCEBED;
}

.risk-moderate {
    color: #A97822;
    background: #FFF4DD;
}

.panel-note {
    font-size: 0.69rem;
    color: #8792A5;
    line-height: 1.5;
    margin-top: 10px;
}

.legend-item {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    margin: 10px 0;
}

.legend-dot {
    width: 9px;
    height: 9px;
    min-width: 9px;
    border-radius: 50%;
    margin-top: 3px;
}

.legend-label {
    color: #52617A;
    font-size: 0.65rem;
    line-height: 1.3;
}

.legend-value {
    color: #243451;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 2px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
    border-color: #E3E8F2;
    background: #FFFFFF;
    box-shadow: 0 3px 12px rgba(36, 52, 81, 0.035);
}

[data-testid="stPlotlyChart"] {
    margin-top: -5px;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    .page-heading {
        font-size: 1.4rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

df = load_data()

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
    *SUBJECT_COLUMNS,
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Missing required dataset columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ============================================================
# CALCULATE RISK ASSESSMENTS
# ============================================================

risk_records = []

for _, student in df.iterrows():

    result = assess_student_risk(student)

    risk_records.append({
        "student_id": student["student_id"],
        "name": student["name"],
        "class_name": student["class_name"],
        "average_marks": student["average_marks"],
        "attendance": student["attendance"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "risk_factors": result["risk_factors"],
    })


risk_df = pd.DataFrame(risk_records)


# ============================================================
# DASHBOARD METRICS
# ============================================================

total_students = len(df)

average_score = float(df["average_marks"].mean())

average_attendance = float(df["attendance"].mean())

pass_count = int(
    (df["average_marks"] >= 40).sum()
)

pass_rate = (
    pass_count / total_students * 100
    if total_students else 0
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

low_attendance_count = int(
    (df["attendance"] < 75).sum()
)

below_pass_count = int(
    (df["average_marks"] < 40).sum()
)


# ============================================================
# TOP NAVIGATION AND PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <span style="font-size:1.05rem;">Dashboard</span>
        <span style="color:#B8C1D1;">/</span>
        <span style="color:#8792A5;font-weight:500;">
            Overview
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

header_col, search_col = st.columns(
    [1.8, 1],
    vertical_alignment="center",
)

with header_col:

    st.markdown(
        '<div class="page-heading">Dashboard Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-description">
            Monitor academic performance, identify students
            needing support, and explore learning outcomes.
        </div>
        """,
        unsafe_allow_html=True,
    )

with search_col:

    search_query = st.text_input(
        "Search students",
        placeholder="Search student name or ID...",
        label_visibility="collapsed",
        key="dashboard_student_search",
    )


# ============================================================
# SEARCH RESULTS
# ============================================================

if search_query.strip():

    search_results = df[
        df["name"].astype(str).str.contains(
            search_query,
            case=False,
            na=False,
        )
        |
        df["student_id"].astype(str).str.contains(
            search_query,
            case=False,
            na=False,
        )
    ]

    if search_results.empty:
        st.info("No matching student records found.")

    else:

        st.markdown("**Matching student records**")

        st.dataframe(
            search_results[
                [
                    "student_id",
                    "name",
                    "class_name",
                    "average_marks",
                    "attendance",
                ]
            ].rename(
                columns={
                    "student_id": "Student ID",
                    "name": "Student",
                    "class_name": "Class",
                    "average_marks": "Average Marks",
                    "attendance": "Attendance",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# MAIN DASHBOARD AND RIGHT PANEL
# ============================================================

main_column, side_column = st.columns(
    [7.25, 2.75],
    gap="medium",
)


# ============================================================
# MAIN DASHBOARD CONTENT
# ============================================================

with main_column:

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    metric_columns = st.columns(4, gap="small")

    metric_data = [
        {
            "label": "Total Students",
            "value": f"{total_students:,}",
            "note": "Registered student records",
            "background": "#E5F3FC",
        },
        {
            "label": "Average Marks",
            "value": f"{average_score:.1f}%",
            "note": f"{pass_rate:.1f}% meeting pass mark",
            "background": "#E9EDFC",
        },
        {
            "label": "At-Risk Students",
            "value": f"{high_risk_count}",
            "note": "High-risk classification",
            "background": "#E4F3FC",
        },
        {
            "label": "Average Attendance",
            "value": f"{average_attendance:.1f}%",
            "note": f"{low_attendance_count} below 75% attendance",
            "background": "#EEEFFD",
        },
    ]

    for column, metric in zip(metric_columns, metric_data):

        with column:

            st.markdown(
                f"""
                <div class="metric-card"
                     style="background:{metric['background']};">
                    <div class="metric-label">
                        {metric['label']}
                    </div>
                    <div>
                        <div class="metric-value">
                            {metric['value']}
                        </div>
                        <div class="metric-note">
                            {metric['note']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # PERFORMANCE AND SUBJECT PERFORMANCE
    # --------------------------------------------------------

    performance_column, subject_column = st.columns(
        [1.85, 1],
        gap="small",
    )


    # STUDENT PERFORMANCE PROFILE

    with performance_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-heading">Student Performance Overview</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="section-caption">
                    Student average marks, ordered from lowest to highest
                </div>
                """,
                unsafe_allow_html=True,
            )

            sorted_scores = (
                df["average_marks"]
                .sort_values()
                .reset_index(drop=True)
            )

            student_positions = list(
                range(1, len(sorted_scores) + 1)
            )

            fig_performance = go.Figure()

            fig_performance.add_trace(
                go.Scatter(
                    x=student_positions,
                    y=sorted_scores,
                    mode="lines",
                    name="Student average",
                    line=dict(
                        color="#5C7CFA",
                        width=3,
                        shape="spline",
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(92,124,250,0.08)",
                    hovertemplate=(
                        "Student rank: %{x}<br>"
                        "Average marks: %{y:.1f}%"
                        "<extra></extra>"
                    ),
                )
            )

            fig_performance.add_hline(
                y=40,
                line_dash="dash",
                line_color="#E5A94B",
                annotation_text="Pass mark",
                annotation_position="bottom right",
                annotation_font_size=10,
                annotation_font_color="#A97822",
            )

            fig_performance.update_layout(
                height=265,
                margin=dict(l=5, r=10, t=10, b=5),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="DM Sans",
                    color="#52617A",
                    size=10,
                ),
                hovermode="x unified",
            )

            fig_performance.update_xaxes(
                title=None,
                showgrid=False,
                showline=True,
                linecolor="#E3E8F2",
                tickfont=dict(size=9),
                nticks=6,
            )

            fig_performance.update_yaxes(
                title=None,
                range=[0, 100],
                ticksuffix="%",
                gridcolor="#E9EDF5",
                zeroline=False,
                tickfont=dict(size=9),
            )

            st.plotly_chart(
                fig_performance,
                use_container_width=True,
                config={"displayModeBar": False},
            )


    # SUBJECT PERFORMANCE

    with subject_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-heading">Subject Performance</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="section-caption">
                    Average marks by subject
                </div>
                """,
                unsafe_allow_html=True,
            )

            subject_averages = (
                df[SUBJECT_COLUMNS]
                .mean()
                .rename(index=SUBJECT_NAMES)
                .reset_index()
            )

            subject_averages.columns = [
                "Subject",
                "Average",
            ]

            subject_averages = subject_averages.sort_values(
                "Average",
                ascending=True,
            )

            subject_colors = [
                "#A8B6FF",
                "#8BCDEB",
                "#B6D8F5",
                "#5C7CFA",
                "#8DD9B5",
            ]

            fig_subjects = go.Figure()

            for index, row in enumerate(
                subject_averages.itertuples(index=False)
            ):

                fig_subjects.add_trace(
                    go.Bar(
                        x=[row.Average],
                        y=[row.Subject],
                        orientation="h",
                        marker_color=subject_colors[
                            index % len(subject_colors)
                        ],
                        width=0.48,
                        showlegend=False,
                        text=[f"{row.Average:.1f}%"],
                        textposition="outside",
                        textfont=dict(
                            size=10,
                            color="#52617A",
                        ),
                        hovertemplate=(
                            "%{y}<br>"
                            "Average: %{x:.1f}%"
                            "<extra></extra>"
                        ),
                    )
                )

            fig_subjects.update_layout(
                height=265,
                margin=dict(l=0, r=28, t=8, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="DM Sans",
                    color="#52617A",
                    size=9,
                ),
                barmode="overlay",
            )

            fig_subjects.update_xaxes(
                range=[0, 115],
                visible=False,
                fixedrange=True,
            )

            fig_subjects.update_yaxes(
                title=None,
                showgrid=False,
                tickfont=dict(size=9),
                automargin=True,
            )

            st.plotly_chart(
                fig_subjects,
                use_container_width=True,
                config={"displayModeBar": False},
            )


    # --------------------------------------------------------
    # CLASS PERFORMANCE AND STUDENT DISTRIBUTION
    # --------------------------------------------------------

    class_column, distribution_column = st.columns(
        [1, 1.25],
        gap="small",
    )


    # CLASS PERFORMANCE

    with class_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-heading">Performance by Class</div>',
                unsafe_allow_html=True,
            )

            class_data = (
                df.groupby("class_name")["average_marks"]
                .mean()
                .reset_index()
                .sort_values("class_name")
            )

            fig_class = px.bar(
                class_data,
                x="class_name",
                y="average_marks",
                color="class_name",
                color_discrete_sequence=[
                    "#A8B6FF",
                    "#5C7CFA",
                    "#8BCDEB",
                    "#B6D8F5",
                    "#8DD9B5",
                ],
                text_auto=".1f",
            )

            fig_class.update_traces(
                marker_line_width=0,
                textposition="outside",
                cliponaxis=False,
                textfont=dict(
                    size=10,
                    color="#52617A",
                ),
            )

            fig_class.update_layout(
                height=245,
                showlegend=False,
                margin=dict(l=5, r=12, t=20, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="DM Sans",
                    color="#52617A",
                    size=10,
                ),
            )

            fig_class.update_xaxes(
                title=None,
                showgrid=False,
                tickfont=dict(size=9),
            )

            fig_class.update_yaxes(
                title=None,
                range=[
                    0,
                    max(
                        100,
                        float(
                            class_data["average_marks"].max()
                        ) + 15,
                    ),
                ],
                gridcolor="#E9EDF5",
                ticksuffix="%",
                tickfont=dict(size=9),
            )

            st.plotly_chart(
                fig_class,
                use_container_width=True,
                config={"displayModeBar": False},
            )


    # STUDENT DISTRIBUTION

    with distribution_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-heading">Student Distribution by Performance</div>',
                unsafe_allow_html=True,
            )

            excellent_count = int(
                (df["average_marks"] >= 80).sum()
            )

            good_count = int(
                (
                    (df["average_marks"] >= 60)
                    & (df["average_marks"] < 80)
                ).sum()
            )

            average_count = int(
                (
                    (df["average_marks"] >= 40)
                    & (df["average_marks"] < 60)
                ).sum()
            )

            support_count = int(
                (df["average_marks"] < 40).sum()
            )

            distribution_data = pd.DataFrame({
                "Category": [
                    "Excellent (80%+)",
                    "Good (60–79%)",
                    "Average (40–59%)",
                    "Needs Support (<40%)",
                ],
                "Students": [
                    excellent_count,
                    good_count,
                    average_count,
                    support_count,
                ],
            })

            distribution_colors = [
                "#5C7CFA",
                "#A8B6FF",
                "#8BCDEB",
                "#8DD9B5",
            ]

            fig_distribution = go.Figure(
                data=[
                    go.Pie(
                        labels=distribution_data["Category"],
                        values=distribution_data["Students"],
                        hole=0.67,
                        sort=False,
                        marker=dict(
                            colors=distribution_colors,
                            line=dict(
                                color="#FFFFFF",
                                width=3,
                            ),
                        ),
                        textinfo="none",
                        hovertemplate=(
                            "%{label}<br>"
                            "Students: %{value}<br>"
                            "Share: %{percent}"
                            "<extra></extra>"
                        ),
                    )
                ]
            )

            fig_distribution.update_layout(
                height=245,
                margin=dict(l=0, r=0, t=5, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                annotations=[
                    dict(
                        text=(
                            f"<b>{total_students}</b>"
                            "<br><span style='font-size:10px'>Students</span>"
                        ),
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(
                            family="Manrope",
                            size=19,
                            color="#243451",
                        ),
                    )
                ],
            )

            donut_col, legend_col = st.columns(
                [1, 1.2],
                vertical_alignment="center",
            )

            with donut_col:

                st.plotly_chart(
                    fig_distribution,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            with legend_col:

                for index, row in enumerate(
                    distribution_data.itertuples(index=False)
                ):

                    percentage = (
                        row.Students / total_students * 100
                        if total_students else 0
                    )

                    # Build HTML without indentation at the start
                    # of the string to prevent Markdown code rendering.

                    legend_html = (
                        '<div class="legend-item">'
                        f'<span class="legend-dot" '
                        f'style="background:{distribution_colors[index]};">'
                        '</span>'
                        '<div>'
                        f'<div class="legend-label">{html.escape(row.Category)}</div>'
                        f'<div class="legend-value">'
                        f'{row.Students} students ({percentage:.1f}%)'
                        '</div>'
                        '</div>'
                        '</div>'
                    )

                    st.markdown(
                        legend_html,
                        unsafe_allow_html=True,
                    )


    # --------------------------------------------------------
    # TOP PERFORMING STUDENTS
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="section-heading">Top Performing Students</div>',
            unsafe_allow_html=True,
        )

        top_students = (
            df.sort_values(
                "average_marks",
                ascending=False,
            )[
                [
                    "student_id",
                    "name",
                    "class_name",
                    "average_marks",
                    "attendance",
                ]
            ]
            .head(5)
            .copy()
        )

        top_students = top_students.rename(
            columns={
                "student_id": "Student ID",
                "name": "Student",
                "class_name": "Class",
                "average_marks": "Average Marks",
                "attendance": "Attendance (%)",
            }
        )

        top_students["Average Marks"] = (
            top_students["Average Marks"].round(1)
        )

        top_students["Attendance (%)"] = (
            top_students["Attendance (%)"].round(1)
        )

        st.dataframe(
            top_students,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# RIGHT-HAND INFORMATION PANEL
# ============================================================

with side_column:

    # --------------------------------------------------------
    # ACADEMIC INSIGHTS AND ALERTS
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="section-heading">Academic Insights & Alerts</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="insight-item">
                <div class="insight-marker"
                     style="background:#FCEBED;color:#D65D67;">
                    !
                </div>
                <div>
                    <div class="insight-title">
                        {high_risk_count} high-risk students
                    </div>
                    <div class="insight-description">
                        May need immediate academic support.
                    </div>
                </div>
            </div>

            <div class="insight-item">
                <div class="insight-marker"
                     style="background:#FFF4DD;color:#B9852F;">
                    !
                </div>
                <div>
                    <div class="insight-title">
                        {low_attendance_count} students below 75% attendance
                    </div>
                    <div class="insight-description">
                        Attendance follow-up may be useful.
                    </div>
                </div>
            </div>

            <div class="insight-item">
                <div class="insight-marker"
                     style="background:#E8F1FC;color:#5279D8;">
                    i
                </div>
                <div>
                    <div class="insight-title">
                        {below_pass_count} students below 40 average marks
                    </div>
                    <div class="insight-description">
                        Consider targeted academic support.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        best_subject = (
            df[SUBJECT_COLUMNS]
            .mean()
            .idxmax()
        )

        best_subject_name = SUBJECT_NAMES[best_subject]

        best_subject_average = float(
            df[best_subject].mean()
        )

        st.markdown(
            f"""
            <div class="insight-item">
                <div class="insight-marker"
                     style="background:#E5F6EE;color:#328B69;">
                    +
                </div>
                <div>
                    <div class="insight-title">
                        Strongest subject: {best_subject_name}
                    </div>
                    <div class="insight-description">
                        Average performance: {best_subject_average:.1f}%.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # STUDENTS REQUIRING ATTENTION
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="section-heading">Students Requiring Attention</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="section-caption">
                Based on the current risk assessment
            </div>
            """,
            unsafe_allow_html=True,
        )

        attention_students = (
            risk_df[
                risk_df["risk_level"].isin(
                    ["High", "Moderate"]
                )
            ]
            .sort_values(
                ["risk_score", "average_marks"],
                ascending=[False, True],
            )
            .head(6)
        )

        if attention_students.empty:

            st.markdown(
                """
                <div class="panel-note">
                    No students currently appear in the high
                    or moderate risk groups.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            for _, student in attention_students.iterrows():

                name = html.escape(str(student["name"]))
                class_name = html.escape(str(student["class_name"]))
                risk_level = str(student["risk_level"])

                risk_class = (
                    "risk-high"
                    if risk_level == "High"
                    else "risk-moderate"
                )

                st.markdown(
                    f"""
                    <div class="student-row">
                        <div>
                            <div class="student-name">{name}</div>
                            <div class="student-detail">
                                Class {class_name}
                                · {student['average_marks']:.1f}% average
                            </div>
                        </div>
                        <span class="risk-pill {risk_class}">
                            {risk_level}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown(
            """
            <div class="panel-note">
                Risk categories use the project's current
                rule-based assessment and are intended as
                initial support indicators.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # ACADEMIC SNAPSHOT
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="section-heading">Academic Snapshot</div>',
            unsafe_allow_html=True,
        )

        st.metric(
            "Pass Rate",
            f"{pass_rate:.1f}%",
        )

        st.metric(
            "Moderate Risk",
            moderate_risk_count,
        )

        st.metric(
            "Low Risk",
            low_risk_count,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#9AA4B6;
        font-size:0.74rem;
        padding:1.5rem 0 0.5rem 0;
        border-top:1px solid #E3E8F2;
        margin-top:2rem;
    ">
        EduAnalytics · Student Performance Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)

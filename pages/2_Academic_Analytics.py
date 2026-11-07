
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import (
    load_data, apply_styles, show_sidebar,
    SUBJECT_COLUMNS, SUBJECT_NAMES
)

st.set_page_config(
    page_title="Academic Analytics | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()
show_sidebar()

st.markdown("""
<style>
.stApp { background:#F4F6FC; color:#243451; }
h1,h2,h3 { color:#243451 !important; font-family:Manrope,sans-serif; }
.page-eyebrow {
    color:#5C7CFA; font-size:.68rem; font-weight:800;
    letter-spacing:1.5px; margin-bottom:7px;
}
.page-subtitle { color:#8792A5; font-size:.86rem; margin-bottom:18px; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:14px; box-shadow:0 3px 12px rgba(36,52,81,.035);
}
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:13px; padding:15px;
}
[data-testid="stMetricLabel"] { color:#73819A; }
[data-testid="stMetricValue"] { color:#243451; font-family:Manrope,sans-serif; }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# DATA VALIDATION
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records found. Check data/students.csv.")
    st.stop()

required = [
    "student_id", "class_name", "average_marks",
    "attendance", *SUBJECT_COLUMNS
]
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing required columns: {', '.join(missing)}")
    st.stop()


# ------------------------------------------------------------
# CHART HELPER
# ------------------------------------------------------------

PALETTE = [
    "#5C7CFA", "#A8B6FF", "#8BCDEB",
    "#B6D8F5", "#8DD9B5"
]

def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#52617A", size=11),
        margin=dict(l=12, r=20, t=20, b=15),
        hoverlabel=dict(
            bgcolor="white",
            font_family="DM Sans",
            font_size=12
        )
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#E3E8F2",
        tickfont=dict(color="#73819A")
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E9EDF5",
        zeroline=False,
        tickfont=dict(color="#73819A")
    )
    return fig


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">WORKSPACE / ANALYTICS</div>',
            unsafe_allow_html=True)
st.title("Academic Analytics")
st.markdown(
    '<div class="page-subtitle">Understand academic performance, '
    'attendance patterns, and classroom outcomes.</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# KPI OVERVIEW
# ------------------------------------------------------------

total_students = len(df)
average_score = float(df["average_marks"].mean())
pass_rate = float((df["average_marks"] >= 40).mean() * 100)
average_attendance = float(df["attendance"].mean())

st.markdown('<div class="page-eyebrow">AT A GLANCE</div>',
            unsafe_allow_html=True)
st.subheader("Academic Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", f"{total_students:,}")
c2.metric("Average Score", f"{average_score:.1f}/100")
c3.metric("Pass Rate", f"{pass_rate:.1f}%")
c4.metric("Attendance", f"{average_attendance:.1f}%")


# ------------------------------------------------------------
# SUBJECT PERFORMANCE
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">SUBJECT ANALYSIS</div>',
            unsafe_allow_html=True)
st.subheader("Subject-wise Performance")
st.caption("Compare average marks across all five academic subjects.")

subject_data = pd.DataFrame({
    "Subject": [SUBJECT_NAMES[col] for col in SUBJECT_COLUMNS],
    "Average Marks": [df[col].mean() for col in SUBJECT_COLUMNS]
}).sort_values("Average Marks", ascending=True)

with st.container(border=True):
    fig = px.bar(
        subject_data,
        x="Average Marks",
        y="Subject",
        orientation="h",
        color="Subject",
        text_auto=".1f",
        color_discrete_sequence=PALETTE
    )
    fig.update_traces(
        textposition="outside", cliponaxis=False,
        marker_line_width=0
    )
    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="Average Marks", range=[0, 115],
                   gridcolor="#E9EDF5"),
        yaxis=dict(title=None, showgrid=False),
        bargap=.35
    )
    fig = style_chart(fig, 360)
    fig.update_xaxes(range=[0, 115], title="Average Marks",
                     showgrid=True, gridcolor="#E9EDF5")
    fig.update_yaxes(title=None, showgrid=False)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


# ------------------------------------------------------------
# MARKS AND ATTENDANCE DISTRIBUTIONS
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">DISTRIBUTION ANALYSIS</div>',
            unsafe_allow_html=True)
st.subheader("Student Distribution")

left, right = st.columns(2, gap="medium")

with left:
    with st.container(border=True):
        st.markdown("**Average Marks Distribution**")
        fig_marks = px.histogram(
            df, x="average_marks", nbins=15,
            color_discrete_sequence=["#5C7CFA"],
            labels={
                "average_marks": "Average Marks",
                "count": "Number of Students"
            }
        )
        fig_marks.update_traces(
            marker_line_color="white", marker_line_width=1
        )
        fig_marks = style_chart(fig_marks, 310)
        fig_marks.update_layout(
            xaxis_title="Average Marks",
            yaxis_title="Number of Students"
        )
        st.plotly_chart(fig_marks, use_container_width=True,
                        config={"displayModeBar": False})

with right:
    with st.container(border=True):
        st.markdown("**Attendance Distribution**")
        fig_attendance = px.histogram(
            df, x="attendance", nbins=15,
            color_discrete_sequence=["#8BCDEB"],
            labels={
                "attendance": "Attendance Percentage",
                "count": "Number of Students"
            }
        )
        fig_attendance.update_traces(
            marker_line_color="white", marker_line_width=1
        )
        fig_attendance = style_chart(fig_attendance, 310)
        fig_attendance.update_layout(
            xaxis_title="Attendance (%)",
            yaxis_title="Number of Students"
        )
        st.plotly_chart(fig_attendance, use_container_width=True,
                        config={"displayModeBar": False})


# ------------------------------------------------------------
# CLASS-WISE SUBJECT PERFORMANCE
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">CLASS COMPARISON</div>',
            unsafe_allow_html=True)
st.subheader("Class-wise Subject Performance")
st.caption("Compare average marks by class across all five subjects.")

class_subject_data = df.melt(
    id_vars=["class_name"],
    value_vars=SUBJECT_COLUMNS,
    var_name="Subject",
    value_name="Marks"
)
class_subject_data["Subject"] = class_subject_data["Subject"].map(
    SUBJECT_NAMES
)

class_performance = (
    class_subject_data
    .groupby(["class_name", "Subject"], as_index=False)["Marks"]
    .mean()
)

with st.container(border=True):
    fig_class = px.bar(
        class_performance,
        x="class_name",
        y="Marks",
        color="Subject",
        barmode="group",
        text_auto=".1f",
        color_discrete_sequence=PALETTE,
        labels={
            "class_name": "Class",
            "Marks": "Average Marks",
            "Subject": "Subject"
        }
    )
    fig_class.update_traces(
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False
    )
    fig_class.update_layout(
        yaxis=dict(title="Average Marks", range=[0, 115],
                   gridcolor="#E9EDF5"),
        xaxis=dict(title="Class"),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        bargap=.2,
        bargroupgap=.08
    )
    fig_class = style_chart(fig_class, 420)
    fig_class.update_yaxes(
        title="Average Marks", range=[0, 115],
        showgrid=True, gridcolor="#E9EDF5"
    )
    st.plotly_chart(fig_class, use_container_width=True,
                    config={"displayModeBar": False})


# ------------------------------------------------------------
# CLASS SUMMARY TABLE
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">CLASS INSIGHTS</div>',
            unsafe_allow_html=True)
st.subheader("Class Performance Summary")

class_summary = (
    df.groupby("class_name")
    .agg(
        Total_Students=("student_id", "count"),
        Average_Score=("average_marks", "mean"),
        Average_Attendance=("attendance", "mean")
    )
    .reset_index()
    .rename(columns={
        "class_name": "Class",
        "Total_Students": "Total Students",
        "Average_Score": "Average Score (%)",
        "Average_Attendance": "Average Attendance (%)"
    })
)

class_summary["Average Score (%)"] = (
    class_summary["Average Score (%)"].round(1)
)
class_summary["Average Attendance (%)"] = (
    class_summary["Average Attendance (%)"].round(1)
)

with st.container(border=True):
    st.dataframe(
        class_summary,
        use_container_width=True,
        hide_index=True,
        height=220
    )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Academic Analytics & Performance Insights
</div>
""", unsafe_allow_html=True)

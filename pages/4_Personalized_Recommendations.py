
import html
import streamlit as st

from data_utils import load_data, apply_styles, show_sidebar
from recommendation_engine import (
    generate_recommendations,
    get_recommendation_summary,
)

st.set_page_config(
    page_title="Personalized Recommendations | EduAnalytics",
    page_icon="E",
    layout="wide",
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
.panel-title { color:#243451; font-size:1rem; font-weight:750; }
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
.priority-card {
    border:1px solid #E5EAF3; border-radius:12px;
    padding:17px; background:#FFFFFF; min-height:100px;
}
.priority-label { color:#73819A; font-size:.74rem; font-weight:650; }
.priority-number {
    font-family:Manrope,sans-serif; font-size:1.65rem;
    font-weight:800; color:#243451; margin-top:7px;
}
.recommendation-observation {
    color:#73819A; font-size:.78rem; line-height:1.55;
}
.recommendation-action {
    color:#34435E; font-size:.82rem; line-height:1.6;
    margin-top:9px;
}
.priority-pill {
    display:inline-block; padding:5px 10px;
    border-radius:20px; font-size:.66rem; font-weight:750;
}
.stButton button,.stDownloadButton button {
    background:#5C7CFA; color:white; border:1px solid #5C7CFA;
    border-radius:9px; font-weight:650;
}
.stButton button:hover,.stDownloadButton button:hover {
    background:#4969E6; color:white; border-color:#4969E6;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">INTELLIGENCE / STUDENT SUPPORT</div>',
    unsafe_allow_html=True,
)
st.title("Personalized Recommendations")
st.markdown(
    '<div class="page-subtitle">Turn academic observations into '
    'clear, actionable support plans for individual students.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# STUDENT SELECTION
# ------------------------------------------------------------

with st.container(border=True):
    st.markdown(
        '<div class="panel-title">Select a Student</div>',
        unsafe_allow_html=True,
    )
    st.caption("Choose a student to generate an individual action plan.")

    student_options = {
        f"{row['name']} ({row['student_id']})": row["student_id"]
        for _, row in df.iterrows()
    }

    selected_student = st.selectbox(
        "Student",
        options=list(student_options.keys()),
        label_visibility="collapsed",
    )

student_id = student_options[selected_student]

student = df[
    df["student_id"] == student_id
].iloc[0]


# ------------------------------------------------------------
# STUDENT OVERVIEW
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">STUDENT PROFILE</div>',
    unsafe_allow_html=True,
)
st.subheader("Student Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Student", student["name"])
c2.metric("Class", student["class_name"])
c3.metric("Average Marks", f"{student['average_marks']:.1f}%")
c4.metric("Attendance", f"{student['attendance']:.1f}%")


# ------------------------------------------------------------
# GENERATE RECOMMENDATIONS
# ------------------------------------------------------------

recommendations = generate_recommendations(student)
summary = get_recommendation_summary(recommendations)


# ------------------------------------------------------------
# PRIORITY SUMMARY
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">ACTION PLAN SUMMARY</div>',
    unsafe_allow_html=True,
)
st.subheader("Recommendation Overview")

summary_columns = st.columns(4)

summary_cards = [
    ("Total Recommendations", summary["total"], "#E9EDFC"),
    ("High Priority", summary["high"], "#FCEBED"),
    ("Medium Priority", summary["medium"], "#FFF4DD"),
    ("Low Priority", summary["low"], "#E5F6EE"),
]

for column, (label, value, background) in zip(
    summary_columns, summary_cards
):
    with column:
        st.markdown(
            f"""
            <div class="priority-card" style="background:{background};">
                <div class="priority-label">{label}</div>
                <div class="priority-number">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------
# PERSONALIZED ACTION PLAN
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">PERSONALIZED GUIDANCE</div>',
    unsafe_allow_html=True,
)
st.subheader("Recommended Actions")

if not recommendations:
    st.success(
        "No specific recommendations at this time. "
        "Continue monitoring the student's academic progress."
    )

else:
    priority_styles = {
        "High": {
            "color": "#C34E5B",
            "background": "#FCEBED",
        },
        "Medium": {
            "color": "#A97822",
            "background": "#FFF4DD",
        },
        "Low": {
            "color": "#328B69",
            "background": "#E5F6EE",
        },
    }

    for index, item in enumerate(recommendations, start=1):

        priority = item["priority"]
        style = priority_styles.get(
            priority,
            priority_styles["Low"],
        )

        with st.container(border=True):
            left, right = st.columns([5, 1])

            with left:
                st.markdown(
                    f"**{index:02d}  {item['category']}**"
                )
                st.markdown(
                    f'<div class="recommendation-observation">'
                    f'{html.escape(str(item["observation"]))}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="recommendation-action">'
                    f'<strong>Suggested action:</strong> '
                    f'{html.escape(str(item["recommendation"]))}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with right:
                st.markdown(
                    f"""
                    <div style="text-align:right;padding-top:5px;">
                        <span class="priority-pill"
                        style="color:{style['color']};
                        background:{style['background']};">
                            {html.escape(str(priority))} Priority
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ------------------------------------------------------------
# DOWNLOAD REPORT
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">EXPORT / STUDENT GUIDANCE</div>',
    unsafe_allow_html=True,
)
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
    "",
]

for index, item in enumerate(recommendations, start=1):
    report_lines.extend([
        f"{index}. {item['category']} - {item['priority']} Priority",
        f"Observation: {item['observation']}",
        f"Recommendation: {item['recommendation']}",
        "",
    ])

report_text = "\n".join(report_lines)

safe_student_id = "".join(
    character for character in str(student_id)
    if character.isalnum() or character in ("-", "_")
)

with st.container(border=True):
    st.markdown("**Recommendation report**")
    st.caption(
        "Export the selected student's profile and personalized action plan."
    )

    st.download_button(
        label="Download Recommendation Report",
        data=report_text,
        file_name=f"recommendations_{safe_student_id}.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.caption(
    "Recommendations are rule-based guidance using configurable "
    "thresholds. They should support teacher judgement, not replace it."
)

st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Personalized Student Support
</div>
""", unsafe_allow_html=True)

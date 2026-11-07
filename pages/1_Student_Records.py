
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
    refresh_student_data
)

from database import (
    add_student,
    update_student,
    delete_student
)

st.set_page_config(
    page_title="Student Records | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()
show_sidebar()

# ------------------------------------------------------------
# PAGE THEME
# ------------------------------------------------------------

st.markdown("""
<style>
.stApp { background:#F4F6FC; color:#243451; }
h1,h2,h3 { color:#243451 !important; font-family:Manrope,sans-serif; }
.page-eyebrow {
    color:#5C7CFA; font-size:0.68rem; font-weight:800;
    letter-spacing:1.5px; margin-bottom:7px;
}
.page-subtitle { color:#8792A5; font-size:0.86rem; margin-bottom:20px; }
.panel-title { color:#243451; font-weight:750; font-size:1rem; }
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
# DATA
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records found in the database.")
    st.stop()

required = [
    "student_id", "name", "class_name", "gender",
    "average_marks", "attendance", "study_hours",
    *SUBJECT_COLUMNS
]
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {', '.join(missing)}")
    st.stop()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">WORKSPACE / STUDENTS</div>',
            unsafe_allow_html=True)
st.title("Student Records")
st.markdown(
    '<div class="page-subtitle">Explore student information, academic results, '
    'and individual performance.</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------

with st.container(border=True):
    st.markdown('<div class="panel-title">Student Directory Filters</div>',
                unsafe_allow_html=True)
    st.caption("Narrow the directory by class, gender, or student name.")

    c1, c2, c3 = st.columns(3)

    with c1:
        class_options = ["All classes"] + sorted(
            df["class_name"].dropna().unique().tolist()
        )
        selected_class = st.selectbox("Class", class_options)

    with c2:
        gender_options = ["All genders"] + sorted(
            df["gender"].dropna().unique().tolist()
        )
        selected_gender = st.selectbox("Gender", gender_options)

    with c3:
        search_name = st.text_input(
            "Search student",
            placeholder="Enter a name or student ID"
        )

filtered = df.copy()

if selected_class != "All classes":
    filtered = filtered[filtered["class_name"] == selected_class]

if selected_gender != "All genders":
    filtered = filtered[filtered["gender"] == selected_gender]

if search_name.strip():
    query = search_name.strip()
    filtered = filtered[
        filtered["name"].astype(str).str.contains(
            query, case=False, na=False
        )
        | filtered["student_id"].astype(str).str.contains(
            query, case=False, na=False
        )
    ]

filtered = filtered.reset_index(drop=True)


# ------------------------------------------------------------
# SUMMARY METRICS
# ------------------------------------------------------------

count = len(filtered)
avg = float(filtered["average_marks"].mean()) if count else 0
pass_rate = (
    float((filtered["average_marks"] >= 40).mean() * 100)
    if count else 0
)
attendance_avg = (
    float(filtered["attendance"].mean()) if count else 0
)

st.markdown('<div class="page-eyebrow">RESULTS OVERVIEW</div>',
            unsafe_allow_html=True)
st.subheader("Directory Summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Matching Students", f"{count:,}")
m2.metric("Average Marks", f"{avg:.1f}/100" if count else "N/A")
m3.metric("Pass Rate", f"{pass_rate:.1f}%" if count else "N/A")
m4.metric("Average Attendance", f"{attendance_avg:.1f}%" if count else "N/A")


# ------------------------------------------------------------
# DIRECTORY TABLE AND EXPORT
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">RECORDS / DIRECTORY</div>',
            unsafe_allow_html=True)
st.subheader("Student Directory")

if filtered.empty:
    st.info("No students match these filters. Adjust your search.")
else:
    display_columns = [
        "student_id", "name", "class_name", "gender",
        *SUBJECT_COLUMNS, "average_marks", "attendance", "study_hours"
    ]

    directory = filtered[display_columns].rename(columns={
        "student_id": "Student ID",
        "name": "Student Name",
        "class_name": "Class",
        "gender": "Gender",
        "math_marks": "Mathematics",
        "science_marks": "Science",
        "english_marks": "English",
        "social_science_marks": "Social Science",
        "computer_marks": "Computer",
        "average_marks": "Average Marks",
        "attendance": "Attendance (%)",
        "study_hours": "Study Hours"
    }).copy()

    for col in ["Mathematics", "Science", "English",
                "Social Science", "Computer", "Average Marks",
                "Attendance (%)", "Study Hours"]:
        directory[col] = directory[col].round(1)

    st.dataframe(
        directory, use_container_width=True,
        hide_index=True, height=390
    )

    st.caption(f"Showing {count} student records.")

    st.download_button(
        "Download Student Records CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="student_records.csv",
        mime="text/csv"
    )


# ------------------------------------------------------------
# INDIVIDUAL STUDENT PROFILE
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">STUDENT INSIGHTS / PROFILE</div>',
            unsafe_allow_html=True)
st.subheader("Individual Student Profile")

if filtered.empty:
    st.info("Change the filters to select a student.")
else:
    student_ids = filtered["student_id"].tolist()

    selected_id = st.selectbox(
        "Choose a student",
        student_ids,
        format_func=lambda sid: (
            f"{filtered.loc[filtered['student_id'] == sid, 'name'].iloc[0]} "
            f"({sid})"
        ),
        key="profile_student_selector"
    )

    student = filtered.loc[
        filtered["student_id"] == selected_id
    ].iloc[0]

    st.markdown(
        f"### {student['name']}"
    )
    st.caption(
        f"Student ID: {student['student_id']}  |  "
        f"Class: {student['class_name']}  |  "
        f"Gender: {student['gender']}"
    )

    passed_subjects = sum(
        float(student[col]) >= 40 for col in SUBJECT_COLUMNS
    )

    a, b, c, d = st.columns(4)
    a.metric("Average Marks", f"{student['average_marks']:.1f}/100")
    b.metric("Attendance", f"{student['attendance']:.1f}%")
    c.metric("Study Hours / Day", f"{student['study_hours']:.1f}")
    d.metric("Subjects Passed", f"{passed_subjects}/5")

    # Subject chart
    st.markdown('<div class="page-eyebrow">ACADEMIC BREAKDOWN</div>',
                unsafe_allow_html=True)
    st.subheader("Subject-wise Performance")

    subject_data = pd.DataFrame({
        "Subject": [SUBJECT_NAMES[x] for x in SUBJECT_COLUMNS],
        "Marks": [float(student[x]) for x in SUBJECT_COLUMNS]
    })

    fig_subject = px.bar(
        subject_data,
        x="Marks",
        y="Subject",
        orientation="h",
        color="Subject",
        text_auto=".1f",
        color_discrete_sequence=[
            "#A8B6FF", "#8BCDEB", "#B6D8F5",
            "#5C7CFA", "#8DD9B5"
        ]
    )
    fig_subject.update_traces(
        textposition="outside", cliponaxis=False,
        marker_line_width=0
    )
    fig_subject.update_layout(
        height=330, showlegend=False,
        margin=dict(l=10, r=35, t=15, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#52617A"),
        xaxis=dict(title="Marks out of 100", range=[0, 115],
                   gridcolor="#E9EDF5"),
        yaxis=dict(title=None, showgrid=False)
    )
    st.plotly_chart(fig_subject, use_container_width=True,
                    config={"displayModeBar": False})

    # Learning habits
    st.markdown('<div class="page-eyebrow">LEARNING HABITS</div>',
                unsafe_allow_html=True)
    st.subheader("Attendance & Study Habits")

    habit1, habit2 = st.columns(2)

    with habit1:
        with st.container(border=True):
            st.markdown("**Attendance Overview**")
            attendance_value = max(
                0, min(100, float(student["attendance"]))
            )
            fig_att = go.Figure(go.Pie(
                labels=["Attendance", "Remaining"],
                values=[attendance_value, 100 - attendance_value],
                hole=0.72,
                marker=dict(
                    colors=["#5C7CFA", "#E8ECF5"],
                    line=dict(color="white", width=3)
                ),
                textinfo="none",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>"
            ))
            fig_att.update_layout(
                height=250,
                showlegend=True,
                margin=dict(l=5, r=5, t=5, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[dict(
                    text=f"<b>{attendance_value:.1f}%</b>",
                    x=.5, y=.5, showarrow=False,
                    font=dict(size=20, color="#243451")
                )]
            )
            st.plotly_chart(fig_att, use_container_width=True,
                            config={"displayModeBar": False})

    with habit2:
        with st.container(border=True):
            st.markdown("**Daily Study Hours**")
            fig_study = go.Figure(go.Bar(
                x=["Daily Study"],
                y=[float(student["study_hours"])],
                marker_color="#8BCDEB",
                text=[f"{float(student['study_hours']):.1f} hrs"],
                textposition="outside"
            ))
            fig_study.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#52617A"),
                yaxis=dict(title="Hours per day", gridcolor="#E9EDF5"),
                xaxis=dict(title=None, showgrid=False)
            )
            st.plotly_chart(fig_study, use_container_width=True,
                            config={"displayModeBar": False})

    # Performance interpretation
    st.markdown('<div class="page-eyebrow">PERFORMANCE ASSESSMENT</div>',
                unsafe_allow_html=True)
    st.subheader("Performance Summary")

    score = float(student["average_marks"])

    if score < 40:
        st.warning(
            "Needs Improvement: The student's average is below 40. "
            "Review individual subject results to identify support needs."
        )
    elif score < 60:
        st.info(
            "Satisfactory Performance: The student is passing, "
            "but there may be opportunities to improve."
        )
    else:
        st.success(
            "Good Performance: The student has achieved an average "
            "score of 60 or above."
        )


st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Student Records & Individual Performance Insights
</div>
""", unsafe_allow_html=True)

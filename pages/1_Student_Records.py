
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Student Records | EduAnalytics",
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
            t=45,
            b=20
        ),
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


# ==================================================
# 4. PAGE HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">WORKSPACE / STUDENTS</div>',
    unsafe_allow_html=True
)

st.title("Student Records")

st.markdown(
    """
    <p class="subtitle">
        Explore student information, academic results,
        and individual performance.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)


# ==================================================
# 5. STUDENT SEARCH AND FILTERS
# ==================================================

st.markdown(
    '<div class="eyebrow">STUDENT DIRECTORY</div>',
    unsafe_allow_html=True
)

st.subheader("Find a student")

st.caption(
    "Use the filters below to narrow down the student records."
)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:

    classes = ["All classes"] + sorted(
        df["class_name"].dropna().unique().tolist()
    )

    selected_class = st.selectbox(
        "Filter by class",
        classes
    )


with col2:

    genders = ["All genders"] + sorted(
        df["gender"].dropna().unique().tolist()
    )

    selected_gender = st.selectbox(
        "Filter by gender",
        genders
    )


with col3:

    search_name = st.text_input(
        "Search student name",
        placeholder="Type a student name..."
    )


# Apply filters

filtered_df = df.copy()

if selected_class != "All classes":

    filtered_df = filtered_df[
        filtered_df["class_name"] == selected_class
    ]

if selected_gender != "All genders":

    filtered_df = filtered_df[
        filtered_df["gender"] == selected_gender
    ]

if search_name.strip():

    filtered_df = filtered_df[
        filtered_df["name"].str.contains(
            search_name.strip(),
            case=False,
            na=False
        )
    ]

filtered_df = filtered_df.reset_index(drop=True)


# ==================================================
# 6. FILTERED STUDENT STATISTICS
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">RESULTS OVERVIEW</div>',
    unsafe_allow_html=True
)

st.subheader("Student Statistics")

matching_students = len(filtered_df)

if matching_students > 0:

    filtered_average = filtered_df["average_marks"].mean()

    filtered_pass_rate = (
        filtered_df["average_marks"] >= 40
    ).mean() * 100

else:

    filtered_average = 0
    filtered_pass_rate = 0


col1, col2, col3 = st.columns(3, gap="medium")

with col1:

    st.metric(
        label="Matching Students",
        value=f"{matching_students:,}"
    )

with col2:

    st.metric(
        label="Average Score",
        value=(
            f"{filtered_average:.1f}/100"
            if matching_students else "N/A"
        )
    )

with col3:

    st.metric(
        label="Pass Rate",
        value=(
            f"{filtered_pass_rate:.1f}%"
            if matching_students else "N/A"
        )
    )


# ==================================================
# 7. STUDENT DIRECTORY TABLE
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">RECORDS / DATABASE</div>',
    unsafe_allow_html=True
)

st.subheader("Student Directory")

st.caption(
    "Browse the filtered student records and export the data."
)

if filtered_df.empty:

    st.warning(
        "No students match your selected filters. "
        "Try changing the search or filter options."
    )

else:

    display_columns = [
        "student_id",
        "name",
        "class_name",
        "gender",
        *SUBJECT_COLUMNS,
        "average_marks",
        "attendance",
        "study_hours"
    ]

    directory_df = filtered_df[display_columns].rename(
        columns={
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
        }
    )

    directory_df = directory_df.copy()

    directory_df["Average Marks"] = (
        directory_df["Average Marks"].round(1)
    )

    directory_df["Attendance (%)"] = (
        directory_df["Attendance (%)"].round(1)
    )

    directory_df["Study Hours"] = (
        directory_df["Study Hours"].round(1)
    )

    st.dataframe(
        directory_df,
        use_container_width=True,
        hide_index=True,
        height=420
    )

    st.caption(
        f"Showing {matching_students} student records."
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Student Records CSV",
        data=csv_data,
        file_name="student_records.csv",
        mime="text/csv"
    )


# ==================================================
# 8. INDIVIDUAL STUDENT PROFILE
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">STUDENT INSIGHTS / PROFILE</div>',
    unsafe_allow_html=True
)

st.header("Individual Student Profile")

st.markdown(
    """
    <p class="subtitle">
        Explore an individual student's academic performance,
        attendance, and study habits.
    </p>
    """,
    unsafe_allow_html=True
)


if filtered_df.empty:

    st.info(
        "Change your filters to select a student and view their profile."
    )

else:

    student_options = filtered_df["student_id"].tolist()

    selected_student_id = st.selectbox(
        "Choose a student",
        options=student_options,
        format_func=lambda student_id: (
            f"{filtered_df.loc[filtered_df['student_id'] == student_id, 'name'].iloc[0]} "
            f"({student_id})"
        ),
        key="individual_student_selector"
    )

    student = filtered_df.loc[
        filtered_df["student_id"] == selected_student_id
    ].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(str(student["name"]))

    st.caption(
        f"Student ID: {student['student_id']}  |  "
        f"Class: {student['class_name']}  |  "
        f"Gender: {student['gender']}"
    )


    # ==================================================
    # 9. INDIVIDUAL STUDENT METRICS
    # ==================================================

    subjects_passed = sum(
        pd.notna(student[column]) and student[column] >= 40
        for column in SUBJECT_COLUMNS
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:

        st.metric(
            "Average Marks",
            f"{student['average_marks']:.1f}/100"
        )

    with col2:

        st.metric(
            "Attendance",
            f"{student['attendance']:.1f}%"
        )

    with col3:

        st.metric(
            "Study Hours / Day",
            f"{student['study_hours']:.1f}"
        )

    with col4:

        st.metric(
            "Subjects Passed",
            f"{subjects_passed}/5"
        )


    # ==================================================
    # 10. SUBJECT-WISE PERFORMANCE
    # ==================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="eyebrow">ACADEMIC BREAKDOWN</div>',
        unsafe_allow_html=True
    )

    st.subheader("Subject-wise Performance")

    student_subjects = pd.DataFrame({
        "Subject": [
            SUBJECT_NAMES[column]
            for column in SUBJECT_COLUMNS
        ],
        "Marks": [
            student[column]
            for column in SUBJECT_COLUMNS
        ]
    })

    fig_student = px.bar(
        student_subjects,
        x="Marks",
        y="Subject",
        orientation="h",
        color="Subject",
        text_auto=".1f",
        color_discrete_sequence=CHART_COLORS
    )

    fig_student.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0
    )

    fig_student.update_layout(
        xaxis=dict(
            title="Marks out of 100",
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
        )
    )

    fig_student = style_chart(fig_student, height=350)

    fig_student.update_xaxes(
        title="Marks out of 100",
        range=[0, 112],
        showgrid=True,
        gridcolor=GRID_COLOR
    )

    fig_student.update_yaxes(
        title=None,
        showgrid=False
    )

    st.plotly_chart(
        fig_student,
        use_container_width=True,
        config={"displayModeBar": False}
    )


    # ==================================================
    # 11. ATTENDANCE AND STUDY HABITS
    # ==================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="eyebrow">LEARNING HABITS</div>',
        unsafe_allow_html=True
    )

    st.subheader("Attendance & Study Habits")

    col1, col2 = st.columns(2, gap="large")


    # Attendance chart

    with col1:

        attendance_value = max(
            0,
            min(100, float(student["attendance"]))
        )

        attendance_df = pd.DataFrame({
            "Category": ["Attendance", "Remaining"],
            "Percentage": [
                attendance_value,
                100 - attendance_value
            ]
        })

        attendance_fig = px.bar(
            attendance_df,
            x="Category",
            y="Percentage",
            color="Category",
            text_auto=".1f",
            color_discrete_map={
                "Attendance": "#52745A",
                "Remaining": "#E5E7DF"
            },
            title="Attendance Overview"
        )

        attendance_fig.update_traces(
            marker_line_width=0,
            textposition="outside"
        )

        attendance_fig.update_layout(
            barmode="group",
            yaxis=dict(
                title="Percentage (%)",
                range=[0, 115]
            ),
            xaxis=dict(title=None)
        )

        attendance_fig = style_chart(
            attendance_fig,
            height=350
        )

        attendance_fig.update_yaxes(
            title="Percentage (%)",
            range=[0, 115],
            showgrid=True,
            gridcolor=GRID_COLOR
        )

        st.plotly_chart(
            attendance_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    # Study hours chart

    with col2:

        study_df = pd.DataFrame({
            "Category": ["Daily Study"],
            "Hours": [student["study_hours"]]
        })

        study_fig = px.bar(
            study_df,
            x="Category",
            y="Hours",
            text_auto=".1f",
            color_discrete_sequence=["#C4A779"],
            title="Daily Study Hours"
        )

        study_fig.update_traces(
            marker_line_width=0,
            textposition="outside"
        )

        study_fig.update_layout(
            xaxis=dict(title=None),
            yaxis=dict(
                title="Hours per day",
                rangemode="tozero"
            )
        )

        study_fig = style_chart(
            study_fig,
            height=350
        )

        study_fig.update_yaxes(
            title="Hours per day",
            rangemode="tozero",
            showgrid=True,
            gridcolor=GRID_COLOR
        )

        st.plotly_chart(
            study_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    # ==================================================
    # 12. PERFORMANCE SUMMARY
    # ==================================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="eyebrow">PERFORMANCE ASSESSMENT</div>',
        unsafe_allow_html=True
    )

    st.subheader("Performance Summary")

    average_score = float(student["average_marks"])

    if average_score < 40:

        st.warning(
            "Needs Improvement: This student's average marks "
            "are below 40. Review their individual subject results "
            "to identify areas that need support."
        )

    elif average_score < 60:

        st.info(
            "Satisfactory Performance: This student is passing, "
            "but there may be opportunities to improve their "
            "academic performance."
        )

    else:

        st.success(
            "Good Performance: This student has achieved an "
            "average score of 60 or above."
        )


# ==================================================
# 13. FOOTER
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
        EduAnalytics · Student Records & Individual Performance Insights
    </div>
    """,
    unsafe_allow_html=True
)


import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Student Records | EduAnalytics",
    page_icon="🎓",
    layout="wide"
)

apply_styles()
show_sidebar()

df = load_data()


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
# 3. PAGE HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">WORKSPACE / STUDENTS</div>',
    unsafe_allow_html=True
)

st.title("Student Records")

st.markdown(
    '<p class="subtitle">Explore student information, academic results '
    'and individual performance.</p>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 4. STUDENT SEARCH AND FILTERS
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


# ==================================================
# 5. FILTERED RESULTS OVERVIEW
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">RESULTS OVERVIEW</div>',
    unsafe_allow_html=True
)

st.subheader("Student Statistics")

col1, col2, col3 = st.columns(3, gap="medium")

matching_students = len(filtered_df)

if matching_students > 0:

    filtered_average = filtered_df["average_marks"].mean()

    filtered_pass_rate = (
        filtered_df["average_marks"] >= 40
    ).mean() * 100

else:
    filtered_average = 0
    filtered_pass_rate = 0


with col1:
    st.metric(
        "Matching Students",
        f"{matching_students:,}"
    )

with col2:
    st.metric(
        "Average Score",
        f"{filtered_average:.1f}%" if matching_students else "N/A"
    )

with col3:
    st.metric(
        "Pass Rate",
        f"{filtered_pass_rate:.1f}%" if matching_students else "N/A"
    )


# ==================================================
# 6. STUDENT DIRECTORY TABLE
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">RECORDS / DATABASE</div>',
    unsafe_allow_html=True
)

st.subheader("Student Directory")

st.caption(
    "Browse the filtered records and download the student data."
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
        *subject_columns,
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

    st.dataframe(
        directory_df,
        use_container_width=True,
        hide_index=True,
        height=420
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
# 7. INDIVIDUAL STUDENT PROFILE
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">STUDENT INSIGHTS / PROFILE</div>',
    unsafe_allow_html=True
)

st.title("Individual Student Profile")

st.markdown(
    '<p class="subtitle">Explore an individual student’s academic '
    'performance, attendance and study habits.</p>',
    unsafe_allow_html=True
)


if filtered_df.empty:

    st.info(
        "Select different filters to view an individual student profile."
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

    st.divider()

    # Student identity
    st.subheader(str(student["name"]))

    st.caption(
        f"Student ID: {student['student_id']}  |  "
        f"Class: {student['class_name']}  |  "
        f"Gender: {student['gender']}"
    )


    # ==================================================
    # 8. INDIVIDUAL STUDENT METRICS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    subjects_passed = sum(
        pd.notna(student[column]) and student[column] >= 40
        for column in subject_columns
    )

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
    # 9. SUBJECT-WISE PERFORMANCE
    # ==================================================

    st.divider()

    st.markdown(
        '<div class="eyebrow">ACADEMIC BREAKDOWN</div>',
        unsafe_allow_html=True
    )

    st.subheader("Subject-wise Performance")

    student_subjects = pd.DataFrame({
        "Subject": [
            subject_names[column]
            for column in subject_columns
        ],
        "Marks": [
            student[column]
            for column in subject_columns
        ]
    })

    fig_student = px.bar(
        student_subjects,
        x="Subject",
        y="Marks",
        color="Subject",
        text_auto=".1f",
        color_discrete_sequence=chart_colors
    )

    fig_student.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="DM Sans, sans-serif",
            size=12,
            color="#252923"
        ),
        showlegend=False,
        yaxis_range=[0, 100],
        xaxis_title="",
        yaxis_title="Marks out of 100",
        margin=dict(l=15, r=15, t=25, b=15)
    )

    fig_student.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig_student,
        use_container_width=True,
        config={"displayModeBar": False}
    )


    # ==================================================
    # 10. ATTENDANCE AND STUDY HABITS
    # ==================================================

    st.divider()

    st.markdown(
        '<div class="eyebrow">LEARNING HABITS</div>',
        unsafe_allow_html=True
    )

    st.subheader("Attendance & Study Habits")

    col1, col2 = st.columns(2, gap="large")


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

        attendance_fig.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="DM Sans, sans-serif",
                size=12,
                color="#252923"
            ),
            showlegend=False,
            yaxis_range=[0, 100],
            xaxis_title="",
            yaxis_title="Percentage (%)",
            margin=dict(l=15, r=15, t=55, b=15)
        )

        st.plotly_chart(
            attendance_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


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

        study_fig.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="DM Sans, sans-serif",
                size=12,
                color="#252923"
            ),
            showlegend=False,
            xaxis_title="",
            yaxis_title="Hours per day",
            margin=dict(l=15, r=15, t=55, b=15)
        )

        st.plotly_chart(
            study_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    # ==================================================
    # 11. PERFORMANCE SUMMARY
    # ==================================================

    st.divider()

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
# 12. FOOTER
# ==================================================

st.divider()

st.caption(
    "EduAnalytics | Student Records & Individual Performance Insights"
)

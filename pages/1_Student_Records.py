
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar

st.set_page_config(
    page_title="Student Records | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()
show_sidebar()

df = load_data()

# Subject configuration
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

# Page heading
st.markdown(
    '<div class="eyebrow">WORKSPACE / STUDENTS</div>',
    unsafe_allow_html=True
)

st.title("Student records")

st.markdown(
    '<p class="subtitle">Search and explore individual student information.</p>',
    unsafe_allow_html=True
)

st.divider()

# ---------- FILTERS ----------
st.subheader("Find students")

col1, col2, col3 = st.columns(3)

with col1:
    classes = ["All classes"] + sorted(
        df["class_name"].dropna().unique().tolist()
    )
    selected_class = st.selectbox("Class", classes)

with col2:
    genders = ["All genders"] + sorted(
        df["gender"].dropna().unique().tolist()
    )
    selected_gender = st.selectbox("Gender", genders)

with col3:
    search_name = st.text_input(
        "Search by name",
        placeholder="Enter a student name"
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

# ---------- RESULTS OVERVIEW ----------
st.divider()
st.subheader("Results overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Matching students", len(filtered_df))

with col2:
    if filtered_df.empty:
        st.metric("Average score", "N/A")
    else:
        st.metric(
            "Average score",
            f"{filtered_df['average_marks'].mean():.1f}%"
        )

with col3:
    if filtered_df.empty:
        st.metric("Pass rate", "N/A")
    else:
        pass_rate = (
            filtered_df["average_marks"] >= 40
        ).mean() * 100

        st.metric("Pass rate", f"{pass_rate:.1f}%")

# ---------- STUDENT DIRECTORY ----------
st.divider()
st.subheader("Student directory")

if filtered_df.empty:
    st.warning("No students match these filters.")

else:
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download filtered records",
        data=csv_data,
        file_name="student_records.csv",
        mime="text/csv"
    )

# ---------- INDIVIDUAL STUDENT PROFILE ----------
st.divider()

st.markdown(
    '<div class="eyebrow">STUDENT INSIGHTS / PROFILE</div>',
    unsafe_allow_html=True
)

st.title("Individual Student Profile")

st.caption(
    "Select a student to explore their academic performance, "
    "attendance, and study habits."
)

if filtered_df.empty:

    st.info("No students are available for the selected filters.")

else:
    student_options = filtered_df["student_id"].tolist()

    selected_student_id = st.selectbox(
        "Select a student",
        options=student_options,
        format_func=lambda student_id: (
            f"{filtered_df.loc[filtered_df['student_id'] == student_id, 'name'].iloc[0]} "
            f"(ID: {student_id})"
        ),
        key="individual_student_selector"
    )

    # Retrieve the student from filtered results
    student = filtered_df.loc[
        filtered_df["student_id"] == selected_student_id
    ].iloc[0]

    st.divider()

    st.subheader(str(student["name"]))

    st.caption(
        f"Student ID: {student['student_id']} · "
        f"Class: {student['class_name']}"
    )

    # ---------- STUDENT SUMMARY METRICS ----------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Marks",
            f"{student['average_marks']:.1f}/100"
        )

    with col2:
        st.metric(
            "Attendance",
            f"{student['attendance']}%"
        )

    with col3:
        st.metric(
            "Study Hours/Day",
            f"{student['study_hours']}"
        )

    with col4:
        subjects_passed = sum(
            student[column] >= 40
            for column in subject_columns
        )

        st.metric(
            "Subjects Passed",
            f"{subjects_passed}/5"
        )

    # ---------- SUBJECT PERFORMANCE ----------
    st.divider()
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
        color_discrete_sequence=[
            "#52745A",
            "#91A68A",
            "#C4A779",
            "#758B9B",
            "#B58B83"
        ]
    )

    fig_student.update_layout(
        paper_bgcolor="#F7F7F2",
        plot_bgcolor="#F7F7F2",
        font_color="#252923",
        showlegend=False,
        yaxis_range=[0, 100],
        xaxis_title="",
        yaxis_title="Marks out of 100"
    )

    st.plotly_chart(
        fig_student,
        use_container_width=True
    )

    # ---------- ATTENDANCE AND STUDY HABITS ----------
    st.divider()
    st.subheader("Attendance & Study Habits")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Attendance**")

        attendance_fig = px.bar(
            pd.DataFrame({
                "Category": ["Attendance", "Remaining"],
                "Percentage": [
                    student["attendance"],
                    max(0, 100 - student["attendance"])
                ]
            }),
            x="Category",
            y="Percentage",
            color="Category",
            color_discrete_sequence=[
                "#52745A",
                "#E5E7DF"
            ]
        )

        attendance_fig.update_layout(
            paper_bgcolor="#F7F7F2",
            plot_bgcolor="#F7F7F2",
            font_color="#252923",
            showlegend=False,
            yaxis_range=[0, 100],
            xaxis_title="",
            yaxis_title="Percentage (%)"
        )

        st.plotly_chart(
            attendance_fig,
            use_container_width=True
        )

    with col2:
        st.markdown("**Daily Study Hours**")

        study_fig = px.bar(
            pd.DataFrame({
                "Category": ["Study hours"],
                "Hours": [student["study_hours"]]
            }),
            x="Category",
            y="Hours",
            text_auto=".1f",
            color_discrete_sequence=["#C4A779"]
        )

        study_fig.update_layout(
            paper_bgcolor="#F7F7F2",
            plot_bgcolor="#F7F7F2",
            font_color="#252923",
            xaxis_title="",
            yaxis_title="Hours per day"
        )

        st.plotly_chart(
            study_fig,
            use_container_width=True
        )

    # ---------- PERFORMANCE SUMMARY ----------
    st.divider()
    st.subheader("Performance Summary")

    if student["average_marks"] < 40:
        st.warning(
            "This student's average marks are below 40. "
            "Consider reviewing their subject-wise performance."
        )

    elif student["average_marks"] < 60:
        st.info(
            "This student is passing, but there may be "
            "opportunities to improve their academic performance."
        )

    else:
        st.success(
            "This student has an average score of 60 or above."
        )

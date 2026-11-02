
import streamlit as st
from data_utils import load_data, apply_styles, show_sidebar
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Student Records | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()
show_sidebar()
df = load_data()

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

# Filters
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

# Metrics update with filters
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
        rate = (
            filtered_df["average_marks"] >= 40
        ).mean() * 100
        st.metric("Pass rate", f"{rate:.1f}%")

# Table
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

import plotly.express as px

if filtered_df.empty:
    st.info("No students are available for the selected filters.")
else:
    # Select a student from the filtered results
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

    # Get the selected student's record
    student = df.loc[
        df["student_id"] == selected_student_id
    ].iloc[0]

    st.divider()

    st.subheader(str(student["name"]))

    st.caption(
        f"Student ID: {student['student_id']} · "
        f"Class: {student['class_name']}"
    )

    # Student summary metrics
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
        subjects_passed = sum([
            student["math_marks"] >= 40,
            student["science_marks"] >= 40,
            student["english_marks"] >= 40
        ])

        st.metric(
            "Subjects Passed",
            f"{subjects_passed}/3"
        )

    # ---------- SUBJECT PERFORMANCE GRAPH ----------
    st.divider()
    st.subheader("Subject-wise Performance")

    student_subjects = pd.DataFrame({
        "Subject": [
            "Mathematics",
            "Science",
            "English"
        ],
        "Marks": [
            student["math_marks"],
            student["science_marks"],
            student["english_marks"]
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
            "#C4A779"
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

    # ---------- PERFORMANCE STATUS ----------
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

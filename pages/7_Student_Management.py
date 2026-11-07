
import streamlit as st
import pandas as pd

from data_utils import (
    load_data,
    apply_styles,
    show_sidebar,
    SUBJECT_COLUMNS,
    SUBJECT_NAMES,
    refresh_student_data,
)

from database import (
    add_student,
    update_student,
    delete_student,
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Management | EduAnalytics",
    layout="wide",
)

apply_styles()
show_sidebar()

if "management_message" in st.session_state:
    st.success(st.session_state["management_message"])
    del st.session_state["management_message"]
# ============================================================
# PAGE HEADER
# ============================================================

st.title("Student Management")

st.markdown(
    "Add, update and manage student records in the database."
)

# ============================================================
# SUMMARY
# ============================================================

df = load_data()

total_students = len(df)

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Students", total_students)

with col2:
    st.metric("Database", "SQLite")

st.divider()

# ============================================================
# MANAGEMENT TABS
# ============================================================

tab_add, tab_edit, tab_delete = st.tabs([
    "Add Student",
    "Edit Student",
    "Delete Student",
])

# ============================================================
# ADD STUDENT
# ============================================================

with tab_add:

    st.subheader("Add New Student")

    with st.form("add_student_form"):

        c1, c2 = st.columns(2)

        with c1:
            new_id = st.text_input("Student ID")
            new_name = st.text_input("Student Name")

            new_class = st.selectbox(
                "Class",
                [
                    "10A", "10B", "10C",
                    "11A", "11B", "11C",
                    "12A", "12B", "12C"
                ]
            )

            new_gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

        with c2:
            new_attendance = st.number_input(
                "Attendance (%)",
                min_value=0.0,
                max_value=100.0,
                value=75.0
            )

            new_study = st.number_input(
                "Study Hours / Day",
                min_value=0.0,
                max_value=24.0,
                value=2.0
            )

        st.markdown("**Subject Marks**")

        marks_cols = st.columns(5)
        subject_values = {}

        for i, subject in enumerate(SUBJECT_COLUMNS):
            with marks_cols[i]:
                subject_values[subject] = st.number_input(
                    SUBJECT_NAMES[subject],
                    min_value=0.0,
                    max_value=100.0,
                    value=50.0,
                    key=f"new_{subject}"
                )

        submitted = st.form_submit_button(
            "Add Student",
            use_container_width=True
        )

        if submitted:

            if not new_id.strip() or not new_name.strip():
                st.error("Student ID and name are required.")

            else:
                try:
                    average = sum(subject_values.values()) / len(
                        subject_values
                    )

                    student_data = {
                        "student_id": new_id.strip(),
                        "name": new_name.strip(),
                        "class_name": new_class,
                        "gender": new_gender,
                        "average_marks": average,
                        "attendance": new_attendance,
                        "study_hours": new_study,
                        **subject_values
                    }

                    add_student(student_data)
                    refresh_student_data()

                    st.session_state["management_message"] = "Student added successfully."
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not add student: {e}")

# ============================================================
# EDIT STUDENT
# ============================================================

with tab_edit:

    edit_df = load_data()

    if edit_df.empty:
        st.info("No student records available.")

    else:
        student_options = edit_df["student_id"].astype(str).tolist()

        edit_id = st.selectbox(
            "Select Student",
            student_options,
            format_func=lambda sid: (
                f"{edit_df.loc[edit_df['student_id'].astype(str) == sid, 'name'].iloc[0]} "
                f"({sid})"
            ),
            key="edit_student_selector"
        )

        edit_student = edit_df[
            edit_df["student_id"].astype(str) == str(edit_id)
        ].iloc[0]

        with st.form(f"edit_student_form_{edit_id}"):

            st.markdown("**Update Student Information**")

            c1, c2 = st.columns(2)

            with c1:
                edit_name = st.text_input(
                    "Student Name",
                    value=str(edit_student["name"]),
                    key=f"edit_name_{edit_id}"
                )

                edit_class = st.text_input(
                    "Class",
                    value=str(edit_student["class_name"]),
                    key=f"edit_class_{edit_id}"
                )

                gender_options = ["Male", "Female", "Other"]
                current_gender = str(edit_student["gender"])

                edit_gender = st.selectbox(
                    "Gender",
                    gender_options,
                    index=(
                        gender_options.index(current_gender)
                        if current_gender in gender_options else 0
                    ),
                    key=f"edit_gender_{edit_id}"
                )

            with c2:
                edit_attendance = st.number_input(
                    "Attendance (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(edit_student["attendance"]),
                    key=f"edit_attendance_{edit_id}"
                )

                edit_study = st.number_input(
                    "Study Hours / Day",
                    min_value=0.0,
                    max_value=24.0,
                    value=float(edit_student["study_hours"]),
                    key=f"edit_study_{edit_id}"
                )

            st.markdown("**Update Subject Marks**")

            edit_marks = {}
            marks_cols = st.columns(5)

            for i, subject in enumerate(SUBJECT_COLUMNS):
                with marks_cols[i]:
                    edit_marks[subject] = st.number_input(
                        SUBJECT_NAMES[subject],
                        min_value=0.0,
                        max_value=100.0,
                        value=float(edit_student[subject]),
                        key=f"edit_{edit_id}_{subject}"
                    )

            update_submitted = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_submitted:

                try:
                    average = sum(edit_marks.values()) / len(edit_marks)

                    updates = {
                        "name": edit_name.strip(),
                        "class_name": edit_class.strip(),
                        "gender": edit_gender,
                        "attendance": edit_attendance,
                        "study_hours": edit_study,
                        "average_marks": average,
                        **edit_marks
                    }

                    update_student(str(edit_id), updates)
                    refresh_student_data()

                    st.success("Student record updated successfully.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not update student: {e}")

# ============================================================
# DELETE STUDENT
# ============================================================

with tab_delete:

    delete_df = load_data()

    if delete_df.empty:
        st.info("No student records available.")

    else:
        delete_options = delete_df["student_id"].astype(str).tolist()

        delete_id = st.selectbox(
            "Select Student to Delete",
            delete_options,
            format_func=lambda sid: (
                f"{delete_df.loc[delete_df['student_id'].astype(str) == sid, 'name'].iloc[0]} "
                f"({sid})"
            ),
            key="delete_student_selector"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to permanently delete this student."
        )

        if st.button(
            "Delete Student",
            type="primary",
            disabled=not confirm_delete
        ):

            try:
                delete_student(str(delete_id))
                refresh_student_data()

                st.success("Student deleted successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"Could not delete student: {e}")

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EduAnalytics | Student Management System"
)

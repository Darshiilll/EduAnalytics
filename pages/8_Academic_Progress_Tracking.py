
import streamlit as st
import pandas as pd
from datetime import date

from data_utils import (
    load_data,
    apply_styles,
    show_sidebar,
    SUBJECT_COLUMNS,
    SUBJECT_NAMES,
)

from database import (
    add_exam,
    get_all_exams,
    save_exam_results_bulk,
    get_exam_results,
    get_exam_history,
    update_exam_max_marks,
)


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Academic Progress Tracking | EduAnalytics",
    layout="wide"
)

apply_styles()
show_sidebar()

st.title("Academic Progress Tracking")
st.markdown(
    "Manage examinations, enter and correct marks, "
    "and monitor student and class performance."
)
st.divider()


# =====================================================
# LOAD DATA
# =====================================================

students_df = load_data()
exams = get_all_exams()

if students_df.empty:
    st.warning("No students found. Add students before tracking progress.")
    st.stop()

if not SUBJECT_COLUMNS:
    st.error("No subject columns are configured.")
    st.stop()

students_df = students_df.copy()
students_df["student_id"] = students_df["student_id"].astype(str)

student_options = students_df["student_id"].tolist()

student_lookup = students_df.set_index("student_id")

class_options = sorted(
    students_df["class_name"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

subject_names = {
    subject: SUBJECT_NAMES.get(
        subject,
        subject.replace("_marks", "").replace("_", " ").title()
    )
    for subject in SUBJECT_COLUMNS
}


def get_exam_label(exam):
    return (
        f"{exam['exam_name']} "
        f"({exam['exam_date']})"
    )


def get_exam_lookup():
    return {
        exam["exam_id"]: exam
        for exam in exams
    }


def get_percentage(marks, maximum):
    if pd.isna(marks) or maximum <= 0:
        return None
    return float(marks) / float(maximum) * 100


def get_result_dataframe(exam_id, class_name=None):
    results = get_exam_results(exam_id, class_name)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df["percentage"] = (
        df["marks"] / df["max_marks"] * 100
    )

    return df


# =====================================================
# SUMMARY METRICS
# =====================================================

total_students = len(students_df)
total_exams = len(exams)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Total Students", total_students)

with metric2:
    st.metric("Total Examinations", total_exams)

with metric3:
    st.metric("Subjects Tracked", len(SUBJECT_COLUMNS))

st.divider()


# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Exam Management",
    "Enter / Edit Marks",
    "Student Progress",
    "Class Analytics",
    "Export Results",
])


# =====================================================
# TAB 1: EXAM MANAGEMENT
# =====================================================

with tab1:

    st.subheader("Create New Examination")

    with st.form("create_exam_form"):

        exam_name = st.text_input(
            "Examination Name",
            placeholder="Example: Unit Test 1"
        )

        exam_date = st.date_input(
            "Examination Date",
            value=date.today()
        )

        max_marks = st.number_input(
            "Maximum Marks per Subject",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=5.0
        )

        create_exam = st.form_submit_button(
            "Create Examination",
            use_container_width=True
        )

        if create_exam:

            if not exam_name.strip():
                st.error("Please enter an examination name.")

            else:
                try:
                    add_exam(
                        exam_name.strip(),
                        exam_date.isoformat(),
                        max_marks
                    )

                    st.success("Examination created successfully.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not create examination: {error}")

    st.divider()

    st.subheader("Examination Records")

    if exams:

        exam_df = pd.DataFrame(exams)

        exam_df = exam_df.rename(
            columns={
                "exam_id": "Exam ID",
                "exam_name": "Examination",
                "exam_date": "Date",
                "max_marks": "Maximum Marks",
            }
        )

        st.dataframe(
            exam_df[
                ["Exam ID", "Examination", "Date", "Maximum Marks"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Update Maximum Marks")

        exam_lookup = get_exam_lookup()

        selected_update_exam = st.selectbox(
            "Choose Examination",
            options=list(exam_lookup.keys()),
            format_func=lambda exam_id: get_exam_label(
                exam_lookup[exam_id]
            ),
            key="update_max_exam"
        )

        selected_exam = exam_lookup[selected_update_exam]

        with st.form("update_max_marks_form"):

            updated_maximum = st.number_input(
                "New Maximum Marks per Subject",
                min_value=1.0,
                max_value=10000.0,
                value=float(selected_exam["max_marks"]),
                step=5.0
            )

            update_maximum_button = st.form_submit_button(
                "Update Maximum Marks",
                use_container_width=True
            )

            if update_maximum_button:

                try:
                    update_exam_max_marks(
                        selected_update_exam,
                        updated_maximum
                    )

                    st.success("Maximum marks updated.")
                    st.rerun()

                except Exception as error:
                    st.error(str(error))

    else:
        st.info("No examinations have been created yet.")


# =====================================================
# TAB 2: ENTER / EDIT MARKS
# =====================================================

with tab2:

    st.subheader("Enter or Correct Examination Marks")

    if not exams:
        st.info("Create an examination before entering marks.")

    else:

        exam_lookup = get_exam_lookup()

        selected_exam_id = st.selectbox(
            "Select Examination",
            options=list(exam_lookup.keys()),
            format_func=lambda exam_id: get_exam_label(
                exam_lookup[exam_id]
            ),
            key="marks_exam_selection"
        )

        selected_exam = exam_lookup[selected_exam_id]
        maximum = float(selected_exam["max_marks"])

        st.caption(
            f"Maximum marks per subject: {maximum:g}. "
            "Existing marks are preloaded, so this table also edits results."
        )

        entry_mode = st.radio(
            "Choose student group",
            ["Entire Class", "Individual Student"],
            horizontal=True,
            key="marks_entry_mode"
        )

        if entry_mode == "Entire Class":

            selected_class = st.selectbox(
                "Select Class",
                options=class_options,
                key="bulk_class_selection"
            )

            selected_students = students_df[
                students_df["class_name"].astype(str) == selected_class
            ].copy()

        else:

            selected_student_id = st.selectbox(
                "Select Student",
                options=student_options,
                format_func=lambda student_id: (
                    f"{student_id} - "
                    f"{student_lookup.loc[student_id, 'name']}"
                ),
                key="individual_marks_student"
            )

            selected_students = students_df[
                students_df["student_id"] == selected_student_id
            ].copy()

        existing_results = get_exam_results(selected_exam_id)

        existing_marks = {
            (row["student_id"], row["subject"]): row["marks"]
            for row in existing_results
        }

        table_rows = []

        for _, student in selected_students.iterrows():

            row = {
                "Student ID": student["student_id"],
                "Student Name": student["name"],
            }

            for subject in SUBJECT_COLUMNS:

                row[subject_names[subject]] = existing_marks.get(
                    (student["student_id"], subject),
                    None
                )

            table_rows.append(row)

        marks_df = pd.DataFrame(table_rows)

        if not marks_df.empty:

            marks_column_config = {}

            for subject in SUBJECT_COLUMNS:
                label = subject_names[subject]

                marks_column_config[label] = st.column_config.NumberColumn(
                    label,
                    min_value=0.0,
                    max_value=maximum,
                    step=1.0,
                    format="%.2f",
                    required=False
                )

            edited_df = st.data_editor(
                marks_df,
                column_config=marks_column_config,
                disabled=["Student ID", "Student Name"],
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                key=f"marks_editor_{selected_exam_id}_{entry_mode}"
            )

            st.caption(
                "Leave a cell blank if the student has not received "
                "a mark for that subject. Enter 0 only when the student "
                "actually scored zero."
            )

            if st.button(
                "Save Examination Results",
                type="primary",
                use_container_width=True,
                key="save_bulk_marks"
            ):

                results_to_save = []

                for _, row in edited_df.iterrows():

                    student_marks = {}

                    for subject in SUBJECT_COLUMNS:

                        label = subject_names[subject]
                        value = row[label]

                        if pd.isna(value):
                            student_marks[subject] = None
                        else:
                            student_marks[subject] = float(value)

                    results_to_save.append({
                        "student_id": str(row["Student ID"]),
                        "marks": student_marks
                    })

                try:

                    save_exam_results_bulk(
                        selected_exam_id,
                        results_to_save
                    )

                    st.success(
                        f"Results saved for "
                        f"{len(results_to_save)} student(s)."
                    )

                    st.rerun()

                except Exception as error:
                    st.error(f"Could not save results: {error}")

        else:
            st.info("No students are available in this selection.")


# =====================================================
# TAB 3: INDIVIDUAL STUDENT PROGRESS
# =====================================================

with tab3:

    st.subheader("Individual Student Performance")

    selected_student_id = st.selectbox(
        "Choose Student",
        options=student_options,
        format_func=lambda student_id: (
            f"{student_id} - "
            f"{student_lookup.loc[student_id, 'name']}"
        ),
        key="progress_student_selection"
    )

    selected_student = student_lookup.loc[selected_student_id]

    st.caption(
        f"Class: {selected_student['class_name']}"
    )

    history = get_exam_history(selected_student_id)

    if history:

        history_df = pd.DataFrame(history)

        history_df["marks"] = pd.to_numeric(
            history_df["marks"],
            errors="coerce"
        )

        history_df["max_marks"] = pd.to_numeric(
            history_df["max_marks"],
            errors="coerce"
        )

        history_df["percentage"] = (
            history_df["marks"] /
            history_df["max_marks"] * 100
        )

        history_df["exam_date"] = pd.to_datetime(
            history_df["exam_date"]
        )

        history_df = history_df.sort_values(
            ["exam_date", "exam_id"]
        )

        # Each exam average is calculated using available subject results.
        exam_averages = (
            history_df.groupby(
                ["exam_id", "exam_name", "exam_date"]
            )
            .agg(
                average_percentage=("percentage", "mean"),
                subjects_attempted=("subject", "count")
            )
            .reset_index()
            .sort_values(["exam_date", "exam_id"])
        )

        overall_average = history_df["percentage"].mean()

        latest_exam = exam_averages.iloc[-1]
        latest_average = latest_exam["average_percentage"]

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric(
                "Exams Attempted",
                history_df["exam_id"].nunique()
            )

        with metric2:
            st.metric(
                "Overall Average",
                f"{overall_average:.1f}%"
            )

        with metric3:
            st.metric(
                "Latest Exam Average",
                f"{latest_average:.1f}%"
            )

        st.divider()

        st.subheader("Examination-wise Progress")

        exam_averages["Exam"] = (
            exam_averages["exam_name"]
            + " ("
            + exam_averages["exam_date"].dt.strftime("%d %b %Y")
            + ")"
        )

        progress_chart = exam_averages.set_index("Exam")[
            ["average_percentage"]
        ].rename(
            columns={"average_percentage": "Average Percentage"}
        )

        st.line_chart(
            progress_chart,
            use_container_width=True
        )

        st.divider()

        st.subheader("Subject-wise Progress")

        subject_progress = history_df.pivot_table(
            index=["exam_date", "exam_name"],
            columns="subject",
            values="percentage",
            aggfunc="mean"
        ).reset_index()

        subject_progress = subject_progress.sort_values("exam_date")

        subject_progress["Exam"] = (
            subject_progress["exam_name"]
            + " ("
            + subject_progress["exam_date"].dt.strftime("%d %b %Y")
            + ")"
        )

        chart_columns = [
            subject
            for subject in SUBJECT_COLUMNS
            if subject in subject_progress.columns
        ]

        if chart_columns:

            subject_chart = subject_progress[
                ["Exam"] + chart_columns
            ].set_index("Exam")

            subject_chart = subject_chart.rename(
                columns=subject_names
            )

            st.line_chart(
                subject_chart,
                use_container_width=True
            )

        st.caption(
            "Subject progress is shown as a percentage, "
            "so examinations with different maximum marks can be compared."
        )

        st.divider()

        st.subheader("Detailed Examination History")

        display_history = history_df.copy()

        display_history["exam_date"] = (
            display_history["exam_date"].dt.strftime("%d %b %Y")
        )

        display_history["subject"] = (
            display_history["subject"].map(subject_names)
        )

        display_history = display_history.rename(
            columns={
                "exam_name": "Examination",
                "exam_date": "Date",
                "subject": "Subject",
                "marks": "Marks Obtained",
                "max_marks": "Maximum Marks",
                "percentage": "Percentage",
            }
        )

        display_history["Percentage"] = (
            display_history["Percentage"].round(1).astype(str) + "%"
        )

        st.dataframe(
            display_history[
                [
                    "Examination",
                    "Date",
                    "Subject",
                    "Marks Obtained",
                    "Maximum Marks",
                    "Percentage",
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Performance Comparison")

        if len(exam_averages) >= 2:

            previous_average = exam_averages.iloc[-2][
                "average_percentage"
            ]

            current_average = exam_averages.iloc[-1][
                "average_percentage"
            ]

            difference = current_average - previous_average

            if difference > 0:
                st.success(
                    f"Performance improved by {difference:.1f} "
                    "percentage points compared with the previous exam."
                )

            elif difference < 0:
                st.warning(
                    f"Performance declined by {abs(difference):.1f} "
                    "percentage points compared with the previous exam."
                )

            else:
                st.info(
                    "Performance remained unchanged compared "
                    "with the previous examination."
                )

        else:
            st.info(
                "At least two examinations with recorded marks "
                "are required to compare progress."
            )

    else:
        st.info(
            "No examination results are available for this student yet."
        )


# =====================================================
# TAB 4: CLASS ANALYTICS
# =====================================================

with tab4:

    st.subheader("Class-wise Academic Performance")

    if not exams:
        st.info("Create examinations and enter marks to view class analytics.")

    else:

        exam_lookup = get_exam_lookup()

        analytics_exam_id = st.selectbox(
            "Select Examination",
            options=list(exam_lookup.keys()),
            format_func=lambda exam_id: get_exam_label(
                exam_lookup[exam_id]
            ),
            key="class_analytics_exam"
        )

        analytics_df = get_result_dataframe(analytics_exam_id)

        if analytics_df.empty:
            st.info("No results have been entered for this examination.")

        else:

            class_summary = (
                analytics_df.groupby("class_name")
                .agg(
                    students=("student_id", "nunique"),
                    average_percentage=("percentage", "mean"),
                    highest_percentage=("percentage", "max"),
                    lowest_percentage=("percentage", "min"),
                    results_recorded=("marks", "count")
                )
                .reset_index()
                .sort_values(
                    "average_percentage",
                    ascending=False
                )
            )

            class_summary = class_summary.rename(
                columns={
                    "class_name": "Class",
                    "students": "Students with Results",
                    "average_percentage": "Average Percentage",
                    "highest_percentage": "Highest Percentage",
                    "lowest_percentage": "Lowest Percentage",
                    "results_recorded": "Subject Results Recorded",
                }
            )

            for column in [
                "Average Percentage",
                "Highest Percentage",
                "Lowest Percentage"
            ]:
                class_summary[column] = (
                    class_summary[column].round(1)
                )

            st.dataframe(
                class_summary,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Class Average Comparison")

            chart_df = class_summary.set_index("Class")[
                ["Average Percentage"]
            ]

            st.bar_chart(
                chart_df,
                use_container_width=True
            )

            st.caption(
                "Class averages are calculated from recorded subject "
                "results only. Missing marks are excluded, not treated as zero."
            )

            st.divider()

            st.subheader("Student Performance in Selected Class")

            selected_class = st.selectbox(
                "Choose Class",
                options=sorted(
                    analytics_df["class_name"]
                    .dropna()
                    .astype(str)
                    .unique()
                ),
                key="class_student_detail"
            )

            class_students = analytics_df[
                analytics_df["class_name"].astype(str) == selected_class
            ]

            student_summary = (
                class_students.groupby(
                    ["student_id", "name"]
                )
                .agg(
                    average_percentage=("percentage", "mean"),
                    subjects_recorded=("subject", "count")
                )
                .reset_index()
                .sort_values(
                    "average_percentage",
                    ascending=False
                )
            )

            student_summary["average_percentage"] = (
                student_summary["average_percentage"].round(1)
            )

            student_summary = student_summary.rename(
                columns={
                    "student_id": "Student ID",
                    "name": "Student Name",
                    "average_percentage": "Average Percentage",
                    "subjects_recorded": "Subjects Recorded",
                }
            )

            st.dataframe(
                student_summary,
                use_container_width=True,
                hide_index=True
            )


# =====================================================
# TAB 5: EXPORT RESULTS
# =====================================================

with tab5:

    st.subheader("Export Examination Results")

    if not exams:

        st.info("No examinations are available for export.")

    else:

        exam_lookup = get_exam_lookup()

        export_exam_id = st.selectbox(
            "Select Examination to Export",
            options=list(exam_lookup.keys()),
            format_func=lambda exam_id: get_exam_label(
                exam_lookup[exam_id]
            ),
            key="export_exam_selection"
        )

        export_df = get_result_dataframe(export_exam_id)

        if export_df.empty:

            st.info("No results are available for this examination.")

        else:

            export_df = export_df.copy()

            export_df["subject"] = (
                export_df["subject"].map(subject_names)
            )

            export_df["percentage"] = (
                export_df["percentage"].round(2)
            )

            export_df = export_df.rename(
                columns={
                    "student_id": "Student ID",
                    "name": "Student Name",
                    "class_name": "Class",
                    "exam_name": "Examination",
                    "exam_date": "Exam Date",
                    "subject": "Subject",
                    "marks": "Marks Obtained",
                    "max_marks": "Maximum Marks",
                    "percentage": "Percentage",
                }
            )

            export_columns = [
                "Student ID",
                "Student Name",
                "Class",
                "Examination",
                "Exam Date",
                "Subject",
                "Marks Obtained",
                "Maximum Marks",
                "Percentage",
            ]

            export_df = export_df[export_columns]

            st.dataframe(
                export_df,
                use_container_width=True,
                hide_index=True
            )

            csv_data = export_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name=(
                    f"exam_results_{export_exam_id}.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )

            try:

                import io

                excel_buffer = io.BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl"
                ) as writer:

                    export_df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Exam Results"
                    )

                st.download_button(
                    "Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=(
                        f"exam_results_{export_exam_id}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )

            except ImportError:

                st.info(
                    "Excel export requires openpyxl. "
                    "Install it with: pip install openpyxl"
                )


# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption("EduAnalytics | Academic Progress Tracking")

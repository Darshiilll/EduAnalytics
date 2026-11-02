
import streamlit as st
from data_utils import load_data, apply_styles, show_sidebar

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

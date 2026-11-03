
import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, apply_styles, show_sidebar

st.set_page_config(
    page_title="Academic Analytics | EduAnalytics",
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
    '<div class="eyebrow">WORKSPACE / ANALYTICS</div>',
    unsafe_allow_html=True
)

st.title("Academic Analytics")

st.markdown(
    '<p class="subtitle">Explore student performance, attendance, '
    'and academic trends across all five subjects.</p>',
    unsafe_allow_html=True
)

st.divider()

# ---------- OVERVIEW METRICS ----------
st.subheader("Academic Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Students",
        len(df)
    )

with col2:
    st.metric(
        "Average Score",
        f"{df['average_marks'].mean():.1f}%"
    )

with col3:
    pass_rate = (df["average_marks"] >= 40).mean() * 100

    st.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )

with col4:
    st.metric(
        "Average Attendance",
        f"{df['attendance'].mean():.1f}%"
    )

st.divider()

# ---------- SUBJECT-WISE PERFORMANCE ----------
st.subheader("Subject-wise Performance")

subject_data = pd.DataFrame({
    "Subject": [
        subject_names[column]
        for column in subject_columns
    ],
    "Average Marks": [
        df[column].mean()
        for column in subject_columns
    ]
})

subject_fig = px.bar(
    subject_data,
    x="Subject",
    y="Average Marks",
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

subject_fig.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    showlegend=False,
    yaxis_range=[0, 100],
    xaxis_title="",
    yaxis_title="Average Marks"
)

st.plotly_chart(
    subject_fig,
    use_container_width=True
)

st.divider()

# ---------- MARKS DISTRIBUTION ----------
st.subheader("Student Marks Distribution")

marks_fig = px.histogram(
    df,
    x="average_marks",
    nbins=15,
    color_discrete_sequence=["#52745A"],
    labels={
        "average_marks": "Average Marks",
        "count": "Number of Students"
    }
)

marks_fig.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    xaxis_title="Average Marks",
    yaxis_title="Number of Students"
)

st.plotly_chart(
    marks_fig,
    use_container_width=True
)

st.divider()

# ---------- ATTENDANCE DISTRIBUTION ----------
st.subheader("Attendance Distribution")

attendance_fig = px.histogram(
    df,
    x="attendance",
    nbins=15,
    color_discrete_sequence=["#C4A779"],
    labels={
        "attendance": "Attendance Percentage",
        "count": "Number of Students"
    }
)

attendance_fig.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    xaxis_title="Attendance (%)",
    yaxis_title="Number of Students"
)

st.plotly_chart(
    attendance_fig,
    use_container_width=True
)

st.divider()

# ---------- CLASS-WISE PERFORMANCE ----------
st.subheader("Class-wise Subject Performance")

class_subject_data = df.melt(
    id_vars=["class_name"],
    value_vars=subject_columns,
    var_name="Subject",
    value_name="Marks"
)

class_subject_data["Subject"] = (
    class_subject_data["Subject"].map(subject_names)
)

class_performance = (
    class_subject_data
    .groupby(["class_name", "Subject"], as_index=False)["Marks"]
    .mean()
)

class_fig = px.bar(
    class_performance,
    x="class_name",
    y="Marks",
    color="Subject",
    barmode="group",
    text_auto=".1f",
    color_discrete_sequence=[
        "#52745A",
        "#91A68A",
        "#C4A779",
        "#758B9B",
        "#B58B83"
    ]
)

class_fig.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    yaxis_range=[0, 100],
    xaxis_title="Class",
    yaxis_title="Average Marks",
    legend_title="Subject"
)

st.plotly_chart(
    class_fig,
    use_container_width=True
)

st.divider()

# ---------- CLASS PERFORMANCE SUMMARY ----------
st.subheader("Class Performance Summary")

class_summary = (
    df.groupby("class_name")
    .agg(
        Total_Students=("student_id", "count"),
        Average_Score=("average_marks", "mean"),
        Average_Attendance=("attendance", "mean")
    )
    .reset_index()
)

class_summary = class_summary.rename(
    columns={
        "class_name": "Class",
        "Total_Students": "Total Students",
        "Average_Score": "Average Score",
        "Average_Attendance": "Average Attendance"
    }
)

st.dataframe(
    class_summary.style.format({
        "Average Score": "{:.1f}%",
        "Average Attendance": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)


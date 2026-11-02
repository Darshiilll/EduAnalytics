
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

st.markdown(
    '<div class="eyebrow">WORKSPACE / ANALYTICS</div>',
    unsafe_allow_html=True
)

st.title("Academic Analytics")
st.markdown(
    '<p class="subtitle">Explore student performance and attendance patterns.</p>',
    unsafe_allow_html=True
)

BACKGROUND = "#F7F7F2"
TEXT = "#252923"
GREEN = "#52745A"
LIGHT_GREEN = "#91A68A"
GOLD = "#C4A779"


def style_chart(fig):
    fig.update_layout(
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT
    )
    return fig


# 1. Subject performance
st.divider()
st.subheader("Subject Performance")

subject_df = pd.DataFrame({
    "Subject": ["Mathematics", "Science", "English"],
    "Average Marks": [
        df["math_marks"].mean(),
        df["science_marks"].mean(),
        df["english_marks"].mean()
    ]
})

fig1 = px.bar(
    subject_df,
    x="Subject",
    y="Average Marks",
    color="Subject",
    color_discrete_sequence=[GREEN, LIGHT_GREEN, GOLD],
    text_auto=".1f"
)

fig1.update_layout(
    showlegend=False,
    yaxis_range=[0, 100],
    xaxis_title="",
    yaxis_title="Average marks out of 100"
)

st.plotly_chart(
    style_chart(fig1),
    use_container_width=True
)


# 2. Attendance distribution
st.divider()
st.subheader("Attendance Distribution")

fig2 = px.histogram(
    df,
    x="attendance",
    nbins=10,
    color_discrete_sequence=[LIGHT_GREEN],
    labels={
        "attendance": "Attendance (%)",
        "count": "Number of students"
    }
)

fig2.update_layout(
    xaxis_title="Attendance (%)",
    yaxis_title="Number of students"
)

st.plotly_chart(
    style_chart(fig2),
    use_container_width=True
)


# 3. Student marks distribution
st.divider()
st.subheader("Student Marks Distribution")

fig3 = px.histogram(
    df,
    x="average_marks",
    nbins=10,
    color_discrete_sequence=[GOLD],
    labels={
        "average_marks": "Average marks",
        "count": "Number of students"
    }
)

fig3.update_layout(
    xaxis_title="Average marks out of 100",
    yaxis_title="Number of students"
)

st.plotly_chart(
    style_chart(fig3),
    use_container_width=True
)


# 4. Class performance comparison
st.divider()
st.subheader("Class Performance Comparison")

class_df = (
    df.groupby("class_name")[
        ["math_marks", "science_marks", "english_marks"]
    ]
    .mean()
    .reset_index()
    .melt(
        id_vars="class_name",
        var_name="Subject",
        value_name="Average Marks"
    )
)

class_df["Subject"] = class_df["Subject"].map({
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English"
})

fig4 = px.bar(
    class_df,
    x="class_name",
    y="Average Marks",
    color="Subject",
    barmode="group",
    color_discrete_sequence=[GREEN, LIGHT_GREEN, GOLD],
    labels={"class_name": "Class"}
)

fig4.update_layout(
    yaxis_range=[0, 100],
    xaxis_title="Class",
    yaxis_title="Average marks out of 100"
)

st.plotly_chart(
    style_chart(fig4),
    use_container_width=True
)

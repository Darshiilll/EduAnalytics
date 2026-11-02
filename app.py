
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="EduAnalytics",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load student dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/students.csv")

df = load_data()

# ---------- EDITORIAL LIGHT THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --background: #F7F7F2;
    --surface: #FFFFFF;
    --text: #252923;
    --muted: #777D73;
    --accent: #52745A;
    --accent-light: #EAF0E8;
    --border: #E5E7DF;
}

/* Main page */
.stApp {
    background-color: var(--background);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1440px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* Typography */
h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.6px;
}

h1 {
    font-size: 2.25rem !important;
    font-weight: 800 !important;
}

p, label, li {
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

.eyebrow {
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 8px;
}

.subtitle {
    color: var(--muted);
    font-size: 16px;
    margin-top: -8px;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Metric summaries */
[data-testid="stMetric"] {
    background: var(--surface);
    padding: 22px 24px;
    border: 1px solid var(--border);
    border-radius: 5px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent);
    color: white;
    border: 1px solid var(--accent);
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: 600;
    transition: background 0.2s ease;
}

.stButton > button:hover {
    background: #405D47;
    border-color: #405D47;
    color: white;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: white;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 5px;
}

[data-baseweb="select"] > div {
    background-color: white;
    border-color: var(--border);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F0F1E9;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.1rem !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--text);
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 5px;
}

/* Data tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid var(--border);
    border-radius: 5px;
}

/* Links */
a {
    color: var(--accent) !important;
}

/* Focus states */
input:focus, textarea:focus {
    border-color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        '<div class="eyebrow">EDUCATION · ANALYTICS</div>',
        unsafe_allow_html=True
    )
    st.title("EduAnalytics")
    st.divider()

    st.markdown("**WORKSPACE**")
    st.markdown("Overview")
    st.markdown("Student records")
    st.markdown("Academic analysis")
    st.markdown("Performance prediction")
    st.markdown("Reports")

    st.divider()
    st.caption("Student Performance Intelligence")


# ---------- HOMEPAGE ----------
st.markdown(
    '<div class="eyebrow">DASHBOARD / OVERVIEW</div>',
    unsafe_allow_html=True
)

st.title("Student performance")
st.markdown(
    '<p class="subtitle">A clear view of academic progress, attendance, and outcomes.</p>',
    unsafe_allow_html=True
)

st.divider()

# Overview metrics: placeholders until database integration
st.markdown("### At a glance")


# Calculate dashboard metrics
df["average_marks"] = df[
    ["math_marks", "science_marks", "english_marks"]
].mean(axis=1)

total_students = len(df)
average_marks = df["average_marks"].mean()
pass_rate = (df["average_marks"] >= 40).mean() * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Students enrolled", total_students)

with col2:
    st.metric("Average score", f"{average_marks:.1f}%")

with col3:
    st.metric("Pass rate", f"{pass_rate:.1f}%")


st.markdown("")
st.divider()

# Intro section
left, right = st.columns([1.5, 1], gap="large")

with left:
    st.markdown("### Your academic workspace")
    st.write(
        "EduAnalytics brings student records, academic trends, "
        "attendance insights, and machine learning predictions "
        "into one practical workspace."
    )

    st.markdown("")
    if st.button("Explore the dashboard"):
        st.info(
            "The dashboard will be connected to real student data "
            "in the next development step."
        )

with right:
    st.markdown("### Project status")
    st.markdown(
        """
        **01** · Interface setup

        **02** · Student dataset

        **03** · Database integration

        **04** · Academic analytics

        **05** · Prediction model
        """
    )

st.divider()

st.caption(
    "EduAnalytics · Student Performance Analysis & Prediction"
)
st.divider()

st.subheader("Student records")
st.caption("Preview of the imported student dataset.")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# ---------- ACADEMIC ANALYTICS ----------
st.divider()
st.title("Academic Analytics")
st.caption("Explore student performance and attendance patterns.")

# Calculate average marks by subject
subject_averages = {
    "Mathematics": df["math_marks"].mean(),
    "Science": df["science_marks"].mean(),
    "English": df["english_marks"].mean(),
}

# Chart 1: Subject performance
import plotly.express as px

st.subheader("Subject Performance")

subject_df = pd.DataFrame({
    "Subject": list(subject_averages.keys()),
    "Average Marks": list(subject_averages.values())
})

fig1 = px.bar(
    subject_df,
    x="Subject",
    y="Average Marks",
    color="Subject",
    color_discrete_sequence=["#52745A", "#91A68A", "#C4A779"],
    text_auto=".1f",
)

fig1.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    showlegend=False,
    yaxis_range=[0, 100],
    yaxis_title="Average marks (out of 100)",
    xaxis_title="",
)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Attendance distribution
st.subheader("Attendance Distribution")

fig2 = px.histogram(
    df,
    x="attendance",
    nbins=10,
    color_discrete_sequence=["#78947A"],
    labels={"attendance": "Attendance (%)", "count": "Students"},
)

fig2.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    xaxis_title="Attendance (%)",
    yaxis_title="Number of students",
)

st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Marks distribution
st.subheader("Student Marks Distribution")

df["average_marks"] = df[
    ["math_marks", "science_marks", "english_marks"]
].mean(axis=1)

fig3 = px.histogram(
    df,
    x="average_marks",
    nbins=10,
    color_discrete_sequence=["#C4A779"],
    labels={"average_marks": "Average marks", "count": "Students"},
)

fig3.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    xaxis_title="Average marks (out of 100)",
    yaxis_title="Number of students",
)

st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Class comparison
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
        value_name="Average Marks",
    )
)

class_df["Subject"] = class_df["Subject"].map({
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English",
})

fig4 = px.bar(
    class_df,
    x="class_name",
    y="Average Marks",
    color="Subject",
    barmode="group",
    color_discrete_sequence=["#52745A", "#91A68A", "#C4A779"],
    labels={"class_name": "Class"},
)

fig4.update_layout(
    paper_bgcolor="#F7F7F2",
    plot_bgcolor="#F7F7F2",
    font_color="#252923",
    yaxis_range=[0, 100],
    xaxis_title="Class",
    yaxis_title="Average marks (out of 100)",
)

st.plotly_chart(fig4, use_container_width=True)

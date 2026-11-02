
import streamlit as st
from data_utils import load_data, apply_styles, show_sidebar

st.set_page_config(
    page_title="EduAnalytics",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()
show_sidebar()
df = load_data()

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
st.markdown("### At a glance")

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

st.divider()

left, right = st.columns([1.5, 1], gap="large")

with left:
    st.markdown("### Your academic workspace")
    st.write(
        "EduAnalytics brings student records, academic trends, "
        "attendance insights, and performance analysis into one workspace."
    )

    st.info(
        "Choose Student Records or Academic Analytics "
        "from the sidebar to explore your data."
    )

with right:
    st.markdown("### Project status")
    st.markdown("""
    **01** · Interface setup

    **02** · Student dataset

    **03** · Database integration

    **04** · Academic analytics

    **05** · Prediction model
    """)

st.divider()

st.caption(
    "EduAnalytics · Student Performance Analysis & Prediction"
)

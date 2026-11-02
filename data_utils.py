
import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    df = pd.read_csv("data/students.csv")

    df["average_marks"] = df[
        ["math_marks", "science_marks", "english_marks"]
    ].mean(axis=1)

    return df


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --background: #F7F7F2;
        --surface: #FFFFFF;
        --text: #252923;
        --muted: #777D73;
        --accent: #52745A;
        --border: #E5E7DF;
    }

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

    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }

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

    .stButton > button,
    .stDownloadButton > button {
        background: var(--accent);
        color: white;
        border: 1px solid var(--accent);
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #405D47;
        border-color: #405D47;
        color: white;
    }

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

    [data-testid="stSidebar"] {
        background: #F0F1E9;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 1.1rem !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 5px;
    }

    a {
        color: var(--accent) !important;
    }

    input:focus, textarea:focus {
        border-color: var(--accent) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="eyebrow">EDUCATION · ANALYTICS</div>',
            unsafe_allow_html=True
        )
        st.title("EduAnalytics")
        st.divider()
        st.caption("Student Performance Intelligence")

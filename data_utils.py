
import streamlit as st
import pandas as pd


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("data/students.csv")

    subject_columns = [
        "math_marks",
        "science_marks",
        "english_marks",
        "social_science_marks",
        "computer_marks"
    ]

    df["average_marks"] = df[subject_columns].mean(axis=1)

    return df


# --------------------------------------------------
# GLOBAL APPLICATION STYLING
# --------------------------------------------------

def apply_styles():

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --background: #F7F7F2;
        --surface: #FFFFFF;
        --sidebar: #F0F1E9;
        --text: #252923;
        --muted: #777D73;
        --accent: #52745A;
        --accent-light: #91A68A;
        --gold: #C4A779;
        --border: #E5E7DF;
    }

    /* ---------- MAIN APPLICATION ---------- */

    .stApp {
        background-color: var(--background);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    /* Prevent content from touching screen edges */

    .block-container {
        max-width: 1380px;
        padding-top: 3.5rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* ---------- TYPOGRAPHY ---------- */

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.35rem !important;
        font-weight: 800 !important;
        line-height: 1.3 !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    p, label, li {
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    /* ---------- PAGE LABELS ---------- */

    .eyebrow {
        display: block;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 11px;
        font-weight: 700;
        line-height: 1.6;
        margin-top: 0.25rem;
        margin-bottom: 0.75rem;
        overflow: visible;
    }

    .subtitle {
        color: var(--muted) !important;
        font-size: 15px;
        line-height: 1.7;
        margin-top: 0;
        margin-bottom: 1rem;
    }

    /* ---------- DIVIDERS ---------- */

    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.8rem 0;
    }

    /* ---------- METRIC CARDS ---------- */

    [data-testid="stMetric"] {
        background: var(--surface);
        padding: 22px 24px;
        border: 1px solid var(--border);
        border-radius: 10px;
        min-height: 115px;
        box-shadow: 0 2px 8px rgba(37, 41, 35, 0.025);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 800 !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button,
    .stDownloadButton > button {
        background: var(--accent);
        color: white;
        border: 1px solid var(--accent);
        border-radius: 7px;
        padding: 10px 20px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #405D47;
        border-color: #405D47;
        color: white;
    }

    /* ---------- INPUT FIELDS ---------- */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 7px;
        min-height: 42px;
    }

    [data-baseweb="select"] > div {
        background-color: var(--surface);
        border-color: var(--border);
        border-radius: 7px;
    }

    input:focus,
    textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2.5rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }

    /* ---------- TABLES ---------- */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        width: 100%;
        max-width: 100%;
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] {
        background: var(--surface);
    }

    /* ---------- CHART CONTAINERS ---------- */

    [data-testid="stPlotlyChart"] {
        width: 100%;
        max-width: 100%;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 8px;
        overflow: hidden;
    }

    /* ---------- GENERAL LAYOUT ---------- */

    [data-testid="stHorizontalBlock"] {
        gap: 1.2rem;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.9rem;
    }

    [data-testid="stMainBlockContainer"] {
        overflow: visible;
    }

    /* ---------- LINKS ---------- */

    a {
        color: var(--accent) !important;
    }

    /* ---------- RESPONSIVE LAYOUT ---------- */

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            padding-top: 2.5rem;
        }
    }

    @media (max-width: 600px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.4rem !important;
        }

        [data-testid="stMetric"] {
            padding: 16px;
        }
    }

    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR BRANDING
# --------------------------------------------------

def show_sidebar():

    with st.sidebar:

        st.markdown(
            '<div class="eyebrow">EDUCATION · ANALYTICS</div>',
            unsafe_allow_html=True
        )

        st.title("EduAnalytics")

        st.divider()

        st.caption(
            "Student Performance Intelligence"
        )

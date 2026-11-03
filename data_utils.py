
import streamlit as st
import pandas as pd


# ==================================================
# DATA CONFIGURATION
# ==================================================

SUBJECT_COLUMNS = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]

SUBJECT_NAMES = {
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English",
    "social_science_marks": "Social Science",
    "computer_marks": "Computer"
}

CHART_COLORS = [
    "#52745A",
    "#91A68A",
    "#C4A779",
    "#758B9B",
    "#B58B83"
]


# ==================================================
# DATA LOADING
# ==================================================

@st.cache_data
def load_data():

    df = pd.read_csv("data/students.csv")

    required_columns = SUBJECT_COLUMNS + [
        "student_id",
        "name",
        "class_name",
        "gender",
        "attendance",
        "study_hours"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required dataset columns: {missing_columns}"
        )

    df["average_marks"] = df[SUBJECT_COLUMNS].mean(axis=1)

    return df


# ==================================================
# GLOBAL APPLICATION STYLING
# ==================================================

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

    /* MAIN APPLICATION */

    .stApp {
        background: var(--background);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1380px;
        padding: 3rem 2.5rem 4rem 2.5rem;
    }

    /* TYPOGRAPHY */

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.35rem !important;
        font-weight: 800 !important;
        line-height: 1.3 !important;
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
        font-family: 'DM Sans', sans-serif;
        color: var(--text);
    }

    /* PAGE LABELS */

    .eyebrow {
        display: block;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 11px;
        font-weight: 700;
        line-height: 1.7;
        margin: 0 0 10px 0;
    }

    .subtitle {
        color: var(--muted) !important;
        font-size: 15px;
        line-height: 1.7;
        margin-top: 0;
    }

    /* DIVIDERS */

    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.7rem 0;
    }

    /* METRIC CARDS */

    [data-testid="stMetric"] {
        background: var(--surface);
        padding: 22px 20px;
        border: 1px solid var(--border);
        border-radius: 10px;
        min-height: 115px;
        box-shadow: 0 2px 8px rgba(37, 41, 35, 0.035);
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

    /* BUTTONS */

    .stButton > button,
    .stDownloadButton > button {
        background: var(--accent);
        color: white;
        border: 1px solid var(--accent);
        border-radius: 7px;
        padding: 10px 20px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #405D47;
        border-color: #405D47;
        color: white;
    }

    /* INPUTS */

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
        background: var(--surface);
        border-color: var(--border);
        border-radius: 7px;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1.2rem;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.2rem !important;
    }

    /* SIDEBAR BRANDING */

    .brand-container {
        padding: 12px 5px 22px 5px;
    }

    .brand-logo {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--accent);
        color: white;
        border-radius: 11px;
        font-size: 25px;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        margin-bottom: 15px;
    }

    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-size: 23px;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -1px;
        margin-bottom: 4px;
    }

    .brand-tagline {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
    }

    .sidebar-section {
        color: var(--accent);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        margin: 12px 0;
    }

    /* NAVIGATION */

    [data-testid="stSidebarNav"] {
        display: none;
    }

    [data-testid="stSidebar"] a {
        border-radius: 8px;
    }

    /* TABLES */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        width: 100%;
        max-width: 100%;
        border: 1px solid var(--border);
        border-radius: 9px;
        overflow: hidden;
    }

    /* CHARTS */

    [data-testid="stPlotlyChart"] {
        width: 100%;
        max-width: 100%;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 8px;
        overflow: hidden;
    }

    /* LINKS */

    a {
        color: var(--accent) !important;
    }

    /* RESPONSIVE */

    @media (max-width: 900px) {
        .block-container {
            padding: 2rem 1.5rem 3rem 1.5rem;
        }
    }

    @media (max-width: 600px) {
        .block-container {
            padding: 1.8rem 1rem 2rem 1rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.4rem !important;
        }

        [data-testid="stMetric"] {
            padding: 15px;
        }
    }

    </style>
    """, unsafe_allow_html=True)


# ==================================================
# SIDEBAR NAVIGATION AND BRANDING
# ==================================================

def show_sidebar():

    with st.sidebar:

        st.markdown("""
        <div class="brand-container">
            <div class="brand-logo">E</div>
            <div class="brand-name">EduAnalytics</div>
            <div class="brand-tagline">
                Student Performance Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown(
            '<div class="sidebar-section">MAIN MENU</div>',
            unsafe_allow_html=True
        )

        st.page_link(
            "app.py",
            label="Dashboard",
            icon=":material/dashboard:",
            use_container_width=True
        )

        st.page_link(
            "pages/1_Student_Records.py",
            label="Student Records",
            icon=":material/school:",
            use_container_width=True
        )

        st.page_link(
            "pages/2_Academic_Analytics.py",
            label="Academic Analytics",
            icon=":material/analytics:",
            use_container_width=True
        )

        st.page_link(
            "pages/3_Performance_Prediction.py",
            label="Performance Prediction",
            icon=":material/psychology:",
            use_container_width=True
        )

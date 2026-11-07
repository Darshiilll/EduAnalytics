from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "students.csv"
LOGO_PATH = BASE_DIR / "assets" / "eduanalytics_logo.png"


# ============================================================
# SUBJECT CONFIGURATION
# ============================================================

SUBJECT_COLUMNS = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks",
]

SUBJECT_NAMES = {
    "math_marks": "Mathematics",
    "science_marks": "Science",
    "english_marks": "English",
    "social_science_marks": "Social Science",
    "computer_marks": "Computer",
}

CHART_COLORS = [
    "#52745A",
    "#8BA58D",
    "#B5C9B3",
    "#D6E1D2",
    "#E8EDE3",
]


# ============================================================
# LOAD STUDENT DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    if all(col in df.columns for col in SUBJECT_COLUMNS):
        df["average_marks"] = df[SUBJECT_COLUMNS].mean(axis=1)

    return df


# ============================================================
# GLOBAL STYLING
# ============================================================

def apply_styles():

    st.markdown(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
        );

        /* GLOBAL */

        .stApp {
            background-color: #F7F7F2;
            color: #252923;
            font-family: 'DM Sans', sans-serif;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        h1, h2, h3, h4 {
            font-family: 'Manrope', sans-serif;
            color: #252923;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        /* SIDEBAR */

        [data-testid="stSidebar"] {
            background-color: #F0F1E9;
            border-right: 1px solid #E3E6DC;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0.8rem;
        }

        [data-testid="stSidebarContent"] {
            padding: 1rem 1rem 1.2rem 1rem;
        }

        /* Hide Streamlit's default navigation */

        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }

        /* BRANDING */

        .brand-container {
            text-align: center;
            padding: 0.8rem 0 1.2rem 0;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid #DDE2D6;
        }

        .brand-name {
            font-family: 'Manrope', sans-serif;
            font-size: 1.35rem;
            font-weight: 800;
            color: #252923;
            letter-spacing: -0.6px;
            line-height: 1.4;
        }

        .brand-tagline {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.7rem;
            color: #777D73;
            font-weight: 500;
            letter-spacing: 0.15px;
            margin-top: 0.2rem;
        }

        /* NAVIGATION SECTION HEADINGS */

        .sidebar-section {
            font-size: 0.67rem;
            font-weight: 700;
            color: #8A9185;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            margin: 1.1rem 0 0.5rem 0;
        }

        /* NAVIGATION LINKS */

        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin: 0.12rem 0;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 8px;
            padding: 0.48rem 0.65rem;
            min-height: 40px;
            transition: background-color 0.2s ease;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background-color: #E2E8DD;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] p {
            font-size: 0.84rem;
            font-weight: 500;
            color: #343B33;
            white-space: normal;
            line-height: 1.35;
        }

        /* Outline-style navigation icons */

        [data-testid="stSidebar"] [data-testid="stPageLink"] svg {
            color: #52745A;
            width: 1.1rem;
            height: 1.1rem;
        }

        [data-testid="stSidebar"] hr {
            margin: 0.9rem 0;
            border-color: #DDE2D6;
        }

        /* METRIC CARDS */

        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E7EAE2;
            border-radius: 12px;
            padding: 1rem 1.1rem;
            box-shadow: 0 2px 8px rgba(37, 41, 35, 0.03);
        }

        [data-testid="stMetricLabel"] {
            color: #777D73;
            font-size: 0.82rem;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: #252923;
            font-family: 'Manrope', sans-serif;
            font-size: 1.7rem;
            font-weight: 800;
            overflow: visible;
        }

        /* GENERAL CARDS */

        .custom-card {
            background-color: #FFFFFF;
            border: 1px solid #E7EAE2;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(37, 41, 35, 0.03);
        }

        /* BUTTONS */

        .stButton > button,
        .stDownloadButton > button {
            background-color: #52745A;
            color: #FFFFFF;
            border: 1px solid #52745A;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background-color: #405D47;
            border-color: #405D47;
            color: #FFFFFF;
        }

        /* INPUTS */

        [data-testid="stSelectbox"] > div > div {
            border-radius: 8px;
            border-color: #DDE2D6;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            border-radius: 8px;
            border-color: #DDE2D6;
        }

        /* DATAFRAMES */

        [data-testid="stDataFrame"] {
            border: 1px solid #E7EAE2;
            border-radius: 10px;
            overflow: hidden;
        }

        /* TABS */

        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            color: #777D73;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            color: #52745A !important;
        }

        /* EXPANDERS */

        [data-testid="stExpander"] {
            border: 1px solid #E7EAE2;
            border-radius: 10px;
            background-color: #FFFFFF;
        }

        /* FOOTER */

        .app-footer {
            text-align: center;
            color: #8A9185;
            font-size: 0.75rem;
            padding: 1.5rem 0 0.5rem 0;
            border-top: 1px solid #E7EAE2;
            margin-top: 2rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def show_sidebar():

    with st.sidebar:

        # TEXT-ONLY BRANDING
        st.markdown(
            """
            <div class="brand-container">
                <div class="brand-name">EduAnalytics</div>
                <div class="brand-tagline">
                    Student Performance Intelligence
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # MAIN MENU
        st.markdown(
            '<div class="sidebar-section">MAIN MENU</div>',
            unsafe_allow_html=True,
        )

        st.page_link(
            "app.py",
            label="Dashboard",
            icon=":material/dashboard:",
        )

        st.page_link(
            "pages/1_Student_Records.py",
            label="Student Records",
            icon=":material/people_outline:",
        )

        st.page_link(
            "pages/2_Academic_Analytics.py",
            label="Academic Analytics",
            icon=":material/analytics:",
        )

        # INTELLIGENCE
        st.markdown(
            '<div class="sidebar-section">INTELLIGENCE</div>',
            unsafe_allow_html=True,
        )

        st.page_link(
            "pages/3_Performance_Prediction.py",
            label="Performance Prediction",
            icon=":material/insights:",
        )

        st.page_link(
            "pages/4_Personalized_Recommendations.py",
            label="Personalized Recommendations",
            icon=":material/lightbulb_outline:",
        )

        st.page_link(
            "pages/5_Student_Risk_Detection.py",
            label="Student Risk Detection",
            icon=":material/monitor_heart:",
        )

        # REPORTS
        st.markdown(
            '<div class="sidebar-section">REPORTS</div>',
            unsafe_allow_html=True,
        )

        st.page_link(
            "pages/6_Automated_Reports.py",
            label="Automated Reports",
            icon=":material/description:",
        )

        st.markdown("---")

        st.markdown(
            """
            <div style="
                text-align:center;
                color:#8A9185;
                font-size:0.68rem;
                padding:0.3rem 0;
            ">
                EduAnalytics · Academic Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )
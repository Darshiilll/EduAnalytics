

from pathlib import Path

import pandas as pd
import streamlit as st

from database import (
    DATABASE_PATH,
    STUDENT_COLUMNS,
    initialize_database,
    setup_database,
    get_all_students
)



# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "students.csv"
LOGO_PATH = BASE_DIR / "assets" / "eduanalytics_logo.png"


# ============================================================
# DESIGN SYSTEM
# ============================================================

COLORS = {
    "background": "#F4F6FC",
    "surface": "#FFFFFF",
    "surface_blue": "#E8F1FC",
    "surface_lavender": "#EEF0FF",
    "primary": "#5C7CFA",
    "primary_dark": "#4263D5",
    "secondary": "#A8B6FF",
    "sky": "#B6E3F5",
    "navy": "#243451",
    "text": "#26334D",
    "muted": "#7C879C",
    "border": "#E3E8F2",
    "grid": "#E9EDF5",
    "success": "#39A879",
    "warning": "#E5A94B",
    "danger": "#E36D70",
}


CHART_COLORS = [
    "#5C7CFA",
    "#A8B6FF",
    "#8BCDEB",
    "#B6D8F5",
    "#8DD9B5",
]


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


# ============================================================
# LOAD STUDENT DATA
# ============================================================


# ============================================================
# LOAD STUDENT DATA FROM SQLITE
# ============================================================

@st.cache_data(ttl=10)
def load_data():

    # Check whether this is the first database launch
    database_exists = DATABASE_PATH.exists()

    if not database_exists:
        # Create database and migrate existing CSV records
        setup_database()
    else:
        # Ensure database tables exist
        initialize_database()

    # Fetch student records from SQLite
    students = get_all_students()

    # Convert database records into a DataFrame
    df = pd.DataFrame(students)

    if df.empty:
        df = pd.DataFrame(columns=STUDENT_COLUMNS)

    # Keep the same columns expected by existing pages
    df = df.reindex(columns=STUDENT_COLUMNS)

    # Ensure subject marks are numeric
    for column in SUBJECT_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Calculate average marks
    if all(column in df.columns for column in SUBJECT_COLUMNS):
        df["average_marks"] = df[
            SUBJECT_COLUMNS
        ].mean(axis=1)

    return df


def refresh_student_data():
    """
    Clear cached student data after database changes.
    """
    st.cache_data.clear()



# ============================================================
# GLOBAL STYLING
# ============================================================

def apply_styles():

    st.markdown(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap'
        );

        :root {
            --app-bg: #F4F6FC;
            --surface: #FFFFFF;
            --surface-blue: #E8F1FC;
            --surface-lavender: #EEF0FF;
            --primary: #5C7CFA;
            --primary-dark: #4263D5;
            --secondary: #A8B6FF;
            --navy: #243451;
            --text: #26334D;
            --muted: #7C879C;
            --border: #E3E8F2;
            --grid: #E9EDF5;
            --success: #39A879;
            --warning: #E5A94B;
            --danger: #E36D70;
        }

        /* ==========================================
           GLOBAL APPLICATION
        ========================================== */

        .stApp {
            background-color: var(--app-bg);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        h1, h2, h3, h4, h5 {
            font-family: 'Manrope', sans-serif;
            color: var(--navy);
            font-weight: 750;
            letter-spacing: -0.4px;
        }

        h1 {
            font-size: 2rem;
        }

        h2 {
            font-size: 1.5rem;
        }

        h3 {
            font-size: 1.12rem;
        }

        p, label {
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1600px;
        }

        /* ==========================================
           SIDEBAR
        ========================================== */

        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid var(--border);
            min-width: 250px;
            max-width: 250px;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0.8rem;
        }

        [data-testid="stSidebarContent"] {
            padding: 1rem 0.8rem 1.2rem 0.8rem;
        }

        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }

        /* ==========================================
           BRANDING
        ========================================== */

        .brand-container {
            text-align: left;
            padding: 0.8rem 0.7rem 1.4rem 0.7rem;
            margin-bottom: 1.1rem;
            border-bottom: 1px solid var(--border);
        }

        .brand-name {
            font-family: 'Manrope', sans-serif;
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--navy);
            letter-spacing: -0.6px;
            white-space: nowrap;
            line-height: 1.4;
        }

        .brand-tagline {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.68rem;
            color: var(--muted);
            font-weight: 500;
            letter-spacing: 0.1px;
            margin-top: 0.25rem;
            white-space: nowrap;
        }

        /* ==========================================
           SIDEBAR SECTION HEADINGS
        ========================================== */

        .sidebar-section {
            font-size: 0.66rem;
            font-weight: 700;
            color: #9AA4B6;
            letter-spacing: 1.15px;
            text-transform: uppercase;
            margin: 1.3rem 0 0.55rem 0.65rem;
        }

        /* ==========================================
           SIDEBAR NAVIGATION
        ========================================== */

        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin: 0.2rem 0;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 9px;
            padding: 0.55rem 0.7rem;
            min-height: 42px;
            transition: background-color 0.2s ease;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background-color: #F0F3FF;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] p {
            font-size: 0.79rem;
            font-weight: 600;
            color: var(--text);
            white-space: normal;
            line-height: 1.35;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] svg {
            color: #7183B5;
            width: 1.12rem;
            height: 1.12rem;
        }

        [data-testid="stSidebar"] hr {
            margin: 1rem 0;
            border-color: var(--border);
        }

        /* ==========================================
           PAGE HEADERS
        ========================================== */

        .eyebrow {
            color: var(--primary);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 1.5px;
            margin-bottom: 0.35rem;
        }

        .subtitle {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }

        /* ==========================================
           METRIC CARDS
        ========================================== */

        [data-testid="stMetric"] {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            box-shadow: 0 3px 12px rgba(36, 52, 81, 0.035);
            min-width: 0;
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: 0.79rem;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--navy);
            font-family: 'Manrope', sans-serif;
            font-size: 1.7rem;
            font-weight: 800;
            overflow: visible;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.76rem;
            font-weight: 600;
        }

        /* ==========================================
           GENERAL CARDS
        ========================================== */

        .custom-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 1.25rem;
            box-shadow: 0 3px 12px rgba(36, 52, 81, 0.035);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(36, 52, 81, 0.025);
        }

        /* ==========================================
           BUTTONS
        ========================================== */

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            background-color: var(--primary);
            color: #FFFFFF;
            border: 1px solid var(--primary);
            border-radius: 9px;
            min-height: 40px;
            font-family: 'DM Sans', sans-serif;
            font-weight: 650;
            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            background-color: var(--primary-dark);
            border-color: var(--primary-dark);
            color: #FFFFFF;
        }

        .stButton > button:focus,
        .stDownloadButton > button:focus {
            box-shadow: 0 0 0 0.2rem rgba(92, 124, 250, 0.2);
            border-color: var(--primary);
        }

        /* ==========================================
           INPUTS
        ========================================== */

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea {
            border-radius: 9px;
            border-color: var(--border);
            background-color: #FFFFFF;
            color: var(--text);
        }

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            border-radius: 9px;
            border-color: var(--border);
            background-color: #FFFFFF;
        }

        /* ==========================================
           SLIDERS
        ========================================== */

        [data-testid="stSlider"] [role="slider"] {
            background-color: var(--primary);
        }

        /* ==========================================
           DATA TABLES
        ========================================== */

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            background-color: #FFFFFF;
        }

        /* ==========================================
           TABS
        ========================================== */

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.8rem;
            border-bottom: 1px solid var(--border);
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--muted);
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            color: var(--primary) !important;
        }

        /* ==========================================
           EXPANDERS
        ========================================== */

        [data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            background-color: #FFFFFF;
        }

        [data-testid="stExpander"] summary {
            color: var(--navy);
            font-weight: 600;
        }

        /* ==========================================
           ALERTS
        ========================================== */

        [data-testid="stAlert"] {
            border-radius: 11px;
        }

        /* ==========================================
           PROGRESS BARS
        ========================================== */

        [data-testid="stProgressBar"] > div > div {
            background-color: var(--primary);
        }

        /* ==========================================
           DIVIDERS
        ========================================== */

        hr {
            border-color: var(--border) !important;
        }

        /* ==========================================
           FOOTER
        ========================================== */

        .app-footer {
            text-align: center;
            color: #9AA4B6;
            font-size: 0.74rem;
            padding: 1.5rem 0 0.5rem 0;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }

        /* ==========================================
           RESPONSIVE LAYOUT
        ========================================== */

        @media (max-width: 768px) {

            .block-container {
                padding-top: 1rem;
                padding-bottom: 1.5rem;
            }

            h1 {
                font-size: 1.65rem;
            }

            [data-testid="stMetric"] {
                padding: 0.8rem;
            }

            [data-testid="stMetricValue"] {
                font-size: 1.4rem;
            }
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
    "pages/7_Student_Management.py",
    label="Student Management",
    icon=":material/manage_accounts:",
)

        st.page_link(
            "pages/2_Academic_Analytics.py",
            label="Academic Analytics",
            icon=":material/analytics:",
        )
        st.page_link(
    "pages/8_Academic_Progress_Tracking.py",
    label="Academic Progress Tracking",
    icon=":material/trending_up:",
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
                text-align:left;
                color:#9AA4B6;
                font-size:0.68rem;
                padding:0.3rem 0.7rem;
                line-height:1.6;
            ">
                EduAnalytics<br>
                Academic Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )

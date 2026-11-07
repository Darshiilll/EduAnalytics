
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from data_utils import load_data, apply_styles, show_sidebar

st.set_page_config(
    page_title="Performance Prediction | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()
show_sidebar()

st.markdown("""
<style>
.stApp { background:#F4F6FC; color:#243451; }
h1,h2,h3 { color:#243451 !important; font-family:Manrope,sans-serif; }
.page-eyebrow {
    color:#5C7CFA; font-size:.68rem; font-weight:800;
    letter-spacing:1.5px; margin-bottom:7px;
}
.page-subtitle { color:#8792A5; font-size:.86rem; margin-bottom:18px; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:14px; box-shadow:0 3px 12px rgba(36,52,81,.035);
}
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:13px; padding:15px;
}
[data-testid="stMetricLabel"] { color:#73819A; }
[data-testid="stMetricValue"] { color:#243451; font-family:Manrope,sans-serif; }
.stButton button,.stFormSubmitButton button {
    background:#5C7CFA; color:white; border:1px solid #5C7CFA;
    border-radius:9px; font-weight:650;
}
.stButton button:hover,.stFormSubmitButton button:hover {
    background:#4969E6; color:white; border-color:#4969E6;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# DATA AND MODEL
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records found. Check data/students.csv.")
    st.stop()

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_DIR / "models" / "student_performance_model.joblib"

if not MODEL_PATH.exists():
    st.error(
        "The prediction model was not found. "
        "Please run python train_model.py first."
    )
    st.stop()

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    st.error(f"The prediction model could not be loaded: {exc}")
    st.stop()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">INTELLIGENCE / MACHINE LEARNING</div>',
            unsafe_allow_html=True)
st.title("Performance Prediction")
st.markdown(
    '<div class="page-subtitle">Estimate academic performance using '
    'attendance and daily study hours.</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# MODEL OVERVIEW
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">PREDICTION MODEL</div>',
            unsafe_allow_html=True)
st.subheader("Model Overview")

m1, m2, m3 = st.columns(3)
m1.metric("Model Type", "Linear Regression")
m2.metric("Evaluation Training Set", "80 records")
m3.metric("Test R² Score", "0.578")

st.caption(
    "The model was evaluated using an 80/20 train-test split. "
    "The saved final model was subsequently fitted using all available records."
)


# ------------------------------------------------------------
# INPUT FORM
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">STUDENT INPUTS</div>',
            unsafe_allow_html=True)
st.subheader("Enter Student Information")
st.caption(
    "Adjust the inputs to explore how the model estimates academic performance."
)

with st.container(border=True):
    with st.form("prediction_form"):
        st.markdown("**Learning habits**")

        col1, col2 = st.columns(2, gap="large")

        with col1:
            attendance = st.slider(
                "Attendance Percentage",
                min_value=0,
                max_value=100,
                value=75,
                step=1,
                help="Enter the student's attendance percentage."
            )

        with col2:
            study_hours = st.slider(
                "Daily Study Hours",
                min_value=0.0,
                max_value=12.0,
                value=3.0,
                step=0.5,
                help="Average number of hours spent studying daily."
            )

        predict_button = st.form_submit_button(
            "Generate Prediction",
            use_container_width=True
        )


# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

if predict_button:

    input_data = pd.DataFrame(
        [[attendance, study_hours]],
        columns=["attendance", "study_hours"]
    )

    predicted_score = float(model.predict(input_data)[0])
    predicted_score = max(0, min(100, predicted_score))
    predicted_score = round(predicted_score, 1)

    dataset_average = round(float(df["average_marks"].mean()), 1)
    difference = round(predicted_score - dataset_average, 1)

    if predicted_score >= 70:
        category = "Strong Performance"
        category_color = "#328B69"
        category_bg = "#E5F6EE"
        recommendation = (
            "The estimated performance is strong. "
            "Continue maintaining consistent study habits."
        )
    elif predicted_score >= 50:
        category = "Moderate Performance"
        category_color = "#A97822"
        category_bg = "#FFF4DD"
        recommendation = (
            "The estimated performance is moderate. "
            "Consistent revision and study habits may help."
        )
    else:
        category = "Needs Improvement"
        category_color = "#C34E5B"
        category_bg = "#FCEBED"
        recommendation = (
            "The estimate indicates a need for additional academic "
            "support and regular revision."
        )

    st.markdown('<div class="page-eyebrow">PREDICTION RESULTS</div>',
                unsafe_allow_html=True)
    st.subheader("Estimated Academic Performance")

    r1, r2, r3 = st.columns(3)
    r1.metric("Predicted Average Marks", f"{predicted_score}/100")
    r2.metric("Dataset Average", f"{dataset_average}/100")
    r3.metric("Difference from Average", f"{difference:+.1f} marks")

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="background:{category_bg};border-radius:12px;
            padding:20px;border:1px solid #E3E8F2;">
                <div style="font-size:.68rem;letter-spacing:1.4px;
                color:#73819A;font-weight:800;">PERFORMANCE CATEGORY</div>
                <div style="font-family:Manrope,sans-serif;font-size:1.5rem;
                font-weight:800;color:{category_color};margin:8px 0;">
                    {category}
                </div>
                <div style="font-size:.84rem;color:#52617A;">
                    {recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("")

        progress_col, score_col = st.columns([3, 1])
        with progress_col:
            st.progress(predicted_score / 100)
        with score_col:
            st.markdown(
                f"<div style='text-align:right;color:#243451;"
                f"font-weight:750;'>{predicted_score:.1f}%</div>",
                unsafe_allow_html=True
            )

    st.info(
        "This result is a model-generated estimate, not a guaranteed exam score. "
        "Actual academic performance can depend on many factors not included "
        "in this model."
    )


# ------------------------------------------------------------
# MODEL INFORMATION
# ------------------------------------------------------------

st.markdown('<div class="page-eyebrow">MODEL INFORMATION</div>',
            unsafe_allow_html=True)
st.subheader("Understanding the Prediction")

with st.container(border=True):
    st.markdown("**Input features**")

    f1, f2 = st.columns(2)

    with f1:
        st.markdown("**Attendance**")
        st.caption("Student attendance percentage.")

    with f2:
        st.markdown("**Study Hours**")
        st.caption("Average number of hours spent studying daily.")

    st.divider()

    st.markdown("**How it works**")
    st.write(
        "Linear Regression estimates the relationship between the two input "
        "features and average marks in the training dataset."
    )

    st.markdown("**Important limitations**")
    st.write(
        "The model uses a relatively small dataset and only two input features. "
        "Its output should be treated as an estimate for exploration, not as "
        "a definitive prediction of a student's future examination result."
    )

st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Student Performance Prediction
</div>
""", unsafe_allow_html=True)

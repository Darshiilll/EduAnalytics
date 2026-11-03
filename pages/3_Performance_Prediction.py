
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from data_utils import load_data, apply_styles, show_sidebar


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Performance Prediction | EduAnalytics",
    page_icon="E",
    layout="wide"
)

apply_styles()

df = load_data()
show_sidebar()


# ==================================================
# 2. LOAD TRAINED MODEL
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_DIR
    / "models"
    / "student_performance_model.joblib"
)

if not MODEL_PATH.exists():
    st.error(
        "The prediction model was not found. "
        "Please run python train_model.py first."
    )
    st.stop()

model = joblib.load(MODEL_PATH)


# ==================================================
# 3. PAGE HEADER
# ==================================================

st.markdown(
    '<div class="eyebrow">WORKSPACE / PREDICTION</div>',
    unsafe_allow_html=True
)

st.title("Student Performance Prediction")

st.markdown(
    """
    <p class="subtitle">
        Estimate academic performance using attendance
        and daily study hours.
    </p>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Enter student details below to generate an estimated "
    "average academic score using our trained machine learning model."
)


# ==================================================
# 4. MODEL OVERVIEW
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">MACHINE LEARNING</div>',
    unsafe_allow_html=True
)

st.subheader("Prediction Model")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.metric(
        "Model",
        "Linear Regression"
    )

with col2:
    st.metric(
        "Training Records",
        "80"
    )

with col3:
    st.metric(
        "Test R² Score",
        "0.578"
    )


# ==================================================
# 5. PREDICTION INPUTS
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">STUDENT INPUTS</div>',
    unsafe_allow_html=True
)

st.subheader("Enter Student Information")

st.caption(
    "Adjust the values to explore how the model estimates "
    "student academic performance."
)

with st.form("prediction_form"):

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


# ==================================================
# 6. GENERATE PREDICTION
# ==================================================

if predict_button:

    input_data = pd.DataFrame(
        [[attendance, study_hours]],
        columns=[
            "attendance",
            "study_hours"
        ]
    )

    predicted_score = model.predict(input_data)[0]

    # Keep estimated marks within the valid score range
    predicted_score = max(
        0,
        min(100, predicted_score)
    )

    predicted_score = round(
        float(predicted_score),
        1
    )

    dataset_average = round(
        float(df["average_marks"].mean()),
        1
    )

    # Performance category
    if predicted_score >= 70:
        category = "Strong Performance"
        category_color = "#52745A"
        recommendation = (
            "The estimated performance is strong. "
            "Continue maintaining consistent study habits."
        )

    elif predicted_score >= 50:
        category = "Moderate Performance"
        category_color = "#C4A779"
        recommendation = (
            "The estimated performance is moderate. "
            "Consistent revision and study habits may help."
        )

    else:
        category = "Needs Improvement"
        category_color = "#B58B83"
        recommendation = (
            "The estimated performance indicates a need "
            "for additional academic support and regular revision."
        )

    difference = predicted_score - dataset_average


    # ==================================================
    # 7. DISPLAY RESULTS
    # ==================================================

    st.divider()

    st.markdown(
        '<div class="eyebrow">PREDICTION RESULTS</div>',
        unsafe_allow_html=True
    )

    st.subheader("Estimated Academic Performance")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Predicted Average Marks",
            f"{predicted_score}/100"
        )

    with result_col2:
        st.metric(
            "Dataset Average",
            f"{dataset_average}/100"
        )

    with result_col3:
        st.metric(
            "Difference from Average",
            f"{difference:+.1f} marks"
        )

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #E5E7DF;
            border-left:5px solid {category_color};
            border-radius:10px;
            padding:22px;
            margin-top:20px;
        ">
            <div style="
                color:#777D73;
                font-size:12px;
                letter-spacing:2px;
                font-weight:600;
                margin-bottom:10px;
            ">
                PERFORMANCE CATEGORY
            </div>
            <div style="
                color:{category_color};
                font-size:25px;
                font-weight:700;
                margin-bottom:8px;
            ">
                {category}
            </div>
            <div style="
                color:#777D73;
                font-size:14px;
            ">
                {recommendation}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "This result is a model-generated estimate, not a guaranteed "
        "exam score. Actual academic performance can depend on many "
        "other factors not included in this model."
    )


# ==================================================
# 8. MODEL LIMITATIONS
# ==================================================

st.divider()

st.markdown(
    '<div class="eyebrow">MODEL INFORMATION</div>',
    unsafe_allow_html=True
)

st.subheader("Understanding the Prediction")

st.write(
    """
    This model uses two input features:

    - **Attendance:** Student attendance percentage.
    - **Study Hours:** Average daily study time.

    Linear Regression identifies relationships between these inputs
    and historical average marks in the training dataset.
    """
)

st.caption(
    "EduAnalytics · Student Performance Prediction"
)

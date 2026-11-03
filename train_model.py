
import os
import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

DATA_PATH = "data/students.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "student_performance_model.joblib"
)

SUBJECT_COLUMNS = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]

FEATURE_COLUMNS = [
    "attendance",
    "study_hours"
]


# ==========================================
# 2. LOAD AND PREPARE DATA
# ==========================================

def prepare_data():

    df = pd.read_csv(DATA_PATH)

    required_columns = SUBJECT_COLUMNS + FEATURE_COLUMNS

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError(
            "Dataset contains missing values. "
            "Please clean the data before training."
        )

    # Calculate average marks across five subjects
    df["average_marks"] = df[SUBJECT_COLUMNS].mean(axis=1)

    X = df[FEATURE_COLUMNS]
    y = df["average_marks"]

    return X, y


# ==========================================
# 3. TRAIN AND EVALUATE MODEL
# ==========================================

def train_model():

    X, y = prepare_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    model = LinearRegression()

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # Evaluation metrics
    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    # Train final model using all available records
    final_model = LinearRegression()
    final_model.fit(X, y)

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(
        final_model,
        MODEL_PATH
    )

    # Display results
    print("\n================================")
    print(" EDUANALYTICS MODEL EVALUATION")
    print("================================")

    print(f"Total records: {len(X)}")
    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")

    print("\nModel Performance:")
    print(f"MAE  : {mae:.2f} marks")
    print(f"RMSE : {rmse:.2f} marks")
    print(f"R²   : {r2:.3f}")

    print("\nModel Coefficients:")
    for feature, coefficient in zip(
        FEATURE_COLUMNS,
        final_model.coef_
    ):
        print(f"{feature}: {coefficient:.3f}")

    print("\nModel saved successfully:")
    print(MODEL_PATH)

    print("================================\n")

    return final_model


# ==========================================
# 4. RUN TRAINING
# ==========================================

if __name__ == "__main__":
    train_model()

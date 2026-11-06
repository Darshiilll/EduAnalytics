
def assess_student_risk(student):
    """
    Classify a student's academic risk using marks,
    attendance and study habits.

    These are initial heuristic rules, not validated
    academic or institutional standards.
    """

    average_marks = float(student["average_marks"])
    attendance = float(student["attendance"])
    study_hours = float(student["study_hours"])

    subject_columns = [
        "math_marks",
        "science_marks",
        "english_marks",
        "social_science_marks",
        "computer_marks"
    ]

    weak_subjects = [
        column for column in subject_columns
        if float(student[column]) < 40
    ]

    risk_score = 0
    risk_factors = []

    # Overall academic performance
    if average_marks < 40:
        risk_score += 3
        risk_factors.append("Overall average is below 40%.")
    elif average_marks < 50:
        risk_score += 2
        risk_factors.append("Overall average is below 50%.")
    elif average_marks < 60:
        risk_score += 1
        risk_factors.append("Overall average needs improvement.")

    # Attendance
    if attendance < 65:
        risk_score += 3
        risk_factors.append("Attendance is below 65%.")
    elif attendance < 75:
        risk_score += 2
        risk_factors.append("Attendance is below 75%.")
    elif attendance < 85:
        risk_score += 1
        risk_factors.append("Attendance could be improved.")

    # Study habits
    if study_hours < 1:
        risk_score += 2
        risk_factors.append("Daily study time is below 1 hour.")
    elif study_hours < 2:
        risk_score += 1
        risk_factors.append("Daily study time is below 2 hours.")

    # Subject-level performance
    if len(weak_subjects) >= 3:
        risk_score += 2
        risk_factors.append(
            f"{len(weak_subjects)} subjects have marks below 40."
        )
    elif len(weak_subjects) >= 1:
        risk_score += 1
        risk_factors.append(
            f"{len(weak_subjects)} subject(s) have marks below 40."
        )

    # Final risk classification
    if risk_score >= 6:
        risk_level = "High"
    elif risk_score >= 3:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    if not risk_factors:
        risk_factors.append(
            "No major risk indicators were identified by these rules."
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "weak_subjects": weak_subjects
    }

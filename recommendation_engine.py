
import pandas as pd


# ==================================================
# 1. CONFIGURATION
# ==================================================

SUBJECT_COLUMNS = {
    "Mathematics": "math_marks",
    "Science": "science_marks",
    "English": "english_marks",
    "Social Science": "social_science_marks",
    "Computer": "computer_marks"
}

PASS_MARKS = 40
IMPROVEMENT_MARKS = 60
LOW_ATTENDANCE = 75
LOW_STUDY_HOURS = 2


# ==================================================
# 2. RECOMMENDATION GENERATOR
# ==================================================

def generate_recommendations(student):

    recommendations = []

    average_marks = float(student["average_marks"])
    attendance = float(student["attendance"])
    study_hours = float(student["study_hours"])

    # --------------------------------------------------
    # OVERALL ACADEMIC PERFORMANCE
    # --------------------------------------------------

    if average_marks < PASS_MARKS:

        recommendations.append({
            "category": "Academic Performance",
            "priority": "High",
            "observation": (
                f"Overall average is {average_marks:.1f}/100."
            ),
            "recommendation": (
                "Arrange an academic support session, identify "
                "difficult topics and establish a structured "
                "revision plan."
            )
        })

    elif average_marks < IMPROVEMENT_MARKS:

        recommendations.append({
            "category": "Academic Performance",
            "priority": "Medium",
            "observation": (
                f"Overall average is {average_marks:.1f}/100."
            ),
            "recommendation": (
                "Focus on weaker topics, practise regularly "
                "and review mistakes from previous assessments."
            )
        })

    else:

        recommendations.append({
            "category": "Academic Performance",
            "priority": "Low",
            "observation": (
                f"Overall average is {average_marks:.1f}/100."
            ),
            "recommendation": (
                "Maintain consistent academic habits and "
                "continue practising challenging topics."
            )
        })

    # --------------------------------------------------
    # SUBJECT-WISE PERFORMANCE
    # --------------------------------------------------

    weak_subjects = []
    improving_subjects = []

    for subject, column in SUBJECT_COLUMNS.items():

        marks = float(student[column])

        if marks < PASS_MARKS:
            weak_subjects.append(subject)

        elif marks < IMPROVEMENT_MARKS:
            improving_subjects.append(subject)

    for subject in weak_subjects:

        recommendations.append({
            "category": "Subject Improvement",
            "priority": "High",
            "observation": (
                f"{subject} marks are below 40."
            ),
            "recommendation": (
                f"Provide additional {subject} practice, "
                "review foundational concepts and arrange "
                "targeted teacher support."
            )
        })

    for subject in improving_subjects:

        recommendations.append({
            "category": "Subject Improvement",
            "priority": "Medium",
            "observation": (
                f"{subject} marks are between 40 and 59."
            ),
            "recommendation": (
                f"Strengthen {subject} through regular exercises, "
                "topic revision and practice assessments."
            )
        })

    # --------------------------------------------------
    # ATTENDANCE ANALYSIS
    # --------------------------------------------------

    if attendance < LOW_ATTENDANCE:

        recommendations.append({
            "category": "Attendance",
            "priority": "High",
            "observation": (
                f"Attendance is {attendance:.1f}%."
            ),
            "recommendation": (
                "Discuss attendance barriers with the student "
                "and encourage more consistent classroom "
                "participation."
            )
        })

    elif attendance >= 90:

        recommendations.append({
            "category": "Attendance",
            "priority": "Low",
            "observation": (
                f"Attendance is {attendance:.1f}%."
            ),
            "recommendation": (
                "Maintain the student's consistent attendance "
                "and classroom participation."
            )
        })

    # --------------------------------------------------
    # STUDY HABITS
    # --------------------------------------------------

    if study_hours < LOW_STUDY_HOURS:

        recommendations.append({
            "category": "Study Habits",
            "priority": "Medium",
            "observation": (
                f"Daily study time is {study_hours:.1f} hours."
            ),
            "recommendation": (
                "Help the student establish a realistic daily "
                "study timetable with short, regular revision "
                "sessions."
            )
        })

    elif study_hours >= 4:

        recommendations.append({
            "category": "Study Habits",
            "priority": "Low",
            "observation": (
                f"Daily study time is {study_hours:.1f} hours."
            ),
            "recommendation": (
                "Maintain a balanced study routine with "
                "regular breaks and sufficient rest."
            )
        })

    # --------------------------------------------------
    # MULTIPLE SUBJECT SUPPORT
    # --------------------------------------------------

    if len(weak_subjects) >= 2:

        recommendations.append({
            "category": "Additional Support",
            "priority": "High",
            "observation": (
                f"{len(weak_subjects)} subjects have marks below 40."
            ),
            "recommendation": (
                "Arrange a teacher review to identify common "
                "learning difficulties and prepare an individual "
                "academic support plan."
            )
        })

    # --------------------------------------------------
    # GENERAL POSITIVE FEEDBACK
    # --------------------------------------------------

    if (
        average_marks >= 70
        and attendance >= 90
        and len(weak_subjects) == 0
    ):

        recommendations.append({
            "category": "Positive Progress",
            "priority": "Low",
            "observation": (
                "Strong academic performance and consistent attendance."
            ),
            "recommendation": (
                "Recognize the student's progress and encourage "
                "continued academic development."
            )
        })

    return recommendations


# ==================================================
# 3. RECOMMENDATION SUMMARY
# ==================================================

def get_recommendation_summary(recommendations):

    return {
        "total": len(recommendations),

        "high": sum(
            item["priority"] == "High"
            for item in recommendations
        ),

        "medium": sum(
            item["priority"] == "Medium"
            for item in recommendations
        ),

        "low": sum(
            item["priority"] == "Low"
            for item in recommendations
        )
    }


import sqlite3
import csv
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import re
import pandas as pd
import math


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATABASE_PATH = DATA_DIR / "eduanalytics.db"
CSV_PATH = DATA_DIR / "students.csv"


# Existing EduAnalytics student columns
STUDENT_COLUMNS = [
    "student_id",
    "name",
    "class_name",
    "gender",
    "average_marks",
    "attendance",
    "study_hours",
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]


EXAM_SUBJECTS = [
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks",
]

NUMERIC_COLUMNS = [
    "average_marks",
    "attendance",
    "study_hours",
    "math_marks",
    "science_marks",
    "english_marks",
    "social_science_marks",
    "computer_marks"
]


# =====================================================
# DATABASE CONNECTION
# =====================================================

@contextmanager
def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# =====================================================
# CREATE DATABASE TABLES
# =====================================================

def initialize_database():

    with get_connection() as conn:

        # Student records
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT,
                gender TEXT,
                average_marks REAL,
                attendance REAL,
                study_hours REAL,
                math_marks REAL,
                science_marks REAL,
                english_marks REAL,
                social_science_marks REAL,
                computer_marks REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Examination details
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_name TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                max_marks REAL NOT NULL DEFAULT 100,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exam_name, exam_date)
            )
            
        """)
               # Check whether max_marks column exists
        exam_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(exams)"
            ).fetchall()
        }

        # Add max_marks to existing databases if missing
        if "max_marks" not in exam_columns:
            conn.execute("""
                ALTER TABLE exams
                ADD COLUMN max_marks REAL NOT NULL DEFAULT 100
            """)
        

        

        # Subject-wise examination results
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (exam_id)
                    REFERENCES exams(exam_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,

                UNIQUE(exam_id, student_id, subject)
            )
        """)

        # Future login system
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        


    return True


# =====================================================
# CSV MIGRATION
# =====================================================

def convert_value(value, column):

    if value is None or str(value).strip() == "":
        return None

    value = str(value).strip()

    if column in NUMERIC_COLUMNS:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    return value


def migrate_students_from_csv(csv_path=None):

    csv_path = Path(csv_path) if csv_path else CSV_PATH

    if not csv_path.exists():
        return {
            "success": False,
            "message": f"CSV file not found: {csv_path}",
            "imported": 0,
            "skipped": 0
        }

    imported = 0
    skipped = 0

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("The CSV file has no column headers.")

        available_columns = {
            column.strip().lower()
            for column in reader.fieldnames
            if column
        }

        if "student_id" not in available_columns:
            raise ValueError(
                "CSV must contain a student_id column."
            )

        with get_connection() as conn:

            for original_row in reader:

                row = {
                    str(key).strip().lower(): value
                    for key, value in original_row.items()
                    if key is not None
                }

                student_id = str(
                    row.get("student_id", "")
                ).strip()

                if not student_id:
                    skipped += 1
                    continue

                values = {}

                for column in STUDENT_COLUMNS:
                    values[column] = convert_value(
                        row.get(column),
                        column
                    )

                if not values["name"]:
                    skipped += 1
                    continue

                columns = ", ".join(STUDENT_COLUMNS)
                placeholders = ", ".join(
                    ["?"] * len(STUDENT_COLUMNS)
                )

                cursor = conn.execute(
                    f"""
                    INSERT OR IGNORE INTO students
                    ({columns})
                    VALUES ({placeholders})
                    """,
                    tuple(values[column] for column in STUDENT_COLUMNS)
                )

                if cursor.rowcount == 1:
                    imported += 1
                else:
                    skipped += 1

    return {
        "success": True,
        "message": "CSV migration completed.",
        "imported": imported,
        "skipped": skipped
    }


# =====================================================
# STUDENT OPERATIONS
# =====================================================

def get_all_students():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM students
            ORDER BY name
        """).fetchall()

        return [dict(row) for row in rows]


def get_student(student_id):

    with get_connection() as conn:

        row = conn.execute("""
            SELECT *
            FROM students
            WHERE student_id = ?
        """, (str(student_id),)).fetchone()

        return dict(row) if row else None
    

def validate_student_id(student_id):
    student_id = str(student_id).strip().upper()

    if not re.fullmatch(r"STUD\d{4}", student_id):
        raise ValueError(
            "Invalid Student ID. Use format STUD0001 (STUD followed by 4 digits)."
        )

    return student_id



def add_student(student):

    required_columns = STUDENT_COLUMNS

    values = {column: student.get(column) for column in required_columns}
    values["student_id"] = validate_student_id(values["student_id"])

    if not values["student_id"] or not values["name"]:
        raise ValueError("Student ID and name are required.")

    # Convert numeric fields consistently
    for column in NUMERIC_COLUMNS:
        if values[column] is not None:
            values[column] = float(values[column])

    columns = ", ".join(STUDENT_COLUMNS)
    placeholders = ", ".join(["?"] * len(STUDENT_COLUMNS))

    with get_connection() as conn:
        conn.execute(
            f"""
            INSERT INTO students ({columns})
            VALUES ({placeholders})
            """,
            tuple(values[column] for column in STUDENT_COLUMNS)
        )

    return True


def update_student(student_id, updates):

    student_id = validate_student_id(student_id)



    allowed_columns = set(STUDENT_COLUMNS) - {"student_id"}

    valid_updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_columns
    }

    if not valid_updates:
        raise ValueError("No valid student fields supplied.")

    # Convert numeric fields consistently
    for column in NUMERIC_COLUMNS:
        if column in valid_updates and valid_updates[column] is not None:
            valid_updates[column] = float(valid_updates[column])

    assignments = ", ".join(
        f"{column} = ?" for column in valid_updates
    )

    query_values = list(valid_updates.values())
    query_values.extend([
        datetime.now().isoformat(timespec="seconds"),
        str(student_id)
    ])

    with get_connection() as conn:

        cursor = conn.execute(
            f"""
            UPDATE students
            SET {assignments},
                updated_at = ?
            WHERE student_id = ?
            """,
            query_values
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"Student ID {student_id} was not found."
            )

    return True


def delete_student(student_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM students
            WHERE student_id = ?
        """, (str(student_id),))

        if cursor.rowcount == 0:
            raise ValueError("Student not found.")

    return True


# =====================================================
# EXAM OPERATIONS
# =====================================================

# =====================================================
# EXAM OPERATIONS
# =====================================================

def add_exam(exam_name, exam_date, max_marks=100):
    exam_name = str(exam_name).strip()
    max_marks = float(max_marks)

    if not exam_name:
        raise ValueError("Examination name is required.")

    if max_marks <= 0:
        raise ValueError("Maximum marks must be greater than zero.")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO exams (
                exam_name,
                exam_date,
                max_marks
            )
            VALUES (?, ?, ?)
            ON CONFLICT(exam_name, exam_date) DO NOTHING
        """, (exam_name, exam_date, max_marks))

        row = conn.execute("""
            SELECT exam_id, max_marks
            FROM exams
            WHERE exam_name = ? AND exam_date = ?
        """, (exam_name, exam_date)).fetchone()

        if row["max_marks"] != max_marks:
            raise ValueError(
                "An examination with this name and date already exists "
                "with a different maximum mark. Edit the existing exam "
                "instead of creating a duplicate."
            )

        return row["exam_id"]


def update_exam_max_marks(exam_id, max_marks):
    max_marks = float(max_marks)

    if not math.isfinite(max_marks) or max_marks <= 0:
        raise ValueError(
            "Maximum marks must be a valid number greater than zero."
        )

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE exams
            SET max_marks = ?
            WHERE exam_id = ?
        """, (max_marks, exam_id))

        if cursor.rowcount == 0:
            raise ValueError("Examination not found.")

        invalid_result = conn.execute("""
            SELECT student_id, subject, marks
            FROM exam_results
            WHERE exam_id = ?
              AND marks > ?
            LIMIT 1
        """, (exam_id, max_marks)).fetchone()

        if invalid_result:
            raise ValueError(
                f"Cannot reduce maximum marks to {max_marks}. "
                f"{invalid_result['student_id']} has "
                f"{invalid_result['marks']} marks in "
                f"{invalid_result['subject']}."
            )

    return True

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE exams
            SET max_marks = ?
            WHERE exam_id = ?
        """, (max_marks, exam_id))

        if cursor.rowcount == 0:
            raise ValueError("Examination not found.")

        # Existing marks must still fit within the new maximum.
        invalid_result = conn.execute("""
            SELECT student_id, subject, marks
            FROM exam_results
            WHERE exam_id = ?
              AND marks > ?
            LIMIT 1
        """, (exam_id, max_marks)).fetchone()

        if invalid_result:
            raise ValueError(
                f"Cannot reduce maximum marks to {max_marks}. "
                f"{invalid_result['student_id']} has "
                f"{invalid_result['marks']} marks in "
                f"{invalid_result['subject']}."
            )


def get_all_exams():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT exam_id, exam_name, exam_date, max_marks
            FROM exams
            ORDER BY exam_date DESC
        """).fetchall()

        return [dict(row) for row in rows]

def save_exam_result(exam_id, student_id, subject, marks):

    if subject not in EXAM_SUBJECTS:
        raise ValueError(f"Invalid subject: {subject}")

    with get_connection() as conn:
        exam = conn.execute("""
            SELECT max_marks
            FROM exams
            WHERE exam_id = ?
        """, (exam_id,)).fetchone()

        if not exam:
            raise ValueError("Examination not found.")

        if marks is None:
            # A blank mark means no result has been entered.
            conn.execute("""
                DELETE FROM exam_results
                WHERE exam_id = ?
                  AND student_id = ?
                  AND subject = ?
            """, (exam_id, str(student_id), subject))
            return True

        marks = float(marks)
        maximum = float(exam["max_marks"])

        if not 0 <= marks <= maximum:
            raise ValueError(
                f"Marks for {subject} must be between 0 and {maximum}."
            )

        conn.execute("""
            INSERT INTO exam_results (
                exam_id,
                student_id,
                subject,
                marks
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(exam_id, student_id, subject)
            DO UPDATE SET
                marks = excluded.marks
        """, (
            exam_id,
            str(student_id),
            subject,
            marks
        ))

    return True


def save_exam_results_bulk(exam_id, results):
    """
    Save multiple students and subjects in one database transaction.

    results format:
    [
        {
            "student_id": "STUD0001",
            "marks": {
                "math_marks": 80,
                "science_marks": None
            }
        }
    ]

    None means the subject result is missing and should not be stored.
    """

    with get_connection() as conn:
        exam = conn.execute("""
            SELECT max_marks
            FROM exams
            WHERE exam_id = ?
        """, (exam_id,)).fetchone()

        if not exam:
            raise ValueError("Examination not found.")

        maximum = float(exam["max_marks"])

        for student_result in results:
            student_id = str(student_result["student_id"])

            student = conn.execute("""
                SELECT student_id
                FROM students
                WHERE student_id = ?
            """, (student_id,)).fetchone()

            if not student:
                raise ValueError(
                    f"Student {student_id} was not found."
                )

            for subject, marks in student_result["marks"].items():
                if subject not in EXAM_SUBJECTS:
                    raise ValueError(f"Invalid subject: {subject}")
                if marks is None:
                    conn.execute("""
                        DELETE FROM exam_results
                        WHERE exam_id = ?
                          AND student_id = ?
                          AND subject = ?
                    """, (exam_id, student_id, subject))
                    continue

                marks = float(marks)

                if not 0 <= marks <= maximum:
                    raise ValueError(
                        f"{student_id}: {subject} must be between "
                        f"0 and {maximum}."
                    )

                conn.execute("""
                    INSERT INTO exam_results (
                        exam_id,
                        student_id,
                        subject,
                        marks
                    )
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(exam_id, student_id, subject)
                    DO UPDATE SET
                        marks = excluded.marks
                """, (
                    exam_id,
                    student_id,
                    subject,
                    marks
                ))

    return True


def get_exam_results(exam_id, class_name=None):
    with get_connection() as conn:
        query = """
            SELECT
                exam_results.exam_id,
                exam_results.student_id,
                students.name,
                students.class_name,
                exam_results.subject,
                exam_results.marks,
                exams.exam_name,
                exams.exam_date,
                exams.max_marks
            FROM exam_results
            JOIN students
                ON students.student_id = exam_results.student_id
            JOIN exams
                ON exams.exam_id = exam_results.exam_id
            WHERE exam_results.exam_id = ?
        """

        parameters = [exam_id]

        if class_name is not None:
            query += " AND students.class_name = ?"
            parameters.append(class_name)

        query += """
            ORDER BY students.name, exam_results.subject
        """

        rows = conn.execute(query, parameters).fetchall()

        return [dict(row) for row in rows]


def get_exam_history(student_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                exams.exam_id,
                exams.exam_name,
                exams.exam_date,
                exams.max_marks,
                exam_results.subject,
                exam_results.marks,
                ROUND(
                    exam_results.marks * 100.0 / exams.max_marks,
                    2
                ) AS percentage
            FROM exam_results
            JOIN exams
                ON exams.exam_id = exam_results.exam_id
            WHERE exam_results.student_id = ?
            ORDER BY exams.exam_date ASC, exams.exam_id ASC
        """, (str(student_id),)).fetchall()

        return [dict(row) for row in rows]


# ====================================================
# DATABASE SETUP
# =====================================================

def setup_database():

    initialize_database()

    migration_result = migrate_students_from_csv()

    return migration_result


if __name__ == "__main__":

    result = setup_database()

    print("EduAnalytics database setup completed.")
    print(result)

    print(
        "Total students:",
        len(get_all_students())
    )

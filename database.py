
import sqlite3
import csv
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import re


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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exam_name, exam_date)
            )
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

        conn.execute("DROP TABLE IF EXISTS activity_logs")


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

def add_exam(exam_name, exam_date):

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO exams (exam_name, exam_date)
            VALUES (?, ?)
            ON CONFLICT(exam_name, exam_date) DO NOTHING
        """, (exam_name, exam_date))

        row = conn.execute("""
            SELECT exam_id
            FROM exams
            WHERE exam_name = ? AND exam_date = ?
        """, (exam_name, exam_date)).fetchone()

        return row["exam_id"]


def get_all_exams():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM exams
            ORDER BY exam_date DESC
        """).fetchall()

        return [dict(row) for row in rows]


def save_exam_result(exam_id, student_id, subject, marks):

    marks = float(marks)

    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100.")

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO exam_results (
                exam_id,
                student_id,
                subject,
                marks
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(exam_id, student_id, subject)
            DO UPDATE SET marks = excluded.marks
        """, (
            exam_id,
            str(student_id),
            subject,
            marks
        ))

    return True


def get_exam_history(student_id):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                exams.exam_id,
                exams.exam_name,
                exams.exam_date,
                exam_results.subject,
                exam_results.marks

            FROM exam_results

            JOIN exams
                ON exams.exam_id = exam_results.exam_id

            WHERE exam_results.student_id = ?

            ORDER BY exams.exam_date ASC
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

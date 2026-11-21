import streamlit as st
import auth

from database import get_connection

require_auth = auth.require_auth
hash_password = auth.hash_password
valid_email = auth.valid_email
valid_password = auth.valid_password

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Teacher Accounts | EduAnalytics",
    page_icon="E",
    layout="wide",
)


# ============================================================
# ADMIN ACCESS
# ============================================================

require_auth()

current_user = st.session_state.get("auth_user")

if current_user.get("role") != "admin":
    st.error("Access denied. Only Admin can manage teacher accounts.")
    st.stop()


# ============================================================
# PAGE
# ============================================================

st.title("Teacher Accounts")
st.caption("Create and manage teacher login accounts.")

tab_create, tab_manage = st.tabs(
    ["Create Teacher Account", "Manage Accounts"]
)


# ============================================================
# CREATE TEACHER
# ============================================================

with tab_create:

    st.subheader("Create New Teacher")

    with st.form("create_teacher_form"):

        full_name = st.text_input("Teacher Name")

        email = st.text_input(
            "Teacher Email"
        )

        temporary_password = st.text_input(
            "Temporary Password",
            type="password",
        )

        confirm_password = st.text_input(
            "Confirm Temporary Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Create Teacher Account",
            use_container_width=True,
        )

    if submitted:

        full_name = full_name.strip()
        email = email.strip().lower()

        if not full_name:
            st.error("Enter the teacher's name.")

        elif not valid_email(email):
            st.error("Enter a valid email address.")

        elif not valid_password(temporary_password):
            st.error(
                "Temporary password must contain at least 8 characters."
            )

        elif temporary_password != confirm_password:
            st.error("Passwords do not match.")

        else:

            with get_connection() as conn:

                existing = conn.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE username = ?
                    """,
                    (email,),
                ).fetchone()

                if existing:
                    st.error("An account with this email already exists.")

                else:

                    conn.execute(
                        """
                        INSERT INTO users (
                            username,
                            password_hash,
                            role,
                            full_name,
                            is_active,
                            must_change_password
                        )
                        VALUES (?, ?, 'teacher', ?, 1, 1)
                        """,
                        (
                            email,
                            hash_password(temporary_password),
                            full_name,
                        ),
                    )

                    st.success(
                        f"Teacher account created for {full_name}."
                    )

                    st.info(
                        "Share the email and temporary password with the teacher. "
                        "They will be required to create a new password at first login."
                    )


# ============================================================
# MANAGE TEACHERS
# ============================================================

with tab_manage:

    st.subheader("Existing Accounts")

    with get_connection() as conn:

        teachers = conn.execute(
            """
            SELECT
                user_id,
                full_name,
                username,
                is_active,
                must_change_password
            FROM users
            WHERE role = 'teacher'
            ORDER BY full_name
            """
        ).fetchall()

    if not teachers:

        st.info("No teacher accounts have been created yet.")

    else:

        for teacher in teachers:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 1, 2]
                )

                with col1:

                    st.markdown(
                        f"**{teacher['full_name']}**"
                    )

                    st.caption(teacher["username"])

                with col2:

                    if teacher["is_active"]:
                        st.success("Active")
                    else:
                        st.error("Disabled")

                with col3:

                    button_label = (
                        "Disable Account"
                        if teacher["is_active"]
                        else "Enable Account"
                    )

                    if st.button(
                        button_label,
                        key=f"toggle_{teacher['user_id']}",
                        use_container_width=True,
                    ):

                        new_status = (
                            0 if teacher["is_active"] else 1
                        )

                        with get_connection() as conn:

                            conn.execute(
                                """
                                UPDATE users
                                SET is_active = ?
                                WHERE user_id = ?
                                AND role = 'teacher'
                                """,
                                (
                                    new_status,
                                    teacher["user_id"],
                                ),
                            )

                        st.rerun()

                with st.expander("Reset Teacher Password"):

                    with st.form(
                        f"reset_form_{teacher['user_id']}"
                    ):

                        new_temp_password = st.text_input(
                            "New Temporary Password",
                            type="password",
                            key=f"new_password_{teacher['user_id']}",
                        )

                        confirm_temp_password = st.text_input(
                            "Confirm Temporary Password",
                            type="password",
                            key=f"confirm_password_{teacher['user_id']}",
                        )

                        reset_submitted = st.form_submit_button(
                            "Reset Password"
                        )

                    if reset_submitted:

                        if not valid_password(new_temp_password):
                            st.error(
                                "Password must contain at least 8 characters."
                            )

                        elif new_temp_password != confirm_temp_password:
                            st.error("Passwords do not match.")

                        else:

                            with get_connection() as conn:

                                conn.execute(
                                    """
                                    UPDATE users
                                    SET password_hash = ?,
                                        must_change_password = 1
                                    WHERE user_id = ?
                                    AND role = 'teacher'
                                    """,
                                    (
                                        hash_password(new_temp_password),
                                        teacher["user_id"],
                                    ),
                                )

                            st.success(
                                "Temporary password reset. "
                                "The teacher must change it at next login."
                            )
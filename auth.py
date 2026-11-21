import streamlit as st
import hashlib
import hmac
import secrets
import re

from database import get_connection, initialize_database


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600000,
    ).hex()

    return f"pbkdf2_sha256${salt}${password_hash}"


def verify_password(password, stored_hash):

    try:
        algorithm, salt, original_hash = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600000,
        ).hex()

        return hmac.compare_digest(new_hash, original_hash)

    except (ValueError, AttributeError):
        return False


# ============================================================
# VALIDATION
# ============================================================

def valid_email(email):

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.match(pattern, email))


def valid_password(password):

    return len(password) >= 8


# ============================================================
# DATABASE / AUTH INITIALIZATION
# ============================================================

def initialize_auth():

    initialize_database()

    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None


def admin_exists():

    with get_connection() as conn:

        result = conn.execute(
            "SELECT user_id FROM users WHERE role = 'admin' LIMIT 1"
        ).fetchone()

    return result is not None


# ============================================================
# CREATE ADMIN ACCOUNT
# ============================================================

def create_admin(full_name, email, password):

    email = email.strip().lower()

    if not full_name.strip():
        return False, "Enter the Admin name."

    if not valid_email(email):
        return False, "Enter a valid email address."

    if not valid_password(password):
        return False, "Password must contain at least 8 characters."

    with get_connection() as conn:

        existing = conn.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (email,),
        ).fetchone()

        if existing:
            return False, "This email is already registered."

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
            VALUES (?, ?, 'admin', ?, 1, 0)
            """,
            (
                email,
                hash_password(password),
                full_name.strip(),
            ),
        )

    return True, "Admin account created successfully."


# ============================================================
# LOGIN
# ============================================================

def authenticate_user(email, password):

    email = email.strip().lower()

    with get_connection() as conn:

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (email,),
        ).fetchone()

    if not user:
        return False, "Invalid email or password."

    if not user["is_active"]:
        return False, "Your account has been disabled. Contact Admin."

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid email or password."

    must_change = user["must_change_password"] if "must_change_password" in user.keys() else 0

    st.session_state.auth_user = {
        "user_id": user["user_id"],
        "email": user["username"],
        "full_name": user["full_name"] or user["username"],
        "role": user["role"],
        "must_change_password": must_change,
    }

    return True, "Login successful."

# ============================================================
# CHANGE PASSWORD
# ============================================================

def update_password(user_id, new_password):

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?,
                must_change_password = 0
            WHERE user_id = ?
            """,
            (
                hash_password(new_password),
                user_id,
            ),
        )

    st.session_state.auth_user["must_change_password"] = 0


def render_password_change():

    st.title("Create Your New Password")

    st.info(
        "Your Admin provided a temporary password. "
        "You must create a new password before accessing EduAnalytics."
    )

    with st.form("first_login_password_form"):

        new_password = st.text_input(
            "New Password",
            type="password",
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Update Password",
            use_container_width=True,
        )

    if submitted:

        if not valid_password(new_password):
            st.error("Password must contain at least 8 characters.")

        elif new_password != confirm_password:
            st.error("Passwords do not match.")

        else:

            update_password(
                st.session_state.auth_user["user_id"],
                new_password,
            )

            st.success("Password updated successfully.")

            st.rerun()


# ============================================================
# LOGIN SCREEN / FIRST ADMIN SETUP
# ============================================================


def render_login_screen():

    st.markdown(
        """
        <style>
        /* Main page layout */
        .block-container {
            max-width: 1100px !important;
            padding: 1rem 2rem !important;
        }

        /* Space below EduAnalytics subtitle */
        [data-testid="stCaptionContainer"] {
            margin-bottom: -0.5rem !important;
        }

        /* Create Admin heading */
        h3 {
            margin-top: 0 !important;
            margin-bottom: 0.4rem !important;
        }

        /* Admin information message */
        [data-testid="stAlert"] {
            display: flex !important;
            align-items: center !important;
            width: fit-content !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            padding: 8px 14px !important;
            margin: 0 !important;
            min-height: unset !important;
        }

        /* Remove extra icon space */
        [data-testid="stAlert"] svg {
            display: none !important;
        }

        /* Align message content */
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
            padding: 0 !important;
            margin: 0 !important;
        }

        [data-testid="stAlert"] p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 20px !important;
            white-space: normal !important;
        }

        /* Form spacing */
        div[data-testid="stForm"] {
            padding-top: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("EduAnalytics")
    st.caption("Student Performance Intelligence")

    # FIRST ADMIN SETUP

    if not admin_exists():

        st.subheader("Create Admin Account")

        st.info(
            "No Admin account exists yet. Create the first Admin account to get started."
        )

        with st.form("first_admin_form"):

            full_name = st.text_input("Admin Name")
            email = st.text_input("Admin Email")
            password = st.text_input(
                "Password",
                type="password",
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Create Admin Account",
                use_container_width=True,
            )

        if submitted:

            if password != confirm_password:
                st.error("Passwords do not match.")

            else:

                success, message = create_admin(
                    full_name,
                    email,
                    password,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        return

    # NORMAL LOGIN

    st.subheader("Login")

    with st.form("login_form"):

        email = st.text_input("Email Address")

        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:

        success, message = authenticate_user(
            email,
            password,
        )

        if success:
            st.rerun()
        else:
            st.error(message)

# ============================================================
# AUTHENTICATION PROTECTION
# ============================================================
def require_auth():

    user = st.session_state.get("auth_user")

    if not user:

        st.markdown(
            """
            <style>
            .login-notice {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                box-sizing: border-box;
                background: #fffae5;
                border: 1px solid #eadcae;
                border-radius: 8px;
                padding: 10px 14px;
                gap: 12px;
            }

            .login-notice-text {
                color: #956b0f;
                font-size: 15px;
                font-weight: 500;
            }

            .login-notice-button {
                display: inline-block;
                background: #956b0f;
                color: #ffffff !important;
                text-decoration: none !important;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                white-space: nowrap;
            }

            .login-notice-button:hover {
                background: #79570b;
            }
            </style>

            <div class="login-notice">
                <span class="login-notice-text">
                    Please log in to continue.
                </span>
                <a class="login-notice-button" href="/" target="_self">
                    Go to Login
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.stop()

    if user.get("must_change_password", 0) == 1:
        render_password_change()
        st.stop()

# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state.auth_user = None

    st.rerun()
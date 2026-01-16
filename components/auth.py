"""Authentication component for Streamlit app."""

import hashlib
import os

import streamlit as st


def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password() -> bool:
    """Check if user is authenticated.

    Returns True if user is authenticated, shows login form otherwise.
    Password is read from APP_PASSWORD environment variable.
    Default password for development: "enrichment2024"
    """
    # Get expected password hash from environment
    expected_password = os.environ.get("APP_PASSWORD", "leadGenBME")
    expected_hash = _hash_password(expected_password)

    # Check if already authenticated
    if st.session_state.get("authenticated", False):
        return True

    # Show login form
    st.title("Login Required")

    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if _hash_password(password) == expected_hash:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password")

    return False


def logout_button() -> None:
    """Display logout button in main content area."""
    if st.session_state.get("authenticated", False):
        if st.button("Logout", type="secondary"):
            st.session_state["authenticated"] = False
            st.rerun()
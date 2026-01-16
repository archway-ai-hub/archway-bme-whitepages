"""CSV upload and validation component for Streamlit app."""

from typing import Optional

import pandas as pd
import streamlit as st


# Expected columns from input CSV based on CLAUDE.md
REQUIRED_COLUMNS = ["name"]
RECOMMENDED_COLUMNS = ["address", "city", "state", "zip"]
ALL_EXPECTED_COLUMNS = [
    "fein", "name", "lat", "long", "address", "city", "state", "zip",
    "phone", "county", "expdate", "website", "email1",
    "name1", "name2", "name3", "name4", "name5", "name6", "name7", "name8", "name9", "name10",
    "phone1", "phone2", "phone3", "phone4", "phone5", "phone6", "phone7", "phone8", "phone9", "phone10",
]


def render_upload_section() -> Optional[pd.DataFrame]:
    """Render file upload section and return uploaded DataFrame.

    Uses st.file_uploader with CSV and Excel support (.csv, .xlsx, .xls).
    Reads uploaded file into pandas DataFrame and stores in session state.

    Returns:
        DataFrame if file uploaded successfully, None otherwise.
    """
    st.subheader("Let's start with your data")

    uploaded_file = st.file_uploader(
        "Drop your file here or click to browse",
        type=["csv", "xlsx", "xls"],
        help="We accept CSV or Excel files. Your file should include restaurant name, address, and any existing contact info you have.",
        key="csv_uploader",
    )

    if uploaded_file is None:
        return None

    try:
        # Read file based on extension
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Hmm, we don't recognize this file type: {uploaded_file.name}")
            return None

        # Store in session state for access by other components
        st.session_state.uploaded_df = df
        return df

    except pd.errors.EmptyDataError:
        st.error("This file appears to be empty. Please try another one.")
        return None
    except pd.errors.ParserError as e:
        st.error(f"We had trouble reading this file: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Something went wrong reading your file: {str(e)}")
        return None


def validate_csv(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate that the uploaded DataFrame has required columns.

    Checks for required column ("name") and recommends additional columns
    for better enrichment results.

    Args:
        df: The pandas DataFrame to validate.

    Returns:
        Tuple of (is_valid, message) where:
        - is_valid: True if all required columns present
        - message: Validation result or warning message
    """
    if df is None or df.empty:
        return False, "The file appears to be empty. Please check and try again."

    # Normalize column names for case-insensitive comparison
    df_columns_lower = [col.lower().strip() for col in df.columns]

    # Check required columns
    missing_required = []
    for col in REQUIRED_COLUMNS:
        if col.lower() not in df_columns_lower:
            missing_required.append(col)

    if missing_required:
        return False, f"We need a '{', '.join(missing_required)}' column to proceed. Please add it and try again."

    # Check recommended columns
    missing_recommended = []
    for col in RECOMMENDED_COLUMNS:
        if col.lower() not in df_columns_lower:
            missing_recommended.append(col)

    if missing_recommended:
        return True, f"Warning: Your file is missing {', '.join(missing_recommended)} columns. We can still work with it, but results may be more limited."

    return True, "Looking good! Your file has all the columns we need."


def render_preview(df: pd.DataFrame) -> None:
    """Render a preview of the uploaded DataFrame with metrics.

    Shows first 10 rows and displays key metrics like total records,
    column count, and data quality indicators.

    Args:
        df: The pandas DataFrame to preview.
    """
    if df is None or df.empty:
        st.warning("No data to preview yet.")
        return

    st.subheader("Here's what you uploaded")

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Records to Process", f"{len(df):,}")

    with col2:
        st.metric("Data Columns", len(df.columns))

    with col3:
        # Count records with coordinates (useful for Google Places lookup)
        if "lat" in df.columns and "long" in df.columns:
            coords_count = df[["lat", "long"]].dropna().shape[0]
        else:
            coords_count = 0
        st.metric("Have Coordinates", f"{coords_count:,}")

    with col4:
        # Count non-empty name values
        if "name" in df.columns:
            name_count = df["name"].notna().sum()
        else:
            name_count = 0
        st.metric("Have Names", f"{name_count:,}")

    # Show column list
    with st.expander("See all columns in your file"):
        st.write(", ".join(df.columns.tolist()))

    # Show first 10 rows
    st.dataframe(df.head(10))

    # Data quality summary
    st.markdown("**A quick look at your data quality:**")
    quality_col1, quality_col2 = st.columns(2)

    with quality_col1:
        # Check for contact columns
        contact_cols = [c for c in df.columns if c.lower().startswith(("name", "phone", "email"))]
        st.write(f"- Contact columns found: {len(contact_cols)}")

        # Count records with any phone
        phone_cols = [c for c in df.columns if "phone" in c.lower()]
        if phone_cols:
            has_phone = df[phone_cols].notna().any(axis=1).sum()
            st.write(f"- Records with phone numbers: {has_phone:,}")

    with quality_col2:
        # Count records with address info
        address_cols = ["address", "city", "state", "zip"]
        present_addr_cols = [c for c in address_cols if c in df.columns]
        if present_addr_cols:
            has_address = df[present_addr_cols].notna().all(axis=1).sum()
            st.write(f"- Records with full address: {has_address:,}")

        # Count records with website
        if "website" in df.columns:
            has_website = df["website"].notna().sum()
            st.write(f"- Records with website: {has_website:,}")

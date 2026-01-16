"""
Restaurant Lead Enrichment - Streamlit Web Application

Provides a web interface for the restaurant lead enrichment CLI tool.
Features: Password authentication, CSV upload, progress tracking, results download.
"""

import streamlit as st

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from components
from components.auth import check_password, logout_button
from components.upload import render_upload_section, validate_csv, render_preview
from components.progress import run_processing
from components.results import render_results, render_download_button

# Import from main.py
from main import Config, parse_csv_row

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Restaurant Lead Enrichment",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for warmer, friendlier styling
st.markdown('''
<style>
    /* Softer buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    /* Friendly metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    /* Warmer container feel */
    .main .block-container {
        padding-top: 2rem;
    }
    /* Softer dividers */
    hr {
        border-color: #E4E7EB;
        margin: 1.5rem 0;
    }
    /* Friendlier info boxes */
    .stAlert {
        border-radius: 8px;
    }
</style>
''', unsafe_allow_html=True)


def main_app() -> None:
    """Main application logic after authentication."""
    # Set default processing settings (sidebar removed)
    batch_size = 10  # Optimal for parallel API calls
    limit = 0  # Process all records
    
    # Header with logout button in top right
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Restaurant Lead Enrichment")
        st.markdown(
            "Let's find the owners behind your restaurant leads. "
            "Just upload your file and we'll handle the rest."
        )
    with col2:
        logout_button()
    
    st.markdown("---")
    
    # Step 1: Upload CSV
    df = render_upload_section()
    
    if df is None:
        st.info("Upload a CSV or Excel file above to get started. We'll take it from there!")
        return
    
    # Step 2: Validate CSV
    is_valid, validation_message = validate_csv(df)
    
    if not is_valid:
        st.error(validation_message)
        return
    
    if "Warning" in validation_message:
        st.warning(validation_message)
    else:
        st.success(validation_message)
    
    st.markdown("---")
    
    # Step 3: Preview data
    render_preview(df)
    
    st.markdown("---")
    
    # Step 4: Processing
    st.subheader("Ready to enrich your leads")
    
    # Calculate records to process based on limit
    records_to_process = min(limit, len(df)) if limit > 0 else len(df)
    st.write(f"We're ready to process **{records_to_process}** records and find the people behind each restaurant.")
    
    # Validate required API keys before allowing processing
    config = Config()
    if not config.google_places_api_key or not config.openrouter_api_key:
        st.error(
            "Looks like we're missing some API keys. Please configure GOOGLE_PLACES_API_KEY "
            "and OPENROUTER_API_KEY in your environment or .env file to continue."
        )
        return
    
    # Start Processing button
    if st.button("Start Enrichment", type="primary"):
        # Apply limit to dataframe
        df_to_process = df.head(limit) if limit > 0 else df
        
        # Parse CSV rows to RestaurantRecord objects
        records = []
        parse_errors = 0
        
        for _, row in df_to_process.iterrows():
            try:
                record = parse_csv_row(row)
                records.append(record)
            except Exception as e:
                parse_errors += 1
                if parse_errors <= 3:  # Only show first 3 errors
                    st.warning(f"Heads up - had trouble parsing a row: {str(e)[:100]}")
        
        if parse_errors > 3:
            st.warning(f"... and {parse_errors - 3} more rows had parsing issues")
        
        if not records:
            st.error("We couldn't find any valid records to process. Please check your file format.")
            return
        
        st.info(f"Great! We've got {len(records)} records ready to go. Starting enrichment now...")
        
        # Run processing with progress tracking
        try:
            results = run_processing(
                records=records,
                config=config,
                batch_size=batch_size
            )
            
            # Store results in session state
            st.session_state.processing_results = results
            st.success(f"All done! We've processed {len(results)} records for you.")
            
        except Exception as e:
            st.error(f"Something went wrong during processing: {str(e)}")
            return
    
    # Step 5: Display results if available
    if "processing_results" in st.session_state and st.session_state.processing_results:
        results = st.session_state.processing_results
        
        st.markdown("---")
        
        # Render results with statistics
        render_results(results)
        
        st.markdown("---")
        
        # Download button
        st.subheader("Get Your Results")
        render_download_button(results)


def main() -> None:
    """Application entry point with authentication check."""
    # Initialize session state for authentication if not present
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication - stops here if not authenticated
    if not check_password():
        return
    
    # User is authenticated, show main app
    main_app()


if __name__ == "__main__":
    main()

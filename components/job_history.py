"""Job history component for Streamlit app."""

import io
import time
from datetime import datetime

import pandas as pd
import streamlit as st

from components.job_manager import Job, JobManager


def render_job_history(job_manager: JobManager, session_id: str) -> None:
    """Render job history section.

    Args:
        job_manager: JobManager instance for Redis operations
        session_id: Current user's session ID
    """
    if not job_manager or not job_manager.is_available():
        return  # Silently skip if Redis unavailable

    jobs = job_manager.get_user_jobs(session_id)

    if not jobs:
        return  # No history to show

    # Check if any jobs are still processing
    has_processing = any(job.status == "processing" for job in jobs)

    with st.expander("📋 Previous Enrichment Runs", expanded=has_processing):
        # Header with refresh button
        col1, col2 = st.columns([4, 1])
        with col1:
            if has_processing:
                st.caption("🔄 Auto-refreshing every 5 seconds...")
        with col2:
            if st.button("🔄", key="refresh_jobs", help="Refresh job status"):
                st.rerun()

        st.divider()

        for job in jobs:
            _render_job_card(job, job_manager)

    # Auto-refresh if jobs are processing and user isn't actively processing now
    # (check if we're NOT in the middle of showing progress)
    if has_processing and "processing_results" not in st.session_state:
        time.sleep(5)
        st.rerun()


def _render_job_card(job: Job, job_manager: JobManager) -> None:
    """Render a single job card with status and actions."""
    # Status badge colors
    status_colors = {
        "processing": "🟡",
        "completed": "🟢", 
        "failed": "🔴",
        "pending": "⚪"
    }
    
    status_icon = status_colors.get(job.status, "⚪")
    
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        st.markdown(f"{status_icon} **{job.filename}**")
        st.caption(f"{job.processed_records}/{job.total_records} records")
    
    with col2:
        # Format timestamp
        time_str = job.created_at.strftime("%b %d, %I:%M %p")
        st.caption(time_str)
    
    with col3:
        if job.status == "completed":
            # View/Download buttons
            if st.button("View", key=f"view_{job.id}", type="secondary"):
                _show_job_results(job, job_manager)
        elif job.status == "failed":
            st.caption(f"Error: {job.error_message[:30]}..." if job.error_message else "Unknown error")
        elif job.status == "processing":
            # Show progress
            progress = job_manager.get_progress(job.id)
            if progress:
                pct = progress.get("current", 0) / max(progress.get("total", 1), 1)
                st.progress(pct)
    
    st.divider()


def _show_job_results(job: Job, job_manager: JobManager) -> None:
    """Display results for a completed job in a modal-like expander."""
    results = job_manager.get_job_results(job.id)
    
    if not results:
        st.warning("Results no longer available")
        return
    
    # Store in session state to display
    st.session_state.viewing_job_results = results
    st.session_state.viewing_job_filename = job.filename
    st.rerun()


def render_viewed_job_results() -> bool:
    """Render results if viewing a past job. Returns True if displaying past results."""
    if "viewing_job_results" not in st.session_state:
        return False
    
    results = st.session_state.viewing_job_results
    filename = st.session_state.get("viewing_job_filename", "past_job")
    
    st.subheader(f"Results from: {filename}")
    
    # Clear button
    if st.button("← Back to current session"):
        del st.session_state.viewing_job_results
        if "viewing_job_filename" in st.session_state:
            del st.session_state.viewing_job_filename
        st.rerun()
    
    # Display as dataframe
    df = pd.DataFrame(results)
    st.dataframe(df, hide_index=True)
    
    # Download button
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"enriched_{filename}",
        mime="text/csv"
    )
    
    return True

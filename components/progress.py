"""Progress tracking component for Streamlit app.

Provides async-to-sync bridging for the batch processing pipeline,
with real-time progress updates via Streamlit widgets.
"""

import asyncio
from typing import Optional

import streamlit as st

from main import process_batch, Config, RestaurantRecord


def run_processing(
    records: list[RestaurantRecord],
    config: Config,
    batch_size: int = 10
) -> list[RestaurantRecord]:
    """Run batch processing with Streamlit progress tracking.

    Bridges the async process_batch function to synchronous Streamlit context,
    providing real-time progress updates via st.progress() and st.empty().

    Args:
        records: List of restaurant records to process.
        config: Configuration object with API keys.
        batch_size: Number of concurrent operations (semaphore limit).

    Returns:
        List of enriched RestaurantRecord objects.

    Raises:
        Exception: Re-raises any exception from processing after displaying error.
    """
    if not records:
        st.warning("No records to process yet.")
        return []

    # Create Streamlit progress widgets
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(records)

    status_text.text(f"Getting started with {total} records...")

    def progress_callback(current: int, total: int, message: str) -> None:
        """Update Streamlit progress widgets.

        Args:
            current: Current record number (1-indexed).
            total: Total number of records.
            message: Status message to display.
        """
        # Update progress bar (value must be 0.0 to 1.0)
        progress_value = current / total if total > 0 else 0.0
        progress_bar.progress(progress_value)

        # Update status text with friendlier message
        status_text.text(f"Working on record {current} of {total}... {message}")

    try:
        # Run async process_batch using asyncio.run()
        # This creates a new event loop for the sync context
        results = asyncio.run(
            process_batch(
                records=records,
                config=config,
                batch_size=batch_size,
                progress_callback=progress_callback
            )
        )

        # Mark completion with friendly message
        progress_bar.progress(1.0)
        status_text.text(f"Done! We've enriched all {total} records.")

        return results

    except Exception as e:
        # Display error in Streamlit with friendlier messaging
        st.error(f"Oops, something went wrong: {str(e)}")

        # Log full traceback for debugging
        import traceback
        st.expander("Technical Details").code(traceback.format_exc())

        # Re-raise to allow caller to handle
        raise

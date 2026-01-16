"""
Results display and download component for the Streamlit app.

Provides functions to render enrichment results as an interactive dataframe
with summary statistics and CSV download functionality.
"""

import io
from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from main import RestaurantRecord

# Import from main module
from main import RestaurantRecord, format_output_row


def render_results(results: list[RestaurantRecord]) -> None:
    """Render enrichment results as an interactive dataframe with summary stats.
    
    Converts results to DataFrame using format_output_row and displays:
    - Interactive dataframe with st.dataframe()
    - Summary statistics in columns (Owners Found, Names Resolved, 
      Whitepages Enriched, CSV Matched)
    
    Args:
        results: List of processed RestaurantRecord objects from the enrichment pipeline
    """
    if not results:
        st.warning("No results to show yet. Run the enrichment first!")
        return
    
    # Convert results to DataFrame using existing format_output_row function
    output_rows = [format_output_row(record) for record in results]
    df = pd.DataFrame(output_rows)
    
    # Calculate summary statistics
    total = len(results)
    
    # Owners Found: count records with at least one owner
    owners_found = sum(1 for r in results if r.owners)
    
    # Names Resolved: count where restaurant_name differs from llc_name
    names_resolved = sum(
        1 for r in results 
        if r.restaurant_name and r.llc_name and r.restaurant_name != r.llc_name
    )
    
    # Whitepages Enriched: count records with personal_phone from Whitepages
    whitepages_enriched = sum(
        1 for r in results 
        if r.owners and any(o.personal_phone for o in r.owners)
    )
    
    # CSV Matched: count records where owner source contains "csv"
    csv_matched = sum(
        1 for r in results 
        if r.owners and any("csv" in o.source.lower() for o in r.owners)
    )
    
    # Display header with encouraging message
    st.subheader("Here's what we found!")
    
    # Add encouraging context based on results
    if owners_found > 0:
        success_rate = (owners_found / total * 100)
        if success_rate >= 70:
            st.success(f"Great news! We found owners for {success_rate:.0f}% of your records.")
        elif success_rate >= 40:
            st.info(f"We found owners for {success_rate:.0f}% of your records. Not bad!")
    
    # Display summary stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Owners Discovered",
            value=f"{owners_found} / {total}",
            delta=f"{(owners_found / total * 100):.1f}%" if total > 0 else "0%"
        )
    
    with col2:
        st.metric(
            label="Restaurant Names Resolved",
            value=f"{names_resolved} / {total}",
            delta=f"{(names_resolved / total * 100):.1f}%" if total > 0 else "0%"
        )
    
    with col3:
        st.metric(
            label="Whitepages Enriched",
            value=f"{whitepages_enriched} / {total}",
            delta=f"{(whitepages_enriched / total * 100):.1f}%" if total > 0 else "0%"
        )
    
    with col4:
        st.metric(
            label="Matched from Your CSV",
            value=f"{csv_matched} / {total}",
            delta=f"{(csv_matched / total * 100):.1f}%" if total > 0 else "0%"
        )
    
    # Display interactive dataframe
    st.subheader("Your Enriched Data")
    st.dataframe(
        df,
        hide_index=True
    )


def render_download_button(results: list[RestaurantRecord]) -> None:
    """Render a download button for exporting results as CSV.
    
    Creates CSV bytes from results using format_output_row and provides
    a download button for "enriched_leads.csv".
    
    Args:
        results: List of processed RestaurantRecord objects from the enrichment pipeline
    """
    if not results:
        st.warning("No results available for download yet.")
        return
    
    # Convert results to DataFrame
    output_rows = [format_output_row(record) for record in results]
    df = pd.DataFrame(output_rows)
    
    # Convert to CSV bytes
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    st.write("Your enriched leads are ready! Click below to download.")
    
    # Render download button
    st.download_button(
        label="Download Enriched Leads",
        data=csv_bytes,
        file_name="enriched_leads.csv",
        mime="text/csv"
    )

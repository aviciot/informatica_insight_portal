import streamlit as st
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import time

from config.config import Config
from st_aggrid import AgGrid, GridOptionsBuilder

from informatica_insight.dev_pages.configuration_p import display_data_viewer
from informatica_insight.dev_pages.data_configuration import display_data_configuration
from informatica_insight.dev_pages.app_configuration import display_app_configuration
from informatica_insight.dev_pages.insight import informatica_insight
from informatica_insight.db_utils.db_utils2 import (
    initialize_database,
    fetch_cached_tables2,
    recreate_selected_tables,
    transfer_data,
    recreate_selected_views
)

# Logging
logger = logging.getLogger(__name__)
logger.propagate = True


def initialize_state():
    """Initialize session state variables for cached tables, config, and mappings."""
    config_file = Path("informatica_insight/config", "config.yaml")
    config = Config(config_file)   
    # st.session_state["config"] = config
    if "config" not in st.session_state:
        st.session_state["config"] = config

    if "cached_tables" not in st.session_state:
        progress_bar = st.progress(0)
        status_container = st.empty()  # Placeholder for live updates
        table_statuses = []  # Store status messages for each table

        def update_progress(current, total, table_name, record_count):
            """Updates the progress bar and table status messages dynamically."""
            percent_complete = int((current / total) * 100)
            progress_bar.progress(percent_complete)

            # Update status dynamically
            table_statuses.append(f"✅ Loaded `{table_name}` ({record_count} records)")
            status_container.markdown("\n".join(table_statuses))

        with st.spinner("Fetching cached tables..."):
            st.session_state["cached_tables"] = fetch_cached_tables2(update_progress)

        progress_bar.empty()  # Remove progress bar after completion
        status_container.markdown("### ✅ Cached tables successfully initialized!")

        if not st.session_state["cached_tables"]:
            st.warning("⚠️ No tables found to cache.")
            st.info("Manage Insight DB (Data Configuration")


def display_informatica_insight_page():
    """Main Development Page for Database Interaction."""
    st.title("🔧 Informatica Insights Portal")
    st.markdown("---")

    initialize_state()
    tabs = st.tabs(["App Configuration", "⚙️ Data Configuration", "📊 informatica Insights", "Test"])

    with tabs[0]:
        if st.session_state.get("role") == "admin":
            st.subheader("App Configuration")
            st.markdown("Manage application settings and database cache.")
            display_app_configuration()
        else:
            st.markdown(
                """
                <div class="access-denied">
                    <div class="access-denied-icon">🚫</div>
                    <p>You do not have permission to access this section.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tabs[1]:
        if st.session_state.get("role") == "admin":
            st.subheader("Insight Data Management")
            st.markdown("Align Insight Data based Informatica and configurations files.")
            display_data_configuration()
        else:
            st.markdown(
                """
                <div class="access-denied">
                    <div class="access-denied-icon">🚫</div>
                    <p>You do not have permission to access this section.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tabs[2]:
        if st.session_state.get("role") == "admin":

            informatica_insight()
        #    st.markdown("Manage application settings and database cache.")
        else:
            st.markdown(
                """
                <div class="access-denied">
                    <div class="access-denied-icon">🚫</div>
                    <p>You do not have permission to access this section.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


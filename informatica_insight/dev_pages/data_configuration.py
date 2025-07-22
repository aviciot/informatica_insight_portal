import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime
from informatica_insight.db_utils.db_utils2 import (recreate_selected_tables,transfer_data,fetch_cached_tables2,
                                                    recreate_selected_views,update_informatica_connection_details)

from informatica_insight.db_utils.ScriptStoreManager import ScriptStoreManager



def display_data_configuration():
    """Displays the data configuration UI for managing tables, views, and data loading."""

    # Define database display names with icons
    db_colors = {
        "sqlite": "🔵 SQLite",
        "postgres": "🟢 PostgreSQL",
    }

    # Get database preference from session state
    db_preference = st.session_state["config"].get("insight_db.work_with", "Unknown")
    db_display_name = db_colors.get(db_preference, "⚠️ Unknown")

    # Display database preference
    st.markdown(f"**Insight DB: {db_display_name}**")

    # Define tabs for different functionalities
    tab1, tab2 = st.tabs(["Manage Configuration Tables & Views", "Data Viewer"])

    with tab1:
        st.subheader("⚙️ Manage Configuration Tables")
        tables_to_process = st.session_state["config"].get("insight_db.ddl", [])


        if not tables_to_process:
            st.info("No tables defined in the configuration.")
            st.stop()

        # Section: Recreate Tables
        with st.expander("🔄 Recreate Tables"):
            st.write("Select one or more tables to drop and recreate:")

            selected_tables_recreate = {
                table: st.checkbox(f"Recreate {table}", key=f"recreate_{table}")
                for table in tables_to_process
            }

            if any(selected_tables_recreate.values()):
                if st.button("Recreate Selected Tables"):
                    selected_tables = [
                        table for table, selected in selected_tables_recreate.items() if selected
                    ]
                    result = recreate_selected_tables(selected_tables)
                    st.write("### Recreate Status")
                    st.table(result)

        st.subheader("⚙️ Manage Script Store Table (FTS5)")
        with st.expander("📄 Manage Script Store Table (FTS5)"):
            st.info("This table stores scripts for full-text search using SQLite FTS5 or PostgreSQL FTS.")

            if st.button("Recreate Script Store Table"):
                try:
                    ScriptStoreManager().recreate_table()
                    ScriptStoreManager().dr
                    st.success("✅ `script_store` table was recreated successfully.")
                except Exception as e:
                    st.error(f"❌ Failed to recreate `script_store`: {e}")

        st.divider()
        #
        # Section: Recreate Views
        with st.expander("🔄 Recreate Views"):
            views_to_recreate = st.session_state["config"].get("insight_db.views", {})

            if not views_to_recreate:
                st.warning("⚠️ No views available for recreation.")
            else:
                st.write("Select one or more views to drop and recreate:")
                selected_views = [
                    view for view in views_to_recreate.keys()
                    if st.checkbox(f"Recreate {view}", key=f"recreate_{view}")
                ]

                if st.button("🚀 Recreate Selected Views"):
                    if not selected_views:
                        st.warning("⚠️ Please select at least one view.")
                    else:
                        with st.spinner("Recreating selected views... ⏳"):
                            result = recreate_selected_views(selected_views)
                            st.success(result)

        st.divider()

        # Load Informatica Data to Insights DB
        st.subheader("🛢️ Load Informatica Data to Insights DB")

        # Select database type
        db_type = st.radio("Select Informatica Source DB:", st.session_state["config"].get("informatica_db", []))
        st.info("Fetch Data from Informatica Repository")
        db_details = st.session_state["config"].get(f"informatica_db.{db_type}", {})
        #
        if db_details:
            st.markdown(f"#### 📌 {db_type.upper()} Database Details")
            st.write(f"**User:** {db_details.get('user', 'N/A')}")
            st.write(f"**Host:** {db_details.get('host', 'N/A')}")
            st.write(f"**Port:** {db_details.get('port', 'N/A')}")
            st.write(f"**Service Name:** {db_details.get('service_name', 'N/A')}")

        # Ensure tables exist before proceeding
        if not tables_to_process:
            st.info("No tables to process defined in the configuration.")
            st.stop()

        # Table selection for data transfer
        selected_tables = {}
        with st.expander("Select Tables to Transfer"):
            for table in tables_to_process:
                selected_tables[table] = st.checkbox(table, key=f"table_{table}")

            selected_tables = [table for table, selected in selected_tables.items() if selected]

            if st.button("Start Data Load"):
                if not selected_tables:
                    st.warning("⚠️ Please select at least one table to transfer.")
                else:
                    st.write("### Data Load Status")
                    status_data = []
                    progress_bar = st.progress(0)
                    total_tables = len(selected_tables)

                    for idx, table in enumerate(selected_tables):
                        progress_percentage = (idx + 1) / total_tables
                        progress_bar.progress(progress_percentage, text=f"Loading `{table}` ({idx + 1}/{total_tables})...")

                        # Transfer data and collect results
                        result = transfer_data(table, db_type)
                        status_data.append({"Table": table, "Status": result})

                    # Mark progress as complete
                    progress_bar.progress(1.0, text="✅ Data load complete.")
                st.table(status_data)

            st.divider()

        st.subheader("🛢️ Process odbc.ini and tnsnames.ora ")
        st.info("Align Infomatica connections with tnsnames.ora(Oracle) and odbc.ini (non-Oracle)\nTable:informatica_connections_details")
        st.write("Align Informatica connection details:")
        with st.expander("🔗 Align Connection Details by Scope"):

            # Fetch prod_env_scope from config
            prod_env_scope = st.session_state["config"].get("informatica_db", [])
            if not prod_env_scope:
                st.info("No scopes defined in `prod_env_scope`.")
            else:
                selected_scopes = {}
                for scope in prod_env_scope:
                    selected_scopes[scope] = st.checkbox(f"Align {scope}", key=f"align_{scope}")

                if any(selected_scopes.values()):
                    if st.button("Align Selected Scopes"):
                        status = []
                        for scope, selected in selected_scopes.items():
                            if selected:
                                try:
                                    user = prod_env_scope[scope].get("user")
                                    update_informatica_connection_details(scope, user)
                                    status.append((scope, "✅ Success"))
                                except Exception as e:
                                    status.append((scope, f"❌ Error: {e}"))
                        st.write("### Connection Alignment Status")
                        st.table(status)
        with tab2:
            st.subheader("📊 Data Viewer")

            last_refresh = st.session_state.get("last_refresh", "Never")
            st.markdown(f"**🕒 Last Refreshed:** {last_refresh}")

            if st.button("🔄 Refresh Cache"):
                with st.spinner("Refreshing cached data..."):
                    try:
                        st.session_state["cached_tables"] = fetch_cached_tables2()
                        st.session_state["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success("Cache refreshed successfully!")
                    except Exception as e:
                        st.error(f"Failed to refresh cache: {e}")

            # Check for cached tables in session state
            cached_tables = st.session_state.get("cached_tables", {})
        #
            if not cached_tables:
                st.warning("⚠️ No cached data available. Please refresh the cache.")
                # if st.button("🔄 Refresh Cache"):
                #     st.rerun()
                # return


            st.markdown("### 🗂️ Cached Tables Summary")

            table_data = [
                {"Table Name": table, "Row Count": f"{len(cached_tables[table]):,}"}
                for table in cached_tables
            ]
            summary_df = pd.DataFrame(table_data)

            st.dataframe(
                summary_df.style.set_properties(**{"text-align": "center"}),
                use_container_width=True,
            )

            st.markdown("### 🔍 Explore Table Data")
            table_names = list(cached_tables.keys())

            selected_table = st.selectbox("Select a table to explore:", table_names)

            if selected_table:
                # Load selected table data
                data = cached_tables[selected_table]
                df = pd.DataFrame(data)

                # Select column to filter
                filter_column = st.selectbox("Select a column to filter by:", df.columns)

                # Get unique values for selected column
                unique_values = df[filter_column].dropna().unique()
                selected_value = st.selectbox(f"Select a value from `{filter_column}`:", unique_values)

                # Filter Data
                filtered_df = df[df[filter_column] == selected_value]

                # Display filtered rows using AgGrid
                st.markdown(f"### 🔍 Rows with `{selected_value}` in `{filter_column}`")

                # Configure GridOptions
                gb = GridOptionsBuilder.from_dataframe(filtered_df)
                gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
                gb.configure_default_column(editable=False, filter=True, resizable=True,
                                            sortable=True)  # Allow filtering
                grid_options = gb.build()

                # Display AgGrid
                AgGrid(filtered_df, gridOptions=grid_options, theme="balham")

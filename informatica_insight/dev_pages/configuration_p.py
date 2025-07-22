import streamlit as st
from streamlit_ace import st_ace
from informatica_insight.db_utils.db_utils2 import test_db_connection,test_oracle_connection
import pandas as pd




def display_data_viewer():
    """Display cached tables for exploration using st_aggrid and manage configuration tables."""
    config = st.session_state["config"]
    st.title("📊 Config Data Viewer & Table Management")
    # Tabs for navigation
    tab1, tab2,tab3 = st.tabs(["Manage Tables And Views" ,"Data Viewer","Monitoring" ])

    with tab1:
        st.subheader("⚙️ Manage Configuration Tables")

        # Get list of tables to process
        tables_to_process = config.get("ddl.tables_to_process", [])
        if not tables_to_process:
            st.info("No tables to process defined in the configuration.")
            return

        # Section for Recreating Tables
        with st.expander("🔄 Recreate Tables"):
            st.write("Select one or more tables to drop and recreate:")
            selected_tables_recreate = {}
            for table in tables_to_process:
                selected_tables_recreate[table] = st.checkbox(f"Recreate {table}", key=f"recreate_{table}")

            if any(selected_tables_recreate.values()):
                if st.button("Recreate Selected Tables"):
                    status = []
                    for table, selected in selected_tables_recreate.items():
                        if selected:
                            try:
                                drop_and_create_table(config, table)
                                status.append((table, "✅ Success"))
                            except Exception as e:
                                status.append((table, f"❌ Error: {e}"))
                    st.write("### Recreate Status")
                    st.table(status)

        # Section for Loading Data
        with st.expander("📥 Load Data into Tables"):
            st.write("Select one or more tables to load data into:")
            selected_tables_load = {}
            for table in tables_to_process:
                selected_tables_load[table] = st.checkbox(f"Load Data into {table}", key=f"load_{table}")

            if any(selected_tables_load.values()):
                if st.button("Load Data into Selected Tables"):
                    status = []
                    for table, selected in selected_tables_load.items():
                        if selected:
                            try:
                                insert_data(config, table)
                                status.append((table, "✅ Success"))
                            except Exception as e:
                                status.append((table, f"❌ Error: {e}"))
                    st.write("### Load Data Status")
                    st.table(status)


        with st.expander("🔎 Create Views"):
            st.write("Select one or more views to create:")

            # Retrieve the views configuration
            views_config = config.get("views")
            if not views_config:
                st.error("No views defined in the configuration.")
            else:
                # Dictionary to store selected views for creation
                selected_views_to_create = {}

                # Display checkboxes for each view
                # for view_key in views_config.keys():
                #     if view_key != "all":  # Exclude the 'all' key
                #         selected_views_to_create[view_key] = st.checkbox(f"Create view: {view_key}",
                #                                                          key=f"create_{view_key}")
                #
                # # Button to trigger the creation process
                # if st.button("Create Selected Views"):
                #     status = []
                #     for view_key, selected in selected_views_to_create.items():
                #         if selected:
                #             try:
                #                 drop_create_view(config, view_key)
                #                 status.append((view_key, "✅ Success"))
                #             except Exception as e:
                #                 status.append((view_key, f"❌ Error: {e}"))
                #
                #     # Display the status
                #     st.write("### View Creation Status")
                #     st.table(status)

                # Option to create all views
                if st.button("Create All Views"):
                    try:
                        drop_create_views_path = config.get("views.all.drop_create")
                        if drop_create_views_path:
                            drop_create_view(config, "all")
                            st.success("All views created successfully.")
                        else:
                            st.error("The 'all' views script path is not defined in the configuration.")
                    except Exception as e:
                        st.error(f"Error creating all views: {e}")

        # Section for Aligning Connection Details by Scope
        with st.expander("🔗 Align Connection Details by Scope"):
            st.write("Align Informatica connection details for each scope in `prod_env_scope`:")

            # Fetch prod_env_scope from config
            prod_env_scope = config.get("prod_env_scope", [])
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
                                    update_informatica_connection_details(config, scope)
                                    status.append((scope, "✅ Success"))
                                except Exception as e:
                                    status.append((scope, f"❌ Error: {e}"))
                        st.write("### Connection Alignment Status")
                        st.table(status)
    with tab2:
        st.subheader("📊 Data Viewer")

        # Refresh Button with Timestamp
        last_refresh = st.session_state.get("last_refresh", "Never")
        st.markdown(f"**🕒 Last Refreshed:** {last_refresh}")

        if st.button("🔄 Refresh Cache"):
            with st.spinner("Refreshing cached data..."):
                try:
                    st.session_state["cached_tables"] = fetch_and_cache_tables(config)
                    st.session_state["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("Cache refreshed successfully!")
                except Exception as e:
                    st.error(f"Failed to refresh cache: {e}")

        # Check for cached tables
        cached_tables = st.session_state.get("cached_tables", {})
        if not cached_tables:
            st.info("No cached data available. Please refresh the cache.")
            return

        # Display Cached Tables Overview
        st.write("### Cached Tables Summary")
        table_data = [{"Table Name": table, "Row Count": len(cached_tables[table])} for table in cached_tables]
        summary_df = pd.DataFrame(table_data)
        st.table(summary_df)

        # Select Table to Explore
        st.write("### Explore Table Data")
        table_names = list(cached_tables.keys())
        selected_table = st.selectbox("Select a table to explore:", table_names)

        if selected_table:
            # Display Data
            st.write(f"### Table: `{selected_table}`")
            data = cached_tables[selected_table]

            # Configure and Display Grid
            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_default_column(editable=True, filter=True)
            grid_options = gb.build()
            AgGrid(
                data,
                gridOptions=grid_options,
                enable_enterprise_modules=False,
                theme="balham",
                update_mode="VALUE_CHANGED",
                fit_columns_on_grid_load=True,
            )

        #
    with tab3:
        st.header("Monitoring Dashboard")

        # Check if monitoring data exists
        if "monitoring_data" not in st.session_state:
            st.warning("Monitoring data is not initialized. Please restart the application.")
            return

        # Display monitoring status
        st.write(f"Status: **{st.session_state['monitoring_data']['status']}**")
       # display_monitoring_dashboard()
    # with tab4:
    #     st.header("Monitoring Dashboard")


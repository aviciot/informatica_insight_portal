
import logging
import streamlit as st
from collections import defaultdict
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.propagate = True

def merge_dicts(dict1, dict2):
    """
    Merges two dictionaries recursively, combining lists and nested dictionaries.
    """
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                merge_dicts(dict1[key], value)
            elif isinstance(value, list) and isinstance(dict1[key], list):
                dict1[key].extend(value)
            else:
                dict1[key] = value  # Overwrite if it's a scalar value
        else:
            dict1[key] = value
    return dict1

def group_and_clean_hierarchy(hierarchy):
    """
    Groups first-level children with the same name and cleans the hierarchy.
    """
    grouped_hierarchy = defaultdict(dict)

    for key, value in hierarchy.items():
        clean_key = key.strip() or "AllSessions"  # Handle empty keys
        if isinstance(value, dict):
            grouped_hierarchy[clean_key] = merge_dicts(grouped_hierarchy[clean_key], value)
        else:
            grouped_hierarchy[clean_key] = value  # Handle non-dict values if necessary

    return dict(grouped_hierarchy)

def display_workflow_hierarchy(workflow_details):
    """Display the workflow hierarchy as a tree structure."""
    st.markdown("### Workflow Hierarchy as JSON")

    # Build the nested JSON hierarchy from the DataFrame
    hierarchy = {}

    for _, row in workflow_details.iterrows():
        # Validate and process hierarchy_structure
        if not row['hierarchy_structure'] or row['hierarchy_structure'].strip('/') == "":
            st.warning(f"Skipping invalid hierarchy_structure: {row['hierarchy_structure']}")
            continue

        # Extract hierarchy path and split into parts
        path_parts = row['hierarchy_structure'].strip('/').split('/')
        current_level = hierarchy

        # Traverse or create levels for each part of the path
        for part in path_parts:
            current_level = current_level.setdefault(part, {})

        # Add session details if session_name is not null
        if pd.notnull(row['session_name']):
            if 'details' not in current_level:
                current_level['details'] = []

            # Add unique connectivity and operations details
            session_detail = {
                "connectivity": {
                    "connection_name": row.get('connection_name', "N/A"),
                    "connection_type": row.get('connection_type', "N/A"),
                    "host_name": row.get('host_name', "N/A"),
                    "database_name": row.get('database_name', "N/A"),
                    "port_number": row.get('port_number', "N/A")
                },
                "operations": {
                    "cmd_task_name": row.get('cmd_task_name', "N/A"),
                    "cmd_name": row.get('cmd_name', "N/A")
                }
            }
            if session_detail not in current_level['details']:
                current_level['details'].append(session_detail)

    # Group and clean the hierarchy to consolidate first-level children
    grouped_hierarchy = group_and_clean_hierarchy(hierarchy)

    # Display the grouped and cleaned JSON with a toggle for expansion
    st.markdown("### Grouped Workflow Hierarchy")
    with st.expander("View Grouped and Cleaned JSON", expanded=False):
        st.json(grouped_hierarchy, expanded=False)

def informatica_insight():
    """Enhanced implementation for exploring related processes."""
    config = st.session_state["config"]
    tabs = st.tabs(["Related Processes", "DB Related Processes"])

    with tabs[0]:
        st.markdown("### 🔍 Explore Related Processes")
        st.markdown("Easily navigate through Informatica Server, Repository, Folder, and Workflow details to explore related processes.")
        st.markdown("---")

        # Fetch workflow roots
        workflow_roots = st.session_state["cached_tables"].get("v_workflows_root")
        wf_hierarchy_explorer = st.session_state["cached_tables"].get("v_wf_hierarchy_explorer")

        if workflow_roots is None or workflow_roots.empty:
            st.error("No data available in `v_workflows_root`. Please check your database or cache.")
            return

        if wf_hierarchy_explorer is None or wf_hierarchy_explorer.empty:
            st.error("No data available in `wf_hierarchy_explorer`. Please check your database or cache.")
            return

        # Step 1: Create a layout with 3 columns for selections
        col1, col2, col3 = st.columns(3)

        # Step 2: Select Informatica Server
        with col1:
            servers = workflow_roots["informatica_server"].unique()
            selected_server = st.selectbox("Server", options=servers, key="server_selection")

        # Step 3: Select Repository (INFORMATICA_USER)
        with col2:
            repositories = workflow_roots[
                workflow_roots["informatica_server"] == selected_server
            ]["informatica_user"].unique()
            selected_repository = st.selectbox("Repository", options=repositories, key="repository_selection")

        # Step 4: Select Folder (FOLDER_NAME)
        with col3:
            folders = workflow_roots[
                (workflow_roots["informatica_server"] == selected_server)
                & (workflow_roots["informatica_user"] == selected_repository)
            ]["folder_name"].unique()
            selected_folder = st.selectbox("Folder", options=folders, key="folder_selection")

        # Step 5: List Workflows with Checkboxes
        workflows = workflow_roots[
            (workflow_roots["informatica_server"] == selected_server)
            & (workflow_roots["informatica_user"] == selected_repository)
            & (workflow_roots["folder_name"] == selected_folder)
        ][["session_wf_name", "workflow_id"]].drop_duplicates()

        if not workflows.empty:
            st.markdown("### Select Workflows")
            selected_workflow_names = st.multiselect(
                "Choose workflows to explore",
                options=workflows["session_wf_name"].tolist(),
                key="workflow_selection_list"
            )

            # Filter workflow IDs for the selected workflow names
            selected_workflow_ids = workflows[
                workflows["session_wf_name"].isin(selected_workflow_names)
            ]["workflow_id"].tolist()

            # Step 6: Add Explore Button
            if st.button("Explore", key="explore_button"):
                if not selected_workflow_ids:
                    st.warning("Please select at least one workflow to explore.")
                    return

                st.info(f"Fetching details for {len(selected_workflow_ids)} workflow(s)...")

                filtered_hierarchy = wf_hierarchy_explorer[
                    (wf_hierarchy_explorer["informatica_user"] == selected_repository)
                    & (wf_hierarchy_explorer["folder_name"] == selected_folder)
                ]

                for workflow_id in selected_workflow_ids:
                    workflow_details = filtered_hierarchy[filtered_hierarchy["workflow_id"] == workflow_id]

                    if not workflow_details.empty:
                        st.markdown(f"### Workflow: {workflow_id}")
                        st.write("Columns in workflow_details:", workflow_details.columns.tolist())
                        st.markdown(f"### Workflow: {workflow_id} - Data Table")
                        st.dataframe(workflow_details)
                        display_workflow_hierarchy(workflow_details)
                    else:
                        st.warning(f"No data found for Workflow ID: {workflow_id} in Folder: {selected_folder}.")
        else:
            st.warning("No workflows available for the selected criteria.")

            #DB Related Processes
    with tabs[1]:
        st.markdown("### 🗃️ DB Related Processes")
        st.markdown("View all related processes by either Host (DB Server/Endpoint) or Connection Name.")
        st.markdown("---")

        # Fetch connection details and workflow hierarchy
        all_connections = st.session_state["cached_tables"].get("informatica_connections_details")
 
        wf_hierarchy_explorer = (
            st.session_state["cached_tables"]
            .get("v_wf_hierarchy_explorer")
            .sort_values(by="path", ascending=True)
        )

        if all_connections is None or all_connections.empty:
            st.error("❌ No data available in `informatica_connections_details`. Please check your database or cache.")
            return

        if wf_hierarchy_explorer is None or wf_hierarchy_explorer.empty:
            st.error("❌ No data available in `v_wf_hierarchy_explorer`. Please check your database or cache.")
            return

        # Step 1: User selects a host (exclude null/empty HOST_NAME)
        valid_connections = all_connections.dropna(subset=["host_name"])
        host_names = valid_connections["host_name"].unique()
        selected_host = st.selectbox("🌐 Select Host", options=host_names, key="host_selection")
        selected_host_details = valid_connections[valid_connections["host_name"] == selected_host]
        if not selected_host_details.empty:
            # Extract the first row (assuming one host has one set of details)
            host_detail = selected_host_details.iloc[0]

            st.markdown(f"### 🖧 Host: **{selected_host}**")
            if not selected_host_details.empty:
                # Extract the first row (assuming one host has one set of details)
                host_detail = selected_host_details.iloc[0]

                # Convert the port number to an integer if it exists
                port_number = int(host_detail['port_number']) if not pd.isna(host_detail.get('port_number')) else 'N/A'


                st.markdown(
                    f"""
                        <div style="padding: 15px; border-radius: 10px; background-color: #f9f9f9; border: 1px solid #ddd;">               
                            <p><b>Scheme/DB Name:</b> {host_detail.get('database_name', 'N/A')}</p>
                                 <p><b>Service Name:</b> {host_detail.get('service_name', 'N/A')}</p>
                            <p><b>Port Number:</b> {port_number}</p>
                        </div>
                        """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning(f"No details found for host '{selected_host}'.")
        # Step 2: Filter connections for the selected host
        connection_names = valid_connections.loc[
            valid_connections["host_name"] == selected_host, "connection_name"
        ].unique()

        if len(connection_names) == 0:
            st.warning("⚠️ No connections found for the selected host.")
            return

        # Convert connection_names to lowercase for comparison
        connection_names = [name.lower() for name in connection_names]

        # Filter workflows by connections, ensuring case-insensitive comparison
        wf_hierarchy_explorer["_lower_connection_name"] = wf_hierarchy_explorer["connection_name"].str.lower()

        relevant_workflows = wf_hierarchy_explorer[
            wf_hierarchy_explorer["_lower_connection_name"].isin(connection_names)
        ]

        if relevant_workflows.empty:
            st.warning("⚠️ No workflows found for the selected host and connections.")
            return

        # Prepare data for display
        distinct_workflow_ids = relevant_workflows["workflow_id"].unique()
        distinct_workflow_id_path = [f"/{workflow_id}" for workflow_id in distinct_workflow_ids]

        workflow_data = wf_hierarchy_explorer[
            wf_hierarchy_explorer["path"].isin(distinct_workflow_id_path)
        ]
       # print("Workflow Data",workflow_data)

        from st_aggrid import AgGrid, GridOptionsBuilder

        # Display connections with expand box
        with st.expander("🔗 Related Connections (Click to Expand)", expanded=False):
            st.success(f"Found {len(connection_names)} connections for host '{selected_host}'.")
            connections_data = valid_connections[valid_connections["host_name"] == selected_host][
                ["connection_type", "connection_name"]
            ]
            # Configure AgGrid for connections
            gb_connections = GridOptionsBuilder.from_dataframe(connections_data)
            gb_connections.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
            # Set custom column styles
            gb_connections.configure_column("connection_name", cellStyle={"color": "blue", "font-weight": "bold"})
            grid_options_connections = gb_connections.build()
            AgGrid(connections_data, gridOptions=grid_options_connections, height=200)

        # Display workflows with expand box
        with st.expander("🛠️ Related Workflows (Click to Expand)", expanded=False):
            st.success(f"Found {len(distinct_workflow_ids)} workflows for host '{selected_host}'.")
            st.markdown("The following workflows are associated with the selected connections:")
            workflow_data = workflow_data.rename(columns={
                "id": "Id",
                "informatica_user": "Repository",
                "hierarchy_structure": "Workflow_name"
            })[["Repository", "folder_name", "Workflow_name"]]

            # Configure AgGrid for workflows
            gb_workflows = GridOptionsBuilder.from_dataframe(workflow_data)
            gb_workflows.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
            # Set custom column styles
            gb_workflows.configure_column("Id", cellStyle={"color": "green"})
            gb_workflows.configure_column("Repository", cellStyle={"color": "green"})
            gb_workflows.configure_column("Workflow_name", cellStyle={"color": "blue", "font-weight": "bold"})
            grid_options_workflows = gb_workflows.build()
            AgGrid(workflow_data, gridOptions=grid_options_workflows, height=300)
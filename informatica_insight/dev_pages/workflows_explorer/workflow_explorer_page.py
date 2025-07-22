import streamlit as st
import pandas as pd
from informatica_insight.dev_pages.workflows_explorer.utils import group_and_clean_hierarchy
import logging

logger = logging.getLogger(__name__)
logger.propagate = True


def display_workflow_hierarchy(workflow_details, wf_related_tables):
    """Display the workflow hierarchy as a tree structure."""
    st.markdown("### Workflow Hierarchy as JSON")
    hierarchy = {}

    for _, row in workflow_details.iterrows():
        if not row['hierarchy_structure'] or row['hierarchy_structure'].strip('/') == "":
            st.warning(f"Skipping invalid hierarchy_structure: {row['hierarchy_structure']}")
            continue

        path_parts = row['hierarchy_structure'].strip('/').split('/')
        current_level = hierarchy

        for part in path_parts:
            current_level = current_level.setdefault(part, {})

        if pd.notnull(row['session_name']):
            if 'details' not in current_level:
                current_level['details'] = []

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

            related_rows = wf_related_tables[
                wf_related_tables["session_name"] == row["session_name"]
            ]

            if not related_rows.empty:
                session_detail["related_tables"] = {
                    "source_name": related_rows["source_name"].dropna().unique().tolist(),
                    "target_name": related_rows["target_name"].dropna().unique().tolist(),
                    "other": related_rows["attr_value"].dropna().unique().tolist()
                }

            if session_detail not in current_level['details']:
                current_level['details'].append(session_detail)

    grouped_hierarchy = group_and_clean_hierarchy(hierarchy)

    st.markdown("### Grouped Workflow Hierarchy")
    with st.expander("View Grouped and Cleaned JSON", expanded=False):
        st.json(grouped_hierarchy, expanded=False)

def render_workflow_explorer_tab():
    """Renders the Workflow/Session Explorer tab content."""
    st.markdown("### 🔍 Explore Related Processes")
    st.markdown("Easily navigate through Informatica Server, Repository, Folder, and Workflow details to explore related processes.")
    st.markdown("---")

    workflow_roots = st.session_state["cached_tables"].get("v_workflows_root")
    wf_hierarchy_explorer = st.session_state["cached_tables"].get("v_wf_hierarchy_explorer")

    if workflow_roots is None or workflow_roots.empty:
        st.error("No data available in `v_workflows_root`. Please check your database or cache.")
        return

    if wf_hierarchy_explorer is None or wf_hierarchy_explorer.empty:
        st.error("No data available in `wf_hierarchy_explorer`. Please check your database or cache.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        servers = workflow_roots["informatica_server"].unique()
        selected_server = st.selectbox("Server", options=servers, key="server_selection")

    with col2:
        repositories = workflow_roots[
            workflow_roots["informatica_server"] == selected_server
        ]["informatica_user"].unique()
        selected_repository = st.selectbox("Repository", options=repositories, key="repository_selection")

    with col3:
        folders = workflow_roots[
            (workflow_roots["informatica_server"] == selected_server)
            & (workflow_roots["informatica_user"] == selected_repository)
        ]["folder_name"].unique()
        selected_folder = st.selectbox("Folder", options=folders, key="folder_selection")

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

        selected_workflow_ids = workflows[
            workflows["session_wf_name"].isin(selected_workflow_names)
        ]["workflow_id"].tolist()

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
                    informatica_related_tables = st.session_state["cached_tables"].get("informatica_related_tables")

                    wf_related_tables = informatica_related_tables[
                        (informatica_related_tables["workflow_id"] == workflow_id) &
                        (informatica_related_tables["folder_name"] == selected_folder) &
                        (informatica_related_tables["informatica_server"] == selected_server) &
                        (informatica_related_tables["informatica_user"] == selected_repository)
                    ][["workflow_id", "session_name", "mapping_name", "source_name", "target_name", "attr_value"]]

                    st.markdown(f"### Workflow: {workflow_id}")
                    st.markdown(f"### Workflow: {workflow_id} - Data Table")
                    st.dataframe(workflow_details)

                    display_workflow_hierarchy(workflow_details, wf_related_tables)
                else:
                    st.warning(f"No data found for Workflow ID: {workflow_id} in Folder: {selected_folder}.")
    else:
        st.warning("No workflows available for the selected criteria.")
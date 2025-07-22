
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

import logging
logger = logging.getLogger(__name__)
logger.propagate = True


def render_db_related_processes_tab():
    """Renders the DB Related Processes tab."""
    st.markdown("### 🗃️ DB Related Processes")
    st.markdown("View all related processes by either Host (DB Server/Endpoint) or Connection Name.")
    st.markdown("---")

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

    valid_connections = all_connections.dropna(subset=["host_name"])
    host_names = valid_connections["host_name"].unique()
    selected_host = st.selectbox("🌐 Select Host", options=host_names, key="host_selection")
    selected_host_details = valid_connections[valid_connections["host_name"] == selected_host]

    if not selected_host_details.empty:
        host_detail = selected_host_details.iloc[0]
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

    connection_names = valid_connections.loc[
        valid_connections["host_name"] == selected_host, "connection_name"
    ].unique()

    if len(connection_names) == 0:
        st.warning("⚠️ No connections found for the selected host.")
        return

    connection_names = [name.lower() for name in connection_names]
    wf_hierarchy_explorer["_lower_connection_name"] = wf_hierarchy_explorer["connection_name"].str.lower()

    relevant_workflows = wf_hierarchy_explorer[
        wf_hierarchy_explorer["_lower_connection_name"].isin(connection_names)
    ]

    if relevant_workflows.empty:
        st.warning("⚠️ No workflows found for the selected host and connections.")
        return

    distinct_workflow_ids = relevant_workflows["workflow_id"].unique()
    distinct_workflow_id_path = [f"/{workflow_id}" for workflow_id in distinct_workflow_ids]

    workflow_data = wf_hierarchy_explorer[
        wf_hierarchy_explorer["path"].isin(distinct_workflow_id_path)
    ]

    with st.expander("🔗 Related Connections (Click to Expand)", expanded=False):
        st.success(f"Found {len(connection_names)} connections for host '{selected_host}'.")
        connections_data = valid_connections[valid_connections["host_name"] == selected_host][
            ["connection_type", "connection_name"]
        ]
        gb_connections = GridOptionsBuilder.from_dataframe(connections_data)
        gb_connections.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
        gb_connections.configure_column("connection_name", cellStyle={"color": "blue", "font-weight": "bold"})
        grid_options_connections = gb_connections.build()
        AgGrid(connections_data, gridOptions=grid_options_connections, height=200)

    with st.expander("🛠️ Related Workflows (Click to Expand)", expanded=False):
        st.success(f"Found {len(distinct_workflow_ids)} workflows for host '{selected_host}'.")
        st.markdown("The following workflows are associated with the selected connections:")
        workflow_data = workflow_data.rename(columns={
            "id": "Id",
            "informatica_user": "Repository",
            "hierarchy_structure": "Workflow_name"
        })[["Repository", "folder_name", "Workflow_name"]]

        gb_workflows = GridOptionsBuilder.from_dataframe(workflow_data)
        gb_workflows.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
        gb_workflows.configure_column("Id", cellStyle={"color": "green"})
        gb_workflows.configure_column("Repository", cellStyle={"color": "green"})
        gb_workflows.configure_column("Workflow_name", cellStyle={"color": "blue", "font-weight": "bold"})
        grid_options_workflows = gb_workflows.build()
        AgGrid(workflow_data, gridOptions=grid_options_workflows, height=300)



def render_table_search_tab():
    """Renders the table search tab to find Informatica processes by table name."""
    st.subheader("🔍 Search Related Informatica Processes by Table Name")

    informatica_related_tables = st.session_state["cached_tables"].get("informatica_related_tables")

    if informatica_related_tables is not None and not informatica_related_tables.empty:
        search_text = st.text_input(
            "Search by table name (matches source/target/attr)",
            placeholder="e.g. ACCOUNT_UPDATER"
        )

        if search_text:
            search_text_lower = search_text.lower()

            filtered_df = informatica_related_tables[
                informatica_related_tables["source_name"].str.lower().str.contains(search_text_lower, na=False)
                | informatica_related_tables["target_name"].str.lower().str.contains(search_text_lower, na=False)
                | informatica_related_tables["attr_value"].str.lower().str.contains(search_text_lower, na=False)
            ]

            st.success(f"Found {len(filtered_df)} matching rows.")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(informatica_related_tables, use_container_width=True)
    else:
        st.warning("No data found in 'informatica_related_tables'.")
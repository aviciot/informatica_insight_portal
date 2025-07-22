import streamlit as st
import plotly.express as px
import pandas as pd

def render_workflow_comparison_chart(valid_workflows: pd.DataFrame):
    """Displays a chart comparing average durations of selected workflows."""
    st.divider()
    st.subheader("📅 Compare Average Runtime of Multiple Workflows")

    with st.expander("📊 Workflows Average Running Time"):
        all_workflow_names = valid_workflows["workflow_name"].dropna().unique()

        selected_workflows = st.multiselect(
            "Select one or more workflows to compare:",
            options=sorted(all_workflow_names),
            default=None
        )

        sort_by_duration = st.checkbox("Sort by average duration (descending)", value=True)
        orientation = st.radio("Bar orientation", ["Vertical", "Horizontal"], horizontal=True)

        if not selected_workflows:
            st.info("Please select at least one workflow to visualize.")
            return

        # Filter and group
        df = valid_workflows[valid_workflows["workflow_name"].isin(selected_workflows)]
        grouped = (
            df.groupby("workflow_name")["time_in_min"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "Average Duration (min)", "count": "Runs"})
        )
        grouped["Average Duration (min)"] = grouped["Average Duration (min)"].round(2)

        if sort_by_duration:
            grouped = grouped.sort_values("Average Duration (min)", ascending=False)

        # Plot
        if orientation == "Vertical":
            fig = px.bar(
                grouped,
                x="workflow_name",
                y="Average Duration (min)",
                color="workflow_name",
                text="Average Duration (min)",
                hover_data=["Runs"],
                title="Average Workflow Duration",
                labels={"workflow_name": "Workflow"}
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Avg Duration (min)",
                showlegend=False,
                plot_bgcolor="#f8f9fa",
                height=400
            )
            fig.update_traces(textposition="outside")
        else:
            fig = px.bar(
                grouped,
                x="Average Duration (min)",
                y="workflow_name",
                orientation="h",
                color="workflow_name",
                text="Average Duration (min)",
                hover_data=["Runs"],
                title="Average Workflow Duration",
                labels={"workflow_name": "Workflow"}
            )
            fig.update_layout(
                xaxis_title="Avg Duration (min)",
                yaxis_title="Workflow",
                showlegend=False,
                plot_bgcolor="#f8f9fa",
                height=400
            )
            fig.update_traces(textposition="outside")

        st.plotly_chart(fig, use_container_width=True)

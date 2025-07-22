import streamlit as st
import pandas as pd

def render_workflow_trend(valid_workflows: pd.DataFrame):
    """Let user choose a workflow + date range. Show runtime trend line. Return selected workflow and range."""

    st.divider()
    st.subheader("📅 Filter by Date Range")

    min_date = valid_workflows["start_time"].min().date()
    max_date = valid_workflows["end_time"].max().date()

    selected_range = st.date_input(
        "Select date range for analysis:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        st.warning("⚠️ Please select both a start and end date.")
        st.stop()

    st.divider()
    st.subheader("📈 Analyze Specific Workflow Trends")

    workflow_names = valid_workflows["workflow_name"].dropna().unique()
    selected_workflow = st.selectbox("Choose a workflow to analyze:", sorted(workflow_names))

    # Filter data
    workflow_trend_df = valid_workflows[
        (valid_workflows["workflow_name"] == selected_workflow) &
        (valid_workflows["start_time"] >= pd.to_datetime(start_date)) &
        (valid_workflows["end_time"] <= pd.to_datetime(end_date))
    ]
    ##Avi, test and remove if not needed

    workflow_trend_df = workflow_trend_df.copy()

    if workflow_trend_df.empty:
        st.warning("No valid data found for the selected workflow in the chosen date range.")
    else:
        trend = (
            workflow_trend_df
            .groupby("start_time")["time_in_min"]
            .mean()
            .reset_index()
            .rename(columns={"start_time": "date", "time_in_min": "avg_runtime"})
        )
        st.markdown(f"#### ⏳ Average Runtime Over Time for `{selected_workflow}`")
        st.line_chart(trend.set_index("date"))

    return selected_workflow, start_date, end_date


def render_long_short_table(workflow_trend_df: pd.DataFrame):
    """Displays top N longest and shortest runs for selected workflow."""
    st.divider()
    st.subheader("📅 Top Longest & Shortest Workflow Runs")

    with st.expander("📊 Longest & Shortest Workflow Runs"):
        top_n = st.slider("Choose how many runs to display:", min_value=2, max_value=10, value=5)

        if workflow_trend_df.empty:
            st.info("No workflow runs found for this workflow in the selected date range.")
            return

        workflow_trend_df.loc[:, "time_in_min"] = workflow_trend_df["time_in_min"].round(2)


        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🐢 Longest Runs")
            top_longest = (
                workflow_trend_df
                .sort_values("time_in_min", ascending=False)
                .head(top_n)[["workflow_run_id", "start_time", "end_time", "time_in_min"]]
                .rename(columns={"time_in_min": "Duration (min)"})
                .reset_index(drop=True)
            )
            st.dataframe(top_longest)

        with col2:
            st.markdown("#### ⚡ Shortest Runs")
            top_shortest = (
                workflow_trend_df
                .sort_values("time_in_min", ascending=True)
                .head(top_n)[["workflow_run_id", "start_time", "end_time", "time_in_min"]]
                .rename(columns={"time_in_min": "Duration (min)"})
                .reset_index(drop=True)
            )
            st.dataframe(top_shortest)

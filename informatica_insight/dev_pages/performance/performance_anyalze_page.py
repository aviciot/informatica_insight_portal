import streamlit as st
import pandas as pd

from .workflow_comparison import render_workflow_comparison_chart
from .workflow_trend_analysis import render_workflow_trend, render_long_short_table
from .session_analysis import render_session_summary, render_session_run_table
from .anomaly_detection import render_anomaly_insights
from .overlap_analysis import render_overlap_impact_analysis
from .ml_base_analysis import render_runtime_trend_monitor

def render_performance_tab():
    """Tabbed UI for Performance Analysis."""
    st.title("📊 Performance Analysis Dashboard")
    st.markdown("Analyze workflow execution trends, overlaps, and anomalies across your Informatica environment.")

    workflow_df = st.session_state["cached_tables"].get("workflow_run_statistics")
    session_df = st.session_state["cached_tables"].get("session_run_statistics")


    if workflow_df is None or session_df is None:
        st.warning("❌ Required data not found in cache (workflow/session stats).")
        return

    # Convert datetime
    workflow_df["start_time"] = pd.to_datetime(workflow_df["start_time"])
    workflow_df["end_time"] = pd.to_datetime(workflow_df["end_time"])
    session_df["start_time"] = pd.to_datetime(session_df["start_time"])
    session_df["end_time"] = pd.to_datetime(session_df["end_time"])

    # Clean data
    valid_workflows = workflow_df[
        workflow_df["time_in_min"].notnull() &
        (workflow_df["time_in_min"] > 0)
        ].dropna(subset=["start_time", "end_time"])

    if not valid_workflows.empty:
        first_run = valid_workflows["start_time"].min()
        last_run = valid_workflows["end_time"].max()

        st.info(
            f"📅 Workflow runs available from **{first_run.strftime('%Y-%m-%d %H:%M')}** to **{last_run.strftime('%Y-%m-%d %H:%M')}**")
    else:
        st.warning("No valid workflow runs available.")


    valid_sessions = session_df[
        session_df["time_in_min"].notnull() & (session_df["time_in_min"] > 0)
    ]

    # Tabs
    tabs = st.tabs([
        "📊 Workflow Comparison",
        "📈 Workflow and Session Analysis,Trends and Anomaly Detection",
        "🕒 Overlap Impact",
        "📈 ML Analysis ...(wip)",
    ])

    # --- Tab 1: Workflow Comparison ---
    with tabs[0]:
        render_workflow_comparison_chart(valid_workflows)

    # --- Tab 2: Workflow Trends ---
    with tabs[1]:
        selected_workflow, start_date, end_date = render_workflow_trend(valid_workflows)
        workflow_trend_df = valid_workflows[
            (valid_workflows["workflow_name"] == selected_workflow) &
            (valid_workflows["start_time"] >= pd.to_datetime(start_date)) &
            (valid_workflows["end_time"] <= pd.to_datetime(end_date))
        ]
        if not workflow_trend_df.empty:
            render_long_short_table(workflow_trend_df)
        if not workflow_trend_df.empty:
            render_session_summary(workflow_trend_df, valid_sessions)
            render_session_run_table(workflow_trend_df, valid_sessions)
        if not workflow_trend_df.empty:
            render_anomaly_insights(workflow_trend_df, valid_sessions, selected_workflow, start_date, end_date)

    # --- Tab 5: Overlap Analysis ---
    with tabs[2]:

        render_overlap_impact_analysis(workflow_df)

    with tabs[3]:
        render_runtime_trend_monitor()

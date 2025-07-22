import streamlit as st
import pandas as pd

def render_session_summary(workflow_trend_df: pd.DataFrame, valid_sessions: pd.DataFrame):
    """Displays session summary (avg/max/min/duration) for a workflow."""
    st.divider()
    st.markdown("#### 🧩 Session Stats")

    workflow_ids = workflow_trend_df["workflow_run_id"].unique()
    related_sessions = valid_sessions[valid_sessions["workflow_run_id"].isin(workflow_ids)]

    if related_sessions.empty:
        st.info("No related session data found for the selected workflow and date range.")
        return

    session_summary = (
        related_sessions
        .groupby("session_name")["time_in_min"]
        .agg(["count", "mean", "max", "min"])
        .reset_index()
        .rename(columns={
            "count": "Runs",
            "mean": "Avg Time (min)",
            "max": "Max Time (min)",
            "min": "Min Time (min)"
        })
    )

    # Round time values
    for col in ["Avg Time (min)", "Max Time (min)", "Min Time (min)"]:
        session_summary[col] = session_summary[col].round(2)

    st.dataframe(session_summary)


def render_session_run_table(workflow_trend_df: pd.DataFrame, valid_sessions: pd.DataFrame):
    """Lets the user choose a date and view detailed session runs."""
    st.markdown("#### 🔎 View Session Runs by Date")

    workflow_ids = workflow_trend_df["workflow_run_id"].unique()
    related_sessions = valid_sessions[valid_sessions["workflow_run_id"].isin(workflow_ids)]

    run_dates = sorted(workflow_trend_df["start_time"].dt.date.unique())
    selected_date = st.selectbox("Choose a date to view session details:", run_dates)

    sessions_on_day = related_sessions[
        related_sessions["start_time"].dt.date == selected_date
    ]

    if sessions_on_day.empty:
        st.info("No session runs found for the selected workflow on this date.")
    else:
        st.markdown(f"##### 📋 Session Run Details on `{selected_date}`")

        session_day_detail = sessions_on_day[[
            "session_name", "task_type_name", "start_time", "end_time",
            "time_in_min", "run_err_code", "run_err_msg"
        ]].sort_values("start_time")

        session_day_detail["time_in_min"] = session_day_detail["time_in_min"].round(2)
        st.dataframe(session_day_detail)

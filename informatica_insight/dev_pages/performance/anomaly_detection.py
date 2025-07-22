import streamlit as st
import pandas as pd

def render_anomaly_insights(
    workflow_trend_df: pd.DataFrame,
    valid_sessions: pd.DataFrame,
    selected_workflow: str,
    start_date,
    end_date
):
    st.divider()
    st.markdown(f"#### 🧠 Anomalous Insights for `{selected_workflow}`")

    with st.expander(f"🧠 Workflow Runtime Anomalies for `{selected_workflow}`"):
        if workflow_trend_df.empty:
            st.info("No data to analyze smart insights.")
            return

        avg_runtime = workflow_trend_df["time_in_min"].mean()
        std_runtime = workflow_trend_df["time_in_min"].std()
        p90_runtime = workflow_trend_df["time_in_min"].quantile(0.90)

        st.markdown(f"""
        ✅ **Average Runtime:** `{avg_runtime:.2f} min`  
        📈 **90th Percentile Runtime:** `{p90_runtime:.2f} min`  
        🧾 **Standard Deviation:** `{std_runtime:.2f} min`
        """)

        anomalies = workflow_trend_df[
            (workflow_trend_df["time_in_min"] > 2 * avg_runtime) |
            (workflow_trend_df["time_in_min"] > p90_runtime)
        ].copy()

        anomalies["time_in_min"] = anomalies["time_in_min"].round(2)
        anomalies = anomalies.sort_values("time_in_min", ascending=False)

        if anomalies.empty:
            st.success("✅ No potential anomalies detected. Workflow runs are stable. 🎉")
        else:
            st.warning(f"⚠️ {len(anomalies)} workflow run(s) flagged as unusually long.")
            st.dataframe(anomalies[[
                "workflow_run_id", "start_time", "end_time", "time_in_min"
            ]].rename(columns={"time_in_min": "Duration (min)"}).reset_index(drop=True))

    st.divider()
    with st.expander(f"🧠 Session Runtime Anomalies for `{selected_workflow}`"):
        session_subset = valid_sessions[
            (valid_sessions["workflow_name"] == selected_workflow) &
            (valid_sessions["start_time"] >= pd.to_datetime(start_date)) &
            (valid_sessions["end_time"] <= pd.to_datetime(end_date))
        ].copy()

        exclude_input = st.text_input(
            "Exclude sessions starting with (comma-separated):",
            value="wl_,_test_"
        )

        exclude_prefixes = [p.strip().lower() for p in exclude_input.split(",") if p.strip()]
        if exclude_prefixes:
            session_subset = session_subset[
                ~session_subset["session_name"].str.lower().str.startswith(tuple(exclude_prefixes))
            ]

        if session_subset.empty:
            st.info("No valid session data found after applying exclusions.")
            return

        avg_runtime = session_subset["time_in_min"].mean()
        p90_runtime = session_subset["time_in_min"].quantile(0.90)

        session_anomalies = session_subset[
            (session_subset["time_in_min"] > 2 * avg_runtime) |
            (session_subset["time_in_min"] > p90_runtime)
        ].copy()

        session_anomalies["Duration (min)"] = session_anomalies["time_in_min"].round(2)
        session_anomalies["Delta from Avg (min)"] = (
            session_anomalies["time_in_min"] - avg_runtime
        ).round(2)

        if session_anomalies.empty:
            st.success("✅ No session anomalies detected.")
        else:
            st.warning(f"⚠️ {len(session_anomalies)} session(s) flagged as unusually long.")

            st.markdown(f"**Average Session Runtime:** `{avg_runtime:.2f} min`")

            st.dataframe(session_anomalies[[
                "session_name", "workflow_run_id", "start_time", "end_time",
                "Duration (min)", "Delta from Avg (min)", "run_err_code"
            ]].reset_index(drop=True))

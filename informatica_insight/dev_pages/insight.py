import streamlit as st
import pandas as pd
import logging
from informatica_insight.dev_pages.workflows_explorer.workflow_explorer_page import render_workflow_explorer_tab
from informatica_insight.dev_pages.db_explorer.db_explorer_page import (
    render_db_related_processes_tab,
    render_table_search_tab
)


from informatica_insight.dev_pages.performance.performance_anyalze_page import render_performance_tab
logger = logging.getLogger(__name__)
logger.propagate = True


def informatica_insight():
    """Enhanced implementation for exploring related processes."""
    config = st.session_state["config"]

    tab_labels = [
        "📁 Workflows Explorer",
        "🗃️ DB Explorer",
        "🔍 Table Search",
        "📊 Performance"
    ]

    selected_tab = st.radio(
        "Select a Section",
        tab_labels,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("---")

    if selected_tab == "📁 Workflows Explorer":
        render_workflow_explorer_tab()

    elif selected_tab == "🗃️ DB Explorer":
        render_db_related_processes_tab()

    elif selected_tab == "🔍 Table Search":
        render_table_search_tab()

    elif selected_tab == "📊 Performance":
        render_performance_tab()
        #
        # st.info("🚧 Performance Analysis coming soon!")
        # st.markdown("### ⚙️ Informatica Workflow & Session Performance Analysis")
        # session_run_statistics = st.session_state["cached_tables"].get("session_run_statistics")
        # workflow_run_statistics = st.session_state["cached_tables"].get("workflow_run_statistics")
        #
        #
        # # ---------------------------
        # # Ensure datetime types
        # # ---------------------------
        # workflow_run_statistics["start_time"] = pd.to_datetime(workflow_run_statistics["start_time"])
        # workflow_run_statistics["end_time"] = pd.to_datetime(workflow_run_statistics["end_time"])
        # session_run_statistics["start_time"] = pd.to_datetime(session_run_statistics["start_time"])
        # session_run_statistics["end_time"] = pd.to_datetime(session_run_statistics["end_time"])
        #
        #
        # # ---------------------------
        # # Filter only valid records
        # # ---------------------------
        # valid_workflows = workflow_run_statistics[
        #     (workflow_run_statistics["time_in_min"].notnull()) &
        #     (workflow_run_statistics["time_in_min"] > 0)
        #     ]
        # valid_sessions = session_run_statistics[
        #     (session_run_statistics["time_in_min"].notnull()) &
        #     (session_run_statistics["time_in_min"] > 0)
        #     ]
        #
        #
        # st.divider()
        # st.subheader("📅 Compare Average Runtime of Multiple Workflows")
        #
        # with st.expander("📊 Workflows average running time"):
        #     import plotly.express as px
        #
        #     all_workflow_names = valid_workflows["workflow_name"].dropna().unique()
        #     selected_workflows = st.multiselect(
        #         "Select one or more workflows to compare:",
        #         options=sorted(all_workflow_names),
        #         default= None
        #     )
        #
        #     # 2. Additional controls
        #     sort_by_duration = st.checkbox("Sort by average duration (descending)", value=True)
        #     orientation = st.radio("Bar orientation", ["Vertical", "Horizontal"], horizontal=True)
        #
        #     # 3. Filter data based on user input
        #     if selected_workflows:
        #         multi_workflow_df = valid_workflows[
        #             (valid_workflows["workflow_name"].isin(selected_workflows))
        #             ]
        #
        #         if multi_workflow_df.empty:
        #             st.info("No data found for selected workflows in this date range.")
        #         else:
        #             # 4. Aggregate average and count
        #             grouped = (
        #                 multi_workflow_df
        #                 .groupby("workflow_name")["time_in_min"]
        #                 .agg(["mean", "count"])
        #                 .reset_index()
        #                 .rename(columns={"mean": "Average Duration (min)", "count": "Runs"})
        #             )
        #             grouped["Average Duration (min)"] = grouped["Average Duration (min)"].round(2)
        #
        #             if sort_by_duration:
        #                 grouped = grouped.sort_values("Average Duration (min)", ascending=False)
        #
        #             # 5. Plotly chart
        #             if orientation == "Vertical":
        #                 fig = px.bar(
        #                     grouped,
        #                     x="workflow_name",
        #                     y="Average Duration (min)",
        #                     color="workflow_name",
        #                     text="Average Duration (min)",
        #                     hover_data=["Runs"],
        #                     title="Average Workflow Duration",
        #                     labels={"workflow_name": "Workflow"}
        #                 )
        #                 fig.update_layout(
        #                     xaxis_tickangle=-45,
        #                     yaxis_title="Avg Duration (min)",
        #                     showlegend=False,
        #                     plot_bgcolor="#f8f9fa",
        #                     height=400
        #                 )
        #                 fig.update_traces(textposition="outside")
        #
        #             else:  # Horizontal
        #                 fig = px.bar(
        #                     grouped,
        #                     x="Average Duration (min)",
        #                     y="workflow_name",
        #                     orientation="h",
        #                     color="workflow_name",
        #                     text="Average Duration (min)",
        #                     hover_data=["Runs"],
        #                     title="Average Workflow Duration",
        #                     labels={"workflow_name": "Workflow"}
        #                 )
        #                 fig.update_layout(
        #                     xaxis_title="Avg Duration (min)",
        #                     yaxis_title="Workflow",
        #                     showlegend=False,
        #                     plot_bgcolor="#f8f9fa",
        #                     height=400
        #                 )
        #                 fig.update_traces(textposition="outside")
        #
        #             # 6. Display the chart
        #             st.plotly_chart(fig, use_container_width=True)
        #     else:
        #         st.info("Please select at least one workflow to visualize.")
        # # ---------------------------
        # # Date filter for analysis
        # # ---------------------------
        # st.subheader("📅 Filter by Date Range")
        #
        # # Calculate min/max bounds from data
        # min_date = valid_workflows["start_time"].min().date()
        # max_date = valid_workflows["end_time"].max().date()
        #
        # # Streamlit date_input (range mode)
        # selected_range = st.date_input(
        #     "Select date range for analysis:",
        #     value=(min_date, max_date),  # pass as a tuple
        #     min_value=min_date,
        #     max_value=max_date,
        # )
        #
        # # Normalize single or missing selections
        # if isinstance(selected_range, tuple) and len(selected_range) == 2:
        #     start_date, end_date = selected_range
        # else:
        #     st.warning("⚠️ Please select both a **start** and an **end** date.")
        #     st.stop()
        #
        # st.divider()
        # # ---------------------------
        # # Analyze specific workflow
        # # ---------------------------
        # st.subheader("📈 Analyze Specific Workflow Trends")
        #
        # workflow_names = valid_workflows["workflow_name"].dropna().unique()
        # selected_workflow = st.selectbox("Choose a workflow to analyze:", sorted(workflow_names))
        #
        #
        # workflow_trend_df = valid_workflows[
        #     (valid_workflows["workflow_name"] == selected_workflow) &
        #     (valid_workflows["start_time"] >= pd.to_datetime(start_date)) &
        #     (valid_workflows["end_time"] <= pd.to_datetime(end_date))
        #     ]
        #
        # if workflow_trend_df.empty:
        #     st.warning("No valid data found for the selected workflow in the chosen date range.")
        # else:
        #     # ---- Trend Over Time ----
        #     workflow_trend = (
        #         workflow_trend_df
        #         .groupby("start_time")["time_in_min"]
        #         .mean()
        #         .reset_index()
        #         .rename(columns={"start_time": "date", "time_in_min": "avg_runtime"})
        #     )
        #
        # st.divider()
        # st.subheader("📅 Top Longest & Shortest Workflow Runs")
        # with st.expander("📊 Longest & Shortest Workflow Runs"):
        #     top_n = st.slider("Choose how many runs to display:", min_value=2, max_value=10, value=5)
        #     if workflow_trend_df.empty:
        #         st.info("No workflow runs found for this workflow in the selected date range.")
        #     else:
        #         workflow_trend_df["time_in_min"] = workflow_trend_df["time_in_min"].round(2)
        #
        #         col1, col2 = st.columns(2)
        #         with col1:
        #             st.markdown("#### 🐢 Longest Runs")
        #             top_longest = (
        #                 workflow_trend_df
        #                 .sort_values("time_in_min", ascending=False)
        #                 .head(top_n)
        #                 [["workflow_run_id", "start_time", "end_time", "time_in_min"]]
        #                 .rename(columns={"time_in_min": "Duration (min)"})
        #             )
        #             top_longest = top_longest.reset_index(drop=True)
        #
        #             st.dataframe(top_longest)
        #
        #         with col2:
        #             st.markdown("#### ⚡ Shortest Runs")
        #             top_shortest = (
        #                 workflow_trend_df
        #                 .sort_values("time_in_min", ascending=True)
        #                 .head(top_n)
        #                 [["workflow_run_id", "start_time", "end_time", "time_in_min"]]
        #                 .rename(columns={"time_in_min": "Duration (min)"})
        #             )
        #             top_shortest = top_shortest.reset_index(drop=True)
        #
        #             st.dataframe(top_shortest)
        # st.divider()
        # st.markdown(f"#### ⏳ Average Runtime Over Time for `{selected_workflow}`")
        # st.line_chart(workflow_trend.set_index("date"))
        #
        # # ---- Day of Week Breakdown ----
        # st.markdown(f"#### 📅 Runtime Breakdown by Day of Week for `{selected_workflow}`")
        # workflow_trend_df["day_of_week"] = workflow_trend_df["day_of_week"].str.strip().str.capitalize()
        #
        # if workflow_trend_df.empty:
        #     st.warning("No valid workflow runs available for the selected workflow and date range.")
        # else:
        # # Group by cleaned day_of_week and compute stats
        #     dow_summary = (
        #         workflow_trend_df
        #         .groupby("day_of_week")["time_in_min"]
        #         .agg(["count", "mean", "max", "min"])
        #         .reset_index()
        #         .rename(columns={
        #             "count": "Runs",
        #             "mean": "Avg Time (min)",
        #             "max": "Max Time (min)",
        #             "min": "Min Time (min)"
        #         })
        #     )
        #
        #     # ✅ Sort by actual day order
        #     weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        #     dow_summary["day_of_week"] = pd.Categorical(
        #         dow_summary["day_of_week"],
        #         categories=weekday_order,
        #         ordered=True
        #     )
        #     dow_summary = dow_summary.sort_values("day_of_week")
        #     st.dataframe(dow_summary)
        #
        # st.divider()
        # st.markdown(f"#### 🧩 Session Stats for `{selected_workflow}`")
        #
        # # Step 1: Get workflow_run_ids for the selected workflow (within valid range)
        # workflow_ids = workflow_trend_df["workflow_run_id"].unique()
        #
        # # Step 2: Filter valid sessions matching those workflow_run_ids
        # related_sessions = valid_sessions[
        #     valid_sessions["workflow_run_id"].isin(workflow_ids)
        # ]
        #
        # if related_sessions.empty:
        #     st.info("No related session data found for the selected workflow and date range.")
        # else:
        #     # Step 3: Summarize by session name
        #     session_summary = (
        #         related_sessions
        #         .groupby("session_name")["time_in_min"]
        #         .agg(["count", "mean", "max", "min"])
        #         .reset_index()
        #         .rename(columns={
        #             "count": "Runs",
        #             "mean": "Avg Time (min)",
        #             "max": "Max Time (min)",
        #             "min": "Min Time (min)"
        #         })
        #     )
        #
        #     # Round time values
        #     session_summary["Avg Time (min)"] = session_summary["Avg Time (min)"].round(2)
        #     session_summary["Max Time (min)"] = session_summary["Max Time (min)"].round(2)
        #     session_summary["Min Time (min)"] = session_summary["Min Time (min)"].round(2)
        #
        #     # Show results
        #     st.dataframe(session_summary)
        #     st.markdown(f"#### 🔎 View Session Runs on  `{selected_workflow}`")
        #
        #     # Step 1: Get available dates for the selected workflow (within the filtered timeframe)
        #     run_dates = sorted(workflow_trend_df["start_time"].dt.date.unique())
        #
        #     # Step 2: Let user choose one
        #     selected_run_date = st.selectbox("Choose a date to view session details:", run_dates)
        #
        #     # Step 3: Filter related sessions for the selected date
        #     sessions_on_day = related_sessions[
        #         related_sessions["start_time"].dt.date == selected_run_date
        #     ]
        #
        #     if sessions_on_day.empty:
        #         st.info("No session runs found for the selected workflow on this date.")
        #     else:
        #         st.markdown(f"##### 📋 Session Run Details for `{selected_workflow}` on `{selected_run_date}`")
        #
        #         session_day_detail = sessions_on_day[[
        #             "session_name", "task_type_name", "start_time", "end_time", "time_in_min", "run_err_code", "run_err_msg"
        #         ]].sort_values("start_time")
        #
        #         # Format time_in_min
        #         session_day_detail["time_in_min"] = session_day_detail["time_in_min"].round(2)
        #
        #         st.dataframe(session_day_detail)
        #     # Filter sessions for selected workflow + date range
        #     session_subset = valid_sessions[
        #         (valid_sessions["workflow_name"] == selected_workflow) &
        #         (valid_sessions["start_time"] >= pd.to_datetime(start_date)) &
        #         (valid_sessions["end_time"] <= pd.to_datetime(end_date))
        #         ].copy()
        #     st.divider()
        #     st.markdown(f"#### 🏋️ Heavy Sessions from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**")
        #     with st.expander("🏋️ Heavy Sessions "):
        #
        #         if session_subset.empty:
        #             st.info("No session data available to analyze heavy processes.")
        #         else:
        #             # Group sessions by name and calculate stats
        #             heavy_summary = (
        #                 session_subset
        #                 .groupby("session_name")["time_in_min"]
        #                 .agg(
        #                     Runs="count",
        #                     Avg_Duration="mean",
        #                     Max_Duration="max",
        #                     Total_Time="sum"
        #                 )
        #                 .reset_index()
        #             )
        #
        #             # Round numbers for display
        #             heavy_summary["Avg_Duration"] = heavy_summary["Avg_Duration"].round(2)
        #             heavy_summary["Max_Duration"] = heavy_summary["Max_Duration"].round(2)
        #             heavy_summary["Total_Time"] = heavy_summary["Total_Time"].round(2)
        #
        #             # Sort by total time (heaviest first)
        #             heavy_summary = heavy_summary.sort_values("Total_Time", ascending=False)
        #
        #             st.markdown(
        #                 "These sessions consumed the most total runtime in the selected workflow and date range:")
        #             st.dataframe(heavy_summary.reset_index(drop=True))
        #     st.divider
        #     st.markdown(f"#### 🧠 Anomalous Insights for  `{selected_workflow}`  Workflow Performance")
        #     with st.expander(f"  **`{selected_workflow}`**  Performance"):
        #         st.info(f"""
        #         This section highlights workflow runs for **`{selected_workflow}`** that stand out as unusually long compared to normal behavior.
        #
        #         A run is flagged as **anomalous** if:
        #         - It took more than **2× the average runtime**, or
        #         - It falls into the **top 10% of longest runs (90th percentile)**
        #
        #         Use this insight to detect performance regressions, slow data days, or resource bottlenecks.
        #         """)
        #
        #         if workflow_trend_df.empty:
        #             st.info("No data to analyze smart insights.")
        #         else:
        #             # Step 1: Basic Stats
        #             avg_runtime = workflow_trend_df["time_in_min"].mean()
        #             std_runtime = workflow_trend_df["time_in_min"].std()
        #             p90_runtime = workflow_trend_df["time_in_min"].quantile(0.90)
        #
        #             st.markdown(f"""
        #             ✅ **Average Runtime:** {avg_runtime:.2f} min
        #             📈 **90th Percentile Runtime:** {p90_runtime:.2f} min
        #             🧾 **Standard Deviation:** {std_runtime:.2f} min
        #             """)
        #
        #             # Step 2: Identify potential anomalies
        #             smart_anomalies = workflow_trend_df[
        #                 (workflow_trend_df["time_in_min"] > 2 * avg_runtime) |
        #                 (workflow_trend_df["time_in_min"] > p90_runtime)
        #                 ].copy()
        #
        #             smart_anomalies["time_in_min"] = smart_anomalies["time_in_min"].round(2)
        #             smart_anomalies = smart_anomalies.sort_values("time_in_min", ascending=False)
        #
        #             if smart_anomalies.empty:
        #                 st.success("✅ No potential anomalies detected. Workflow runs are stable. 🎉")
        #             else:
        #                 st.warning(f"⚠️ {len(smart_anomalies)} run(s) flagged as unusually long.")
        #                 st.dataframe(
        #                     smart_anomalies[[
        #                         "workflow_run_id", "start_time", "end_time", "time_in_min"
        #                     ]].rename(columns={"time_in_min": "Duration (min)"})
        #                     .reset_index(drop=True)
        #                 )
        #
        #             st.divider()
        #             # User-defined session name prefixes to ignore
        #             st.markdown(f"##### 🧠 Exclude sessions")
        #             exclude_prefixes_input = st.text_input(
        #                 "Exclude sessions starting with (comma-separated):",
        #                 value="wl_,_test_"
        #             )
        #
        #             exclude_prefixes = [p.strip().lower() for p in exclude_prefixes_input.split(",") if p.strip()]
        #
        #
        #             # Apply exclusion filter
        #             if exclude_prefixes:
        #                 session_subset = session_subset[
        #                     ~session_subset["session_name"].str.lower().str.startswith(tuple(exclude_prefixes))
        #                 ]
        #
        #
        #             st.info(f"""
        #                This section highlights **sessions** under workflow **`{selected_workflow}`** that ran unusually long.
        #
        #                A session is flagged as **anomalous** if:
        #                - It took more than **2× the average session runtime**, or
        #                - It falls into the **top 10% of longest session runs (90th percentile)**
        #
        #                Sessions starting with: `{", ".join(exclude_prefixes)}` are excluded from analysis.
        #                """)
        #
        #             if session_subset.empty:
        #                 st.info("No valid session data found after applying exclusions.")
        #             else:
        #                 avg_session_runtime = session_subset["time_in_min"].mean()
        #                 p90_session_runtime = session_subset["time_in_min"].quantile(0.90)
        #
        #                 # Flag anomalies
        #                 session_anomalies = session_subset[
        #                     (session_subset["time_in_min"] > 2 * avg_session_runtime) |
        #                     (session_subset["time_in_min"] > p90_session_runtime)
        #                     ].copy()
        #
        #                 session_anomalies["time_in_min"] = session_anomalies["time_in_min"].round(2)
        #
        #                 if session_anomalies.empty:
        #                     st.success("✅ No session anomalies detected — all sessions ran within normal thresholds.")
        #                 else:
        #                     st.warning(f"⚠️ {len(session_anomalies)} session(s) flagged as unusually long.")
        #
        #                     # Add column showing how far each anomaly is from the average
        #                     session_anomalies["Delta from Avg (min)"] = (
        #                             session_anomalies["time_in_min"] - avg_session_runtime
        #                     ).round(2)
        #
        #                     # Round duration for consistency
        #                     session_anomalies["time_in_min"] = session_anomalies["time_in_min"].round(2)
        #
        #                     st.markdown(f"**Average Session Runtime:** `{avg_session_runtime:.2f} min`")
        #
        #                     st.dataframe(
        #                         session_anomalies[[
        #                             "session_name",
        #                             "workflow_run_id",
        #                             "start_time",
        #                             "end_time",
        #                             "time_in_min",
        #                             "Delta from Avg (min)",
        #                             "run_err_code"
        #                         ]].rename(columns={"time_in_min": "Duration (min)"})
        #                         .reset_index(drop=True)
        #                     )

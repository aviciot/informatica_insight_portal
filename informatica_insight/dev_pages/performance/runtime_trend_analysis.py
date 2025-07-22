# runtime_trend_analysis.py
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

def render_runtime_trend_monitor():
    df = st.session_state["cached_tables"].get("workflow_run_statistics")
    if df is None or df.empty:
        st.warning("No workflow run statistics found in cache.")
        return

    df = df.dropna(subset=["workflow_name", "start_time", "time_in_min"])
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["time_in_min"] = pd.to_numeric(df["time_in_min"], errors="coerce")

    tabs = st.tabs([
        "📈 Workflow Runtime Trends",
        "📆 Daily & Hourly Trends",
        "📊 Advanced Temporal Insights"
    ])

    # --- TAB 1: Workflow Trend Over Time ---
    with tabs[0]:
        st.subheader("📈 Workflow Runtime Trend Monitor")

        workflow_names = sorted(df["workflow_name"].unique())
        selected_workflows = st.multiselect("Select workflows to monitor:", workflow_names)

        if not selected_workflows:
            st.info("Please select one or more workflows to view runtime trends.")
            return

        num_days = st.slider("Look back window (days):", min_value=1, max_value=90, value=30)
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=num_days)

        trend_df = df[
            (df["workflow_name"].isin(selected_workflows)) &
            (df["start_time"] >= cutoff_date)
        ].copy()

        if trend_df.empty:
            st.warning("No data found in the selected date range.")
            return

        st.markdown(f"### 📊 Average Runtime Trend (Last {num_days} Days)")
        st.info(
            """
            This chart shows how each selected workflow's average daily runtime has changed over the selected time window.
            - **Colored markers** show the actual average runtime per day.
            - **Dashed lines** represent trend lines (using linear regression) to help spot increasing or decreasing patterns.
            - If the dashed line is steeply rising, the workflow may be slowing down over time.
            """
        )

        trend_df["date"] = trend_df["start_time"].dt.date

        summary = (
            trend_df
            .groupby(["workflow_name", "date"])["time_in_min"]
            .mean()
            .reset_index()
            .rename(columns={"time_in_min": "avg_runtime"})
        )

        trend_alerts = []
        regression_lines = pd.DataFrame()

        for wf in selected_workflows:
            wf_data = summary[summary["workflow_name"] == wf]
            if len(wf_data) < 5:
                continue

            wf_data = wf_data.sort_values("date")
            X = np.arange(len(wf_data)).reshape(-1, 1)
            y = wf_data["avg_runtime"].values.reshape(-1, 1)
            model = LinearRegression().fit(X, y)
            slope = model.coef_[0][0]

            wf_data = wf_data.copy()
            wf_data["regression"] = model.predict(X)
            wf_data["workflow_name"] = wf
            regression_lines = pd.concat([regression_lines, wf_data], ignore_index=True)

            if slope > 0.5:
                trend_alerts.append((wf, round(slope, 2)))

        if trend_alerts:
            st.warning("⚠️ The following workflows show a significant upward trend in runtime:")
            for wf, slope in trend_alerts:
                st.markdown(f"- **{wf}** (slope = +{slope} min/day)")

        fig = px.line(
            summary,
            x="date",
            y="avg_runtime",
            color="workflow_name",
            markers=True,
            labels={"avg_runtime": "Avg Duration (min)", "date": "Date"},
            title="Workflow Runtime Trend Over Time"
        )
        fig.update_layout(height=500, plot_bgcolor="#f8f9fa")

        if not regression_lines.empty and "workflow_name" in regression_lines.columns:
            for wf in regression_lines["workflow_name"].unique():
                wf_data = regression_lines[regression_lines["workflow_name"] == wf]
                fig.add_scatter(
                    x=wf_data["date"],
                    y=wf_data["regression"],
                    mode="lines",
                    name=f"{wf} Trend",
                    line=dict(dash="dash")
                )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(summary.sort_values(["workflow_name", "date"], ascending=[True, False]))

    # --- TAB 2: Daily & Hourly Trends ---
    with tabs[1]:
        st.subheader("📆 Daily & Hourly Runtime Trends")
        st.info("""
        Understand execution patterns across days and hours.
        - Helps identify scheduling hotspots or slow periods
        - Useful for planning parallelization or resource allocation
        """)

        df["day_of_week"] = df["start_time"].dt.day_name()
        df["hour"] = df["start_time"].dt.hour

        daily = (
            df.groupby("day_of_week")["time_in_min"]
            .mean()
            .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            .reset_index()
        )

        hourly = (
            df.groupby("hour")["time_in_min"]
            .mean()
            .reset_index()
            .sort_values("hour")
        )

        st.markdown("#### 🗓️ Average Runtime by Day of Week")
        st.bar_chart(daily.set_index("day_of_week"))

        st.markdown("#### ⏰ Average Runtime by Hour of Day")
        st.line_chart(hourly.set_index("hour"))

    # --- TAB 3: Advanced Temporal Insights ---
    with tabs[2]:
        st.subheader("📊 Advanced Temporal Insights")

        st.markdown("### 🔁 Weekend vs Weekday Performance")
        df["is_weekend"] = df["start_time"].dt.dayofweek >= 5
        weekend_stats = (
            df.groupby("is_weekend")["time_in_min"]
            .mean()
            .reset_index()
            .replace({True: "Weekend", False: "Weekday"})
            .rename(columns={"is_weekend": "Day Type", "time_in_min": "Average Duration (min)"})
        )
        st.bar_chart(weekend_stats.set_index("Day Type"))

        st.markdown("### ❌ Failed Runs by Day of Week")
        if "run_err_code" in df.columns:
            df["failed"] = df["run_err_code"].notnull() & (df["run_err_code"] != "0")
            failed_by_day = (
                df[df["failed"]]
                .groupby("day_of_week")
                .size()
                .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                .fillna(0)
            )
            st.bar_chart(failed_by_day)

        st.markdown("### 🔥 Heatmap: Hour vs Day")
        heatmap_data = (
            df.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0).reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
        )
        st.dataframe(heatmap_data.style.background_gradient(cmap="Blues"))

        st.markdown("### 📦 Box Plot of Runtime by Day")
        fig_box = px.box(df, x="day_of_week", y="time_in_min", points="outliers",
                         category_orders={"day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                         labels={"time_in_min": "Duration (min)", "day_of_week": "Day"},
                         title="Runtime Distribution by Day")
        st.plotly_chart(fig_box, use_container_width=True)

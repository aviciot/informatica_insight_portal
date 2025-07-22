import streamlit as st
import pandas as pd
import numpy as np


def render_overlap_impact_analysis(workflow_run_df: pd.DataFrame):
    """Allows user to select workflows or scan all under a server to see concurrency impact."""

    def detect_overlap_cross_workflows_detailed(target_df, reference_df, workflow_map):
        target_df = target_df.sort_values("start_time").reset_index(drop=True)
        target_df["run_context"] = "solo"
        target_df["overlapped_with"] = ""

        for i, row in target_df.iterrows():
            start, end = row["start_time"], row["end_time"]
            run_id = row["workflow_run_id"]

            overlaps = reference_df[
                (reference_df["workflow_run_id"] != run_id) &
                (reference_df["start_time"] < end) &
                (reference_df["end_time"] > start)
            ]

            if not overlaps.empty:
                target_df.at[i, "run_context"] = "overlapped"
                overlapped_names = overlaps["workflow_id"].map(workflow_map).dropna().unique().tolist()
                target_df.at[i, "overlapped_with"] = ", ".join(overlapped_names)

        return target_df

    workflow_roots = st.session_state["cached_tables"].get("v_workflows_root")

    st.divider()
    st.subheader("🕒 Workflow Concurrency & Performance Impact")

    st.markdown("""
    Detect if workflows run slower when overlapping with others in the same environment.
    """)

    if workflow_roots is None or workflow_roots.empty:
        st.warning("❌ `v_workflows_root` is missing or empty.")
        return

    if workflow_run_df is None or workflow_run_df.empty:
        st.warning("❌ `workflow_run_statistics` is missing or empty.")
        return

    # Ensure clean datetime and workflow_id
    workflow_run_df["start_time"] = pd.to_datetime(workflow_run_df["start_time"])
    workflow_run_df["end_time"] = pd.to_datetime(workflow_run_df["end_time"])
    workflow_run_df = workflow_run_df.dropna(subset=["start_time", "end_time", "workflow_id"])

    mode = st.radio("Choose analysis mode:", ["Selected Folder Workflows", "Entire Server Scan"], horizontal=True)
    servers = workflow_roots["informatica_server"].dropna().unique()
    selected_server = st.selectbox("Server", options=sorted(servers))

    results = []

    if mode == "Selected Folder Workflows":
        col1, col2 = st.columns(2)
        with col1:
            repositories = workflow_roots[
                workflow_roots["informatica_server"] == selected_server
            ]["informatica_user"].dropna().unique()
            selected_repository = st.selectbox("Repository", options=sorted(repositories))

        with col2:
            folders = workflow_roots[
                (workflow_roots["informatica_server"] == selected_server) &
                (workflow_roots["informatica_user"] == selected_repository)
            ]["folder_name"].dropna().unique()
            selected_folder = st.selectbox("Folder", options=sorted(folders))

        workflows = workflow_roots[
            (workflow_roots["informatica_server"] == selected_server) &
            (workflow_roots["informatica_user"] == selected_repository) &
            (workflow_roots["folder_name"] == selected_folder)
        ][["session_wf_name", "workflow_id"]].drop_duplicates()

        if workflows.empty:
            st.warning("No workflows available for selected context.")
            return

        selected_workflow_names = st.multiselect(
            "Select workflows to analyze overlap impact:",
            options=sorted(workflows["session_wf_name"].tolist())
        )

        selected_workflow_ids = workflows[
            workflows["session_wf_name"].isin(selected_workflow_names)
        ]["workflow_id"].tolist()

        if not selected_workflow_ids:
            st.info("Please select at least one workflow to continue.")
            return

        filtered_runs = workflow_run_df[
            workflow_run_df["workflow_id"].isin(selected_workflow_ids)
        ].copy()

        workflow_map = workflows.set_index("workflow_id")["session_wf_name"].to_dict()

        for wf_id in filtered_runs["workflow_id"].unique():
            wf_name = workflow_map.get(wf_id, f"Workflow {wf_id}")
            wf_runs = filtered_runs[filtered_runs["workflow_id"] == wf_id].copy()

            if wf_runs.empty or len(wf_runs) < 2:
                continue

            wf_runs = detect_overlap_cross_workflows_detailed(wf_runs, filtered_runs, workflow_map)

            summary = (
                wf_runs.groupby("run_context")["time_in_min"]
                .agg(["mean", "count"])
                .rename(columns={"mean": "Avg Duration", "count": "Runs"})
            )

            avg_solo = summary.loc["solo", "Avg Duration"] if "solo" in summary.index else None
            avg_overlap = summary.loc["overlapped", "Avg Duration"] if "overlapped" in summary.index else None
            overlap_count = summary.loc["overlapped", "Runs"] if "overlapped" in summary.index else 0
            delta = (avg_overlap - avg_solo) if (avg_solo and avg_overlap) else None

            # Get other overlapping workflows (only if impacted)
            overlapped_with_set = (
                wf_runs[wf_runs["run_context"] == "overlapped"]["overlapped_with"]
                .str.split(", ")
                .explode()
                .dropna()
                .unique()
                .tolist()
            )
            overlapped_with_str = ", ".join(sorted(set(overlapped_with_set))) if overlapped_with_set else "-"

            results.append({
                "Workflow": wf_name,
                "Avg Solo (min)": round(avg_solo, 2) if avg_solo is not None else np.nan,
                "Avg Overlapped (min)": round(avg_overlap, 2) if avg_overlap is not None else np.nan,
                "Delta (min)": round(delta, 2) if delta is not None else np.nan,
                "Overlap Runs": overlap_count,
                "Impact": "⚠️ Slower When Overlapped" if delta and delta > 1 else "✅ Stable",
                "Overlapped With": overlapped_with_str if delta and delta > 1 else "-"
            })

    else:
        server_workflows = workflow_roots[
            workflow_roots["informatica_server"] == selected_server
        ][["workflow_id", "session_wf_name"]].drop_duplicates()

        workflow_ids = server_workflows["workflow_id"].tolist()
        filtered_runs = workflow_run_df[
            workflow_run_df["workflow_id"].isin(workflow_ids)
        ].copy()

        if filtered_runs.empty:
            st.warning("No workflow runs found for this server.")
            return

        workflow_map = server_workflows.set_index("workflow_id")["session_wf_name"].to_dict()

        st.info("⚠️ Entire Server Scan may take some time depending on data size...")
        progress = st.progress(0, text="Analyzing workflows...")

        total = len(workflow_ids)
        chunk = 1 / total if total else 1

        for i, wf_id in enumerate(workflow_ids):
            wf_name = workflow_map.get(wf_id, f"Workflow {wf_id}")
            wf_runs = filtered_runs[filtered_runs["workflow_id"] == wf_id].copy()

            if wf_runs.empty or len(wf_runs) < 2:
                progress.progress(min(1.0, (i + 1) * chunk), text=f"Skipping: {wf_name}")
                continue

            wf_runs = detect_overlap_cross_workflows_detailed(wf_runs, filtered_runs, workflow_map)

            summary = (
                wf_runs.groupby("run_context")["time_in_min"]
                .agg(["mean", "count"])
                .rename(columns={"mean": "Avg Duration", "count": "Runs"})
            )

            avg_solo = summary.loc["solo", "Avg Duration"] if "solo" in summary.index else None
            avg_overlap = summary.loc["overlapped", "Avg Duration"] if "overlapped" in summary.index else None
            overlap_count = summary.loc["overlapped", "Runs"] if "overlapped" in summary.index else 0
            delta = (avg_overlap - avg_solo) if (avg_solo and avg_overlap) else None

            overlapped_with_set = (
                wf_runs[wf_runs["run_context"] == "overlapped"]["overlapped_with"]
                .str.split(", ")
                .explode()
                .dropna()
                .unique()
                .tolist()
            )
            overlapped_with_str = ", ".join(sorted(set(overlapped_with_set))) if overlapped_with_set else "-"

            results.append({
                "Workflow": wf_name,
                "Avg Solo (min)": round(avg_solo, 2) if avg_solo is not None else np.nan,
                "Avg Overlapped (min)": round(avg_overlap, 2) if avg_overlap is not None else np.nan,
                "Delta (min)": round(delta, 2) if delta is not None else np.nan,
                "Overlap Runs": overlap_count,
                "Impact": "⚠️ Slower When Overlapped" if delta and delta > 1 else "✅ Stable",
                "Overlapped With": overlapped_with_str if delta and delta > 1 else "-"
            })

            progress.progress(min(1.0, (i + 1) * chunk), text=f"Analyzed: {wf_name}")

        progress.empty()

    if results:
        st.markdown("### 🧾 Overlap Impact Summary")
        st.dataframe(pd.DataFrame(results))
    else:
        st.info("No sufficient run data to calculate overlap impact.")

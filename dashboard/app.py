import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="QA Dashboard", layout="wide")
st.title("AI Test Orchestrator — QA Dashboard")

EXECUTION_LOG = "reports/execution_log.json"
PIPELINE_LOG = "logs/pipeline.log"


def load_executions():
    if not os.path.exists(EXECUTION_LOG):
        return pd.DataFrame()
    with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
        records = json.load(f)
    return pd.DataFrame(records)


def load_pipeline_log():
    if not os.path.exists(PIPELINE_LOG):
        return pd.DataFrame()
    entries = []
    with open(PIPELINE_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return pd.DataFrame(entries)


st.sidebar.header("Filters")
df = load_executions()
log_df = load_pipeline_log()

# Overview metrics
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)

total_runs = len(df)
success_runs = len(df[df["status"] == "success"]) if not df.empty else 0
success_rate = round(success_runs / total_runs * 100, 1) if total_runs > 0 else 0
total_cost = round(df["metrics"].apply(lambda m: m.get("estimated_cost_usd", 0)).sum(), 4) if not df.empty else 0

col1.metric("Total Executions", total_runs)
col2.metric("Success Rate", f"{success_rate}%")
col3.metric("Estimated Cost", f"${total_cost}")
col4.metric("Models Used", ", ".join(df["model"].unique()) if not df.empty else "-")

# Execution history
st.subheader("Execution History")
if not df.empty:
    display = df.copy()
    display["timestamp"] = pd.to_datetime(display["timestamp"])
    display = display.sort_values("timestamp", ascending=False)
    display["duration"] = display["metrics"].apply(
        lambda m: m.get("execution_time_s", "-") if isinstance(m, dict) else "-"
    )
    st.dataframe(
        display[["execution_id", "timestamp", "feature", "model", "status", "metrics"]],
        use_container_width=True,
        column_config={
            "execution_id": "Execution ID",
            "timestamp": "Timestamp",
            "feature": "Feature",
            "model": "Model",
            "status": st.column_config.TextColumn("Status", help="pass/fail"),
            "metrics": st.column_config.JsonColumn("Metrics", help="Step details")
        }
    )
else:
    st.info("No execution history yet. Run the pipeline first.")

# KPI trends
st.subheader("KPI Trends")
if not df.empty:
    df_ts = df.copy()
    df_ts["timestamp"] = pd.to_datetime(df_ts["timestamp"])
    df_ts = df_ts.sort_values("timestamp")
    df_ts["run_number"] = range(1, len(df_ts) + 1)
    df_ts["cost"] = df_ts["metrics"].apply(lambda m: m.get("estimated_cost_usd", 0))
    df_ts["roi"] = df_ts["metrics"].apply(lambda m: m.get("estimated_roi", 0))
    df_ts["tokens"] = df_ts["metrics"].apply(lambda m: m.get("estimated_tokens", 0))

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.line_chart(df_ts.set_index("run_number")["cost"])
        st.caption("Estimated Cost per Run")
    with chart_col2:
        st.line_chart(df_ts.set_index("run_number")["roi"])
        st.caption("Estimated ROI % per Run")

# Pipeline log timeline
st.subheader("Pipeline Log (Recent)")
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
    log_df = log_df.sort_values("timestamp", ascending=False).head(50)
    st.dataframe(log_df[["timestamp", "action", "details"]], use_container_width=True)
else:
    st.info("No pipeline log yet.")

# Success distribution
st.subheader("Status Distribution")
if not df.empty:
    status_counts = df["status"].value_counts()
    st.bar_chart(status_counts)
else:
    st.info("No data available.")

import streamlit as st
from utils.db import run_query
from utils.filters import get_sidebar_filters

st.set_page_config(page_title="Grid Operations", layout="wide", page_icon="🔌")
st.title("🔌 Grid Operations")

filters = get_sidebar_filters(show_date_range=True)
start, end = filters["start_date"], filters["end_date"]

# ── KPIs ──────────────────────────────────────────────────────────────────────
stats = run_query(f"""
    SELECT
        metric_name,
        AVG(metric_value) AS avg_val,
        MAX(metric_value) AS max_val
    FROM staging.stg_ercot_region_hourly
    WHERE metric_name IN ('Demand', 'Net generation', 'Day-ahead demand forecast')
      AND datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY metric_name;
""")
stats_dict = stats.set_index("metric_name").to_dict("index")

c1, c2, c3 = st.columns(3)
if "Demand" in stats_dict:
    c1.metric("Avg Demand", f"{stats_dict['Demand']['avg_val']:,.0f} MWh")
    c2.metric("Peak Demand", f"{stats_dict['Demand']['max_val']:,.0f} MWh")
if "Net generation" in stats_dict:
    c3.metric("Avg Net Generation", f"{stats_dict['Net generation']['avg_val']:,.0f} MWh")

st.divider()

# ── Demand vs Forecast ────────────────────────────────────────────────────────
st.subheader("Daily Demand vs. Day-Ahead Forecast")
daily = run_query(f"""
    SELECT
        DATE(datetime_hour) AS dt,
        metric_name,
        AVG(metric_value) AS avg_val
    FROM staging.stg_ercot_region_hourly
    WHERE metric_name IN ('Demand', 'Day-ahead demand forecast')
      AND datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY dt, metric_name
    ORDER BY dt;
""")

pivot = daily.pivot(index="dt", columns="metric_name", values="avg_val")
pivot.index = pivot.index.astype(str)
st.line_chart(pivot)

st.divider()

# ── Net Generation trend ──────────────────────────────────────────────────────
st.subheader("Net Generation Over Time")
gen = run_query(f"""
    SELECT DATE(datetime_hour) AS dt, AVG(metric_value) AS avg_gen
    FROM staging.stg_ercot_region_hourly
    WHERE metric_name = 'Net generation'
      AND datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY dt
    ORDER BY dt;
""")
gen["dt"] = gen["dt"].astype(str)
st.line_chart(gen.set_index("dt")["avg_gen"])

st.divider()

# ── Forecast error ────────────────────────────────────────────────────────────
st.subheader("Forecast Error (Actual − Forecast)")
if "Demand" in pivot.columns and "Day-ahead demand forecast" in pivot.columns:
    pivot["Forecast Error"] = pivot["Demand"] - pivot["Day-ahead demand forecast"]
    st.line_chart(pivot["Forecast Error"])
else:
    st.info("Not enough data to compute forecast error for this date range.")

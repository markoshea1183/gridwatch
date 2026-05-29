import streamlit as st
from utils.db import run_query

st.set_page_config(page_title="ERCOT Dashboard", layout="wide", page_icon="⚡")

st.title("⚡ ERCOT Energy Market Dashboard")
st.caption(
    "Exploratory dashboard for ERCOT prices, demand, weather, fuel mix, "
    "renewable resources, natural gas prices, and holidays."
)

# ── KPI Cards ────────────────────────────────────────────────────────────────
tables = run_query("""
    SELECT table_name, table_rows
    FROM information_schema.tables
    WHERE table_schema = 'staging'
    ORDER BY table_name;
""")
tables.columns = ["Table", "Rows"]
tables["Rows"] = tables["Rows"].astype(int)

avg_price = run_query("""
    SELECT AVG(settlement_point_price) AS avg_price
    FROM staging.stg_ercot_dam_prices;
""")["avg_price"].iloc[0]

peak_demand = run_query("""
    SELECT MAX(metric_value) AS peak
    FROM staging.stg_ercot_region_hourly
    WHERE metric_name = 'Demand';
""")["peak"].iloc[0]

top_fuel = run_query("""
    SELECT fuel_type_name, SUM(generation_mwh) AS total
    FROM staging.stg_ercot_fuel_mix
    GROUP BY fuel_type_name
    ORDER BY total DESC
    LIMIT 1;
""")["fuel_type_name"].iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Staging Tables", len(tables))
col2.metric("Total Rows", f"{tables['Rows'].sum():,}")
col3.metric("Avg DAM Price", f"${avg_price:.2f}/MWh")
col4.metric("Peak Demand", f"{peak_demand:,.0f} MWh")
col5.metric("Top Fuel Source", top_fuel)

st.divider()

# ── Table Inventory ───────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Staging Tables")
    pretty = tables.copy()
    pretty["Table"] = (
        pretty["Table"]
        .str.replace("stg_", "", regex=False)
        .str.replace("_", " ")
        .str.title()
    )
    st.dataframe(pretty, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("Rows by Table")
    st.bar_chart(pretty.set_index("Table")["Rows"])

st.divider()

# ── Sparklines ────────────────────────────────────────────────────────────────
st.subheader("Recent Trends")

spark_col1, spark_col2 = st.columns(2)

with spark_col1:
    st.caption("Average Daily DAM Price (last 90 days)")
    prices_spark = run_query("""
        SELECT delivery_date, AVG(settlement_point_price) AS avg_price
        FROM staging.stg_ercot_dam_prices
        GROUP BY delivery_date
        ORDER BY delivery_date DESC
        LIMIT 90;
    """)
    prices_spark["delivery_date"] = prices_spark["delivery_date"].astype(str)
    st.line_chart(prices_spark.set_index("delivery_date")["avg_price"])

with spark_col2:
    st.caption("Average Daily Demand (last 90 days)")
    demand_spark = run_query("""
        SELECT DATE(datetime_hour) AS dt, AVG(metric_value) AS avg_demand
        FROM staging.stg_ercot_region_hourly
        WHERE metric_name = 'Demand'
        GROUP BY dt
        ORDER BY dt DESC
        LIMIT 90;
    """)
    demand_spark["dt"] = demand_spark["dt"].astype(str)
    st.line_chart(demand_spark.set_index("dt")["avg_demand"])

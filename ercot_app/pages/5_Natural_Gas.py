import streamlit as st
from utils.db import run_query
from utils.filters import get_sidebar_filters
from utils.charts import scatter_chart

st.set_page_config(page_title="Natural Gas", layout="wide", page_icon="🔥")
st.title("🔥 Natural Gas Prices")

filters = get_sidebar_filters(show_date_range=True)
start, end = filters["start_date"], filters["end_date"]

# ── KPIs ──────────────────────────────────────────────────────────────────────
stats = run_query(f"""
    SELECT
        AVG(price) AS avg_price,
        MAX(price) AS max_price,
        MIN(price) AS min_price
    FROM staging.stg_eia_natural_gas_prices
    WHERE price_date BETWEEN '{start}' AND '{end}';
""")

c1, c2, c3 = st.columns(3)
c1.metric("Avg Gas Price", f"${stats['avg_price'].iloc[0]:.2f}/MMBtu")
c2.metric("Max Gas Price", f"${stats['max_price'].iloc[0]:.2f}/MMBtu")
c3.metric("Min Gas Price", f"${stats['min_price'].iloc[0]:.2f}/MMBtu")

st.divider()

# ── Gas price trend ───────────────────────────────────────────────────────────
st.subheader("Natural Gas Price Over Time")

gas = run_query(f"""
    SELECT
        DATE(price_date) AS dt,
        AVG(price) AS avg_price
    FROM staging.stg_eia_natural_gas_prices
    WHERE price_date BETWEEN '{start}' AND '{end}'
    GROUP BY dt
    ORDER BY dt;
""")

if gas.empty:
    st.info("No natural gas price data available for this date range.")
else:
    gas["dt"] = gas["dt"].astype(str)
    st.line_chart(gas.set_index("dt")["avg_price"])

st.divider()

# ── Gas vs Electricity price ──────────────────────────────────────────────────
st.subheader("Natural Gas vs. Electricity Price Correlation")

gas_elec = run_query(f"""
    SELECT
        DATE(g.price_date) AS dt,
        AVG(g.price) AS avg_gas,
        AVG(p.settlement_point_price) AS avg_elec
    FROM staging.stg_eia_natural_gas_prices g
    JOIN staging.stg_ercot_dam_prices p
        ON DATE(g.price_date) = DATE(p.datetime_hour)
    WHERE g.price_date BETWEEN '{start}' AND '{end}'
    GROUP BY dt
    ORDER BY dt;
""")

if gas_elec.empty:
    st.info("No overlapping natural gas and ERCOT DAM price data available for this date range.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Gas vs. Electricity Price")
        combined = gas_elec.set_index("dt")[["avg_gas", "avg_elec"]]
        combined.index = combined.index.astype(str)
        st.line_chart(combined)

    with col2:
        st.caption("Scatter: Gas Price vs. Electricity Price")
        scatter_chart(
            gas_elec,
            "avg_gas",
            "avg_elec",
            "Gas Price vs. Electricity Price",
            "Gas Price ($/MMBtu)",
            "Electricity Price ($/MWh)",
        )
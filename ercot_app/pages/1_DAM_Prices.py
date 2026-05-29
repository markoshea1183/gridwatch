import streamlit as st
from utils.db import run_query
from utils.filters import get_sidebar_filters
from utils.charts import line_chart, histogram

st.set_page_config(page_title="DAM Prices", layout="wide", page_icon="💲")
st.title("💲 Day-Ahead Market Prices")

filters = get_sidebar_filters(show_date_range=True, show_zone=True)
start, end = filters["start_date"], filters["end_date"]
zone = filters["zone"]

zone_clause = "" if zone == "All" else f"AND settlement_point = '{zone}'"

# ── KPIs ──────────────────────────────────────────────────────────────────────
stats = run_query(f"""
    SELECT
        AVG(settlement_point_price)  AS avg_price,
        MAX(settlement_point_price)  AS max_price,
        MIN(settlement_point_price)  AS min_price,
        COUNT(DISTINCT delivery_date) AS days
    FROM staging.stg_ercot_dam_prices
    WHERE delivery_date BETWEEN '{start}' AND '{end}'
    {zone_clause};
""")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Price", f"${stats['avg_price'].iloc[0]:.2f}/MWh")
c2.metric("Max Price", f"${stats['max_price'].iloc[0]:.2f}/MWh")
c3.metric("Min Price", f"${stats['min_price'].iloc[0]:.2f}/MWh")
c4.metric("Days Covered", int(stats["days"].iloc[0]))

st.divider()

# ── Daily trend ───────────────────────────────────────────────────────────────
st.subheader("Average Daily Price")
daily = run_query(f"""
    SELECT delivery_date, AVG(settlement_point_price) AS avg_price
    FROM staging.stg_ercot_dam_prices
    WHERE delivery_date BETWEEN '{start}' AND '{end}'
    {zone_clause}
    GROUP BY delivery_date
    ORDER BY delivery_date;
""")
daily["delivery_date"] = daily["delivery_date"].astype(str)
st.line_chart(daily.set_index("delivery_date")["avg_price"])

st.divider()

# ── By zone ───────────────────────────────────────────────────────────────────
st.subheader("Price by Settlement Zone")
by_zone = run_query(f"""
    SELECT settlement_point, AVG(settlement_point_price) AS avg_price
    FROM staging.stg_ercot_dam_prices
    WHERE delivery_date BETWEEN '{start}' AND '{end}'
    GROUP BY settlement_point
    ORDER BY avg_price DESC;
""")
st.bar_chart(by_zone.set_index("settlement_point")["avg_price"])

st.divider()

# ── Distribution ──────────────────────────────────────────────────────────────
st.subheader("Price Distribution")
prices = run_query(f"""
    SELECT settlement_point_price
    FROM staging.stg_ercot_dam_prices
    WHERE delivery_date BETWEEN '{start}' AND '{end}'
    {zone_clause};
""")
histogram(prices, "settlement_point_price", "Distribution of DAM Prices", "Price ($/MWh)")

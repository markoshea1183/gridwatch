import streamlit as st
from utils.db import run_query
from utils.filters import get_sidebar_filters
from utils.charts import stacked_area

st.set_page_config(page_title="Fuel Mix", layout="wide", page_icon="⚙️")
st.title("⚙️ Fuel Mix")

filters = get_sidebar_filters(show_date_range=True)
start, end = filters["start_date"], filters["end_date"]

# ── KPIs ──────────────────────────────────────────────────────────────────────
totals = run_query(f"""
    SELECT fuel_type_name, SUM(generation_mwh) AS total_mwh
    FROM staging.stg_ercot_fuel_mix
    WHERE datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY fuel_type_name
    ORDER BY total_mwh DESC;
""")

grand_total = totals["total_mwh"].sum()
top_fuel = totals.iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Total Generation", f"{grand_total/1e6:.2f} TWh")
c2.metric("Top Fuel", top_fuel["fuel_type_name"])
c3.metric("Top Fuel Share", f"{100 * top_fuel['total_mwh'] / grand_total:.1f}%")

st.divider()

# ── Share pie (bar) ───────────────────────────────────────────────────────────
st.subheader("Generation Share by Fuel Type")
totals_pct = totals.copy()
totals_pct["share_pct"] = 100 * totals_pct["total_mwh"] / grand_total
st.bar_chart(totals_pct.set_index("fuel_type_name")["share_pct"])

st.divider()

# ── Stacked area over time ────────────────────────────────────────────────────
st.subheader("Daily Generation by Fuel Type")
daily_mix = run_query(f"""
    SELECT DATE(datetime_hour) AS dt, fuel_type_name, SUM(generation_mwh) AS mwh
    FROM staging.stg_ercot_fuel_mix
    WHERE datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY dt, fuel_type_name
    ORDER BY dt;
""")

pivot = daily_mix.pivot(index="dt", columns="fuel_type_name", values="mwh").fillna(0)
pivot.index = pivot.index.astype(str)

# Use Streamlit's native area chart for interactivity
st.area_chart(pivot)

st.divider()

# ── Renewables vs Fossil ──────────────────────────────────────────────────────
st.subheader("Renewables vs. Fossil Fuels Over Time")
daily_mix["category"] = daily_mix["fuel_type_name"].map(
    lambda f: "Renewable" if f in ("Solar", "Wind", "Hydro") else "Fossil / Other"
)
cat_daily = (
    daily_mix.groupby(["dt", "category"])["mwh"]
    .sum()
    .reset_index()
)
cat_pivot = cat_daily.pivot(index="dt", columns="category", values="mwh").fillna(0)
cat_pivot.index = cat_pivot.index.astype(str)
st.line_chart(cat_pivot)

import streamlit as st
from utils.db import run_query
from utils.filters import get_sidebar_filters
from utils.charts import line_chart, scatter_chart

st.set_page_config(page_title="Weather & Renewables", layout="wide", page_icon="🌤️")
st.title("🌤️ Weather & Renewables")

filters = get_sidebar_filters(show_date_range=True, show_city=True)
start, end = filters["start_date"], filters["end_date"]
city = filters["city"]

city_clause = "" if city == "All" else f"AND w.city = '{city}'"

# ── Weather vs Demand ─────────────────────────────────────────────────────────
st.subheader("Temperature vs. Demand")

weather_demand = run_query(f"""
    SELECT
        w.datetime_hour,
        AVG(w.temperature_c) AS avg_temp,
        AVG(r.metric_value)  AS avg_demand
    FROM staging.stg_weather_texas_hourly w
    JOIN staging.stg_ercot_region_hourly r ON w.datetime_hour = r.datetime_hour
    WHERE r.metric_name = 'Demand'
      AND w.datetime_hour BETWEEN '{start}' AND '{end}'
      {city_clause}
    GROUP BY w.datetime_hour
    ORDER BY w.datetime_hour;
""")

weather_demand["temp_bin"] = weather_demand["avg_temp"].round()
temp_demand = (
    weather_demand.groupby("temp_bin")["avg_demand"].mean().reset_index()
)

col1, col2 = st.columns(2)
with col1:
    st.caption("Average Demand by Temperature Bin")
    line_chart(
        temp_demand, "temp_bin", "avg_demand",
        "Avg Demand by Temperature",
        "Temperature (°C)", "Avg Demand (MWh)"
    )
with col2:
    st.caption("Scatter: Temperature vs. Demand")
    scatter_chart(
        weather_demand, "avg_temp", "avg_demand",
        "Temperature vs. Demand",
        "Temperature (°C)", "Demand (MWh)"
    )

st.divider()

# ── Weather vs Price ──────────────────────────────────────────────────────────
st.subheader("Temperature vs. DAM Price")

weather_price = run_query(f"""
    SELECT
        w.datetime_hour,
        AVG(w.temperature_c)             AS avg_temp,
        AVG(p.settlement_point_price)    AS avg_price
    FROM staging.stg_weather_texas_hourly w
    JOIN staging.stg_ercot_dam_prices p ON w.datetime_hour = p.datetime_hour
    WHERE w.datetime_hour BETWEEN '{start}' AND '{end}'
      {city_clause}
    GROUP BY w.datetime_hour
    ORDER BY w.datetime_hour;
""")

weather_price["temp_bin"] = weather_price["avg_temp"].round()
temp_price = (
    weather_price.groupby("temp_bin")["avg_price"].median().reset_index()
)

col3, col4 = st.columns(2)
with col3:
    st.caption("Median DAM Price by Temperature Bin")
    line_chart(
        temp_price, "temp_bin", "avg_price",
        "Median DAM Price by Temperature",
        "Temperature (°C)", "Median Price ($/MWh)"
    )
with col4:
    st.caption("Scatter: Temperature vs. Price")
    scatter_chart(
        weather_price, "avg_temp", "avg_price",
        "Temperature vs. DAM Price",
        "Temperature (°C)", "Avg Price ($/MWh)"
    )

st.divider()

# ── Solar & Wind resource ─────────────────────────────────────────────────────
st.subheader("Solar & Wind Resource")

solar = run_query(f"""
    SELECT DATE(datetime_hour) AS dt, AVG(ghi) AS avg_ghi
    FROM staging.stg_nrel_solar_resource
    WHERE datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY dt ORDER BY dt;
""")

wind = run_query(f"""
    SELECT DATE(datetime_hour) AS dt, AVG(wind_speed) AS avg_wind
    FROM staging.stg_nrel_wind_resource
    WHERE datetime_hour BETWEEN '{start}' AND '{end}'
    GROUP BY dt ORDER BY dt;
""")

col5, col6 = st.columns(2)
with col5:
    st.caption("Avg Daily Solar Irradiance (GHI)")
    if not solar.empty:
        solar["dt"] = solar["dt"].astype(str)
        st.line_chart(solar.set_index("dt")["avg_ghi"])
    else:
        st.info("No solar data for this range.")

with col6:
    st.caption("Avg Daily Wind Speed")
    if not wind.empty:
        wind["dt"] = wind["dt"].astype(str)
        st.line_chart(wind.set_index("dt")["avg_wind"])
    else:
        st.info("No wind data for this range.")

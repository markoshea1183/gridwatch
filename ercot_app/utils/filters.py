from datetime import date
import streamlit as st


def get_sidebar_filters(
    show_date_range: bool = True,
    show_zone: bool = False,
    show_city: bool = False,
) -> dict:
    """
    Render sidebar filters and return selections as a dict.
    Only renders the filters requested by the calling page.
    """
    filters = {}

    if show_date_range:
        st.sidebar.subheader("Date Range")
        filters["start_date"] = st.sidebar.date_input(
            "Start date", value=date(2024, 1, 1)
        )
        filters["end_date"] = st.sidebar.date_input(
            "End date", value=date(2024, 12, 31)
        )

    if show_zone:
        st.sidebar.subheader("Settlement Zone")
        filters["zone"] = st.sidebar.selectbox(
            "Zone",
            ["All", "HB_HOUSTON", "HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_BUSAVG", "HB_HUBAVG"],
        )

    if show_city:
        st.sidebar.subheader("City")
        filters["city"] = st.sidebar.selectbox(
            "City",
            ["All", "Dallas", "Houston", "San Antonio", "Austin", "Lubbock"],
        )

    return filters

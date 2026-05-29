import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+pymysql://root:Toronto123@34.171.67.51:3306/",
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"connect_timeout": 10},
    )


@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    return pd.read_sql(query, get_engine())

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """
    Loads processed data from CSV files.
    """
    try:
        app_kpis = pd.read_csv("../data/processed/app_level_kpis.csv")
        daily_metrics = pd.read_csv("../data/processed/daily_metrics.csv")

        # Ensure date format
        daily_metrics["date"] = pd.to_datetime(daily_metrics["date"])

        return app_kpis, daily_metrics
    except FileNotFoundError:
        st.error("Data files not found. Please run the data pipeline first.")
        return None, None

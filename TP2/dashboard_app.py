import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(layout="wide", page_title="Play Store Analytics")

st.title("📊 Google Play Store Analytics")
st.markdown("Data powered by **dbt** & **DuckDB**")


# --- DATABASE CONNECTION ---
@st.cache_resource
def get_connection():
    # Connect to the DuckDB database file created by dbt
    conn = duckdb.connect("dbt_playstore/playstore.duckdb", read_only=True)
    return conn


conn = get_connection()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

# Get available categories from Dimension table
categories = conn.execute(
    "SELECT DISTINCT genre FROM dim_apps WHERE genre IS NOT NULL ORDER BY genre"
).df()
selected_genre = st.sidebar.selectbox(
    "Select Category", ["All"] + categories["genre"].tolist()
)

# --- MAIN KPI METRICS ---
col1, col2, col3 = st.columns(3)

# Total Reviews
total_reviews_query = "SELECT COUNT(*) FROM fct_reviews"
if selected_genre != "All":
    total_reviews_query += f" WHERE app_id IN (SELECT app_id FROM dim_apps WHERE genre = '{selected_genre}')"

total_reviews = conn.execute(total_reviews_query).fetchone()[0]
col1.metric("Total Reviews", f"{total_reviews:,}")

# Average Rating
avg_rating_query = "SELECT AVG(rating) FROM fct_reviews"
if selected_genre != "All":
    avg_rating_query += f" WHERE app_id IN (SELECT app_id FROM dim_apps WHERE genre = '{selected_genre}')"

avg_rating = conn.execute(avg_rating_query).fetchone()[0]
col2.metric("Average Rating", f"{avg_rating:.2f} ⭐")

# --- CHARTS ---

# 1. Ratings Distribution
st.subheader("Ratings Distribution")
hist_query = """
    SELECT 
        rating, 
        COUNT(*) as count 
    FROM fct_reviews 
    GROUP BY rating 
    ORDER BY rating
"""
df_hist = conn.execute(hist_query).df()
st.bar_chart(df_hist.set_index("rating"))

# 2. Daily Reviews Evolution (Time Dimension usage)
st.subheader("Reviews Evolution (2023)")
time_query = """
    SELECT 
        d.date_day,
        COUNT(r.review_id) as daily_reviews
    FROM fct_reviews r
    JOIN dim_dates d ON r.date_day = d.date_day
    WHERE d.year = 2026 -- Adjust based on your data range
    GROUP BY d.date_day
    ORDER BY d.date_day
"""
df_time = conn.execute(time_query).df()
st.line_chart(df_time.set_index("date_day"))

# 3. Top Apps Table
st.subheader("Top Used Apps")
top_apps_query = """
    SELECT 
        da.app_name, 
        da.genre,
        AVG(fr.rating) as avg_score,
        COUNT(fr.review_id) as review_count
    FROM fct_reviews fr
    JOIN dim_apps da ON fr.app_id = da.app_id
    GROUP BY da.app_name, da.genre
    ORDER BY review_count DESC
    LIMIT 10
"""
df_top = conn.execute(top_apps_query).df()
st.dataframe(df_top)

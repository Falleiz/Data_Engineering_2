import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(layout="wide", page_title="Play Store Analytics")

st.title("📊 Google Play Store Analytics (Snowflake Schema)")
st.markdown("Data powered by **dbt** & **DuckDB**")


# --- DATABASE CONNECTION ---
@st.cache_resource
def get_connection():
    # Connect to the DuckDB database file created by dbt
    try:
        conn = duckdb.connect("dbt_playstore/playstore.duckdb", read_only=True)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None


conn = get_connection()

if conn:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")

    # Get available categories from dim_categories
    try:
        categories = conn.execute(
            "SELECT DISTINCT category_name FROM dim_categories ORDER BY category_name"
        ).df()
        selected_genre = st.sidebar.selectbox(
            "Select Category", ["All"] + categories["category_name"].tolist()
        )
    except:
        st.warning(
            "Could not load categories. Have you run 'dbt run' with the new schema?"
        )
        selected_genre = "All"

    # --- MAIN KPI METRICS ---
    col1, col2, col3 = st.columns(3)

    # Base Query Parts
    base_query = """
        FROM fact_reviews f
        JOIN dim_apps a ON f.app_key = a.app_key
        JOIN dim_categories c ON a.category_key = c.category_key
    """
    where_clause = ""
    if selected_genre != "All":
        where_clause = f" WHERE c.category_name = '{selected_genre}'"

    # Total Reviews
    total_reviews = conn.execute(
        f"SELECT COUNT(*) {base_query} {where_clause}"
    ).fetchone()[0]
    col1.metric("Total Reviews", f"{total_reviews:,}")

    # Average Rating
    avg_rating = conn.execute(
        f"SELECT AVG(f.rating) {base_query} {where_clause}"
    ).fetchone()[0]
    if avg_rating:
        col2.metric("Average Rating", f"{avg_rating:.2f} ⭐")
    else:
        col2.metric("Average Rating", "N/A")

    # --- CHARTS ---

    # 1. Ratings Distribution
    st.subheader("Ratings Distribution")
    hist_query = f"""
        SELECT 
            f.rating, 
            COUNT(*) as count 
        {base_query}
        {where_clause}
        GROUP BY f.rating 
        ORDER BY f.rating
    """
    df_hist = conn.execute(hist_query).df()
    st.bar_chart(df_hist.set_index("rating"))

    # 2. Daily Reviews Evolution (Time Dimension usage)
    st.subheader("Reviews Evolution")
    time_query = f"""
        SELECT 
            d.date,
            COUNT(f.review_id) as daily_reviews
        {base_query}
        JOIN dim_date d ON f.date_key = d.date_key
        {where_clause}
        GROUP BY d.date
        ORDER BY d.date
    """
    df_time = conn.execute(time_query).df()
    st.line_chart(df_time.set_index("date"))

    # 3. Top Apps Table
    st.subheader("Top Used Apps")
    top_apps_query = f"""
        SELECT 
            a.app_name, 
            c.category_name as genre,
            AVG(f.rating) as avg_score,
            COUNT(f.review_id) as review_count
        {base_query}
        {where_clause}
        GROUP BY a.app_name, c.category_name
        ORDER BY review_count DESC
        LIMIT 10
    """
    df_top = conn.execute(top_apps_query).df()
    st.dataframe(df_top)

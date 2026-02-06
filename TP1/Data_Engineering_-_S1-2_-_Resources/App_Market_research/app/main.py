import streamlit as st
from utils import load_data
from charts import plot_best_worst_apps, plot_rating_trend, plot_volume_distribution

# Page Config
st.set_page_config(page_title="App Market Analysis", page_icon="📱", layout="wide")

st.title("📊 AI Note-Taking Apps Market Analysis")
st.markdown(
    "Analysis of the AI Note-Taking apps market based on Google Play Store reviews."
)

# Load Data
app_kpis, daily_metrics = load_data()

if app_kpis is not None and daily_metrics is not None:

    # --- Summary Metrics (Restored as requested) ---
    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters")
    all_apps = sorted(app_kpis["app_name"].unique())
    selected_apps = st.sidebar.multiselect("Select Competitors", all_apps, default=None)

    # Filter logic
    if selected_apps:
        filtered_kpis = app_kpis[app_kpis["app_name"].isin(selected_apps)]
        st.sidebar.success(f"Showing {len(filtered_kpis)} apps")
    else:
        filtered_kpis = app_kpis  # Show all if selection is empty
    # -----------------------

    # --- Summary Metrics (Restored as requested) ---
    st.subheader("Overview")

    # Custom CSS for the overview box
    st.markdown(
        """
    <style>
    .metric-box {
        background-color: #F0F8FF; /* AliceBlue */
        border: 1px solid #4682B4; /* SteelBlue */
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Apps Tracked", len(filtered_kpis))
        col2.metric("Total Reviews Analyzed", f"{filtered_kpis['num_reviews'].sum():,}")
        col3.metric(
            "Global Avg Rating", f"{filtered_kpis['avg_rating'].mean():.2f} / 5.0"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    # -----------------------------------------------

    # Question 1
    st.header("1. Which applications appear to perform best or worst?")
    st.markdown("*Based on average user ratings (min. 10 reviews).*")
    st.plotly_chart(plot_best_worst_apps(filtered_kpis), use_container_width=True)
    st.divider()

    # Question 2
    st.header("2. Are user ratings improving or declining over time?")
    st.plotly_chart(plot_rating_trend(daily_metrics), use_container_width=True)
    st.divider()

    # Question 3
    st.header("3. Are there noticeable differences in review volume?")
    st.plotly_chart(plot_volume_distribution(filtered_kpis), use_container_width=True)
    st.divider()

    # --- Raw Data Table (Restored as requested) ---
    with st.expander("🔍 Inspect Raw Data (App KPIs)"):
        st.dataframe(app_kpis)
    # ----------------------------------------------

else:
    st.error(
        "Please run the data pipeline to generate the necessary CSV files (data/processed)."
    )

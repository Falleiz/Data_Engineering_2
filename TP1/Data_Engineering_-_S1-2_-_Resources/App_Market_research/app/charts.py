import plotly.express as px
import pandas as pd


def plot_best_worst_apps(df):
    """
    Q1: Which applications appear to perform best or worst?
    Shows Top 5 highest rated and Top 5 lowest rated apps (min 10 reviews).
    """
    # Filter for significant apps (e.g. > 10 reviews) to avoid noise
    significant_apps = df[df["num_reviews"] > 10].copy()

    top_5 = significant_apps.sort_values("avg_rating", ascending=False).head(5)
    bottom_5 = significant_apps.sort_values("avg_rating", ascending=True).head(5)

    # Combine
    combined = pd.concat([top_5, bottom_5])
    combined["Category"] = ["Best Performing"] * len(top_5) + [
        "Worst Performing"
    ] * len(bottom_5)

    fig = px.bar(
        combined,
        x="avg_rating",
        y="app_name",
        orientation="h",
        color="Category",
        title="Best vs Worst Performing Apps (Avg Rating)",
        labels={"avg_rating": "Average Rating", "app_name": "Application"},
        color_discrete_map={"Best Performing": "green", "Worst Performing": "red"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def plot_rating_trend(df):
    """
    Q2: Are user ratings improving or declining over time?
    Line chart of daily average rating.
    """
    fig = px.line(
        df,
        x="date",
        y="daily_avg_rating",
        title="Evolution of User Ratings Over Time",
        labels={"date": "Date", "daily_avg_rating": "Daily Average Rating"},
        color_discrete_sequence=["purple"],
    )
    # Add trendline if possible, simple moving average
    df["SMA_30"] = df["daily_avg_rating"].rolling(window=30).mean()
    fig.add_scatter(
        x=df["date"],
        y=df["SMA_30"],
        mode="lines",
        name="30-Day Trend",
        line=dict(color="orange", dash="dash"),
    )

    return fig


def plot_volume_distribution(df):
    """
    Q3: Are there noticeable differences in review volume between applications?
    Bar chart showing volume distribution.
    """
    df_sorted = df.sort_values("num_reviews", ascending=False).head(
        20
    )  # Top 20 to show contrast

    fig = px.bar(
        df_sorted,
        x="num_reviews",
        y="app_name",
        title="Review Volume Distribution (Top 20 Apps)",
        labels={"num_reviews": "Number of Reviews", "app_name": "Application"},
        color="num_reviews",
        color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig

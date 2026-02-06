import pandas as pd


def main():
    print("Creating Serving Layer...")

    # Load data
    try:
        reviews_df = pd.read_csv("../data/processed/apps_reviews.csv")
        reviews_df["at"] = pd.to_datetime(reviews_df["at"])
    except FileNotFoundError:
        print("Error: apps_reviews.csv not found.")
        return

    # 1. App-Level KPIs
    # Metrics: count, avg rating
    app_stats = (
        reviews_df.groupby("app_id")
        .agg({"reviewId": "count", "score": "mean", "at": ["min", "max"]})
        .reset_index()
    )

    app_stats.columns = [
        "app_id",
        "num_reviews",
        "avg_rating",
        "first_review_date",
        "last_review_date",
    ]
    app_stats["avg_rating"] = app_stats["avg_rating"].round(2)

    # Calculate pct_low_rating (score <= 2)
    low_ratings = (
        reviews_df[reviews_df["score"] <= 2]
        .groupby("app_id")
        .size()
        .reset_index(name="low_rating_count")
    )
    app_stats = app_stats.merge(low_ratings, on="app_id", how="left")
    app_stats["low_rating_count"] = app_stats["low_rating_count"].fillna(0)
    app_stats["pct_low_rating"] = (
        (app_stats["low_rating_count"] / app_stats["num_reviews"]) * 100
    ).round(2)
    app_stats.drop("low_rating_count", axis=1, inplace=True)

    # Add app names
    app_names = reviews_df[["app_id", "app_name"]].drop_duplicates()
    app_stats = app_stats.merge(app_names, on="app_id", how="left")

    # Reorder and sort
    cols = [
        "app_id",
        "app_name",
        "num_reviews",
        "avg_rating",
        "pct_low_rating",
        "first_review_date",
        "last_review_date",
    ]
    app_stats = app_stats[cols].sort_values("num_reviews", ascending=False)

    app_stats.to_csv("../data/processed/app_level_kpis.csv", index=False)
    print(f"Saved app_level_kpis.csv ({len(app_stats)} apps)")

    # 2. Daily Metrics
    reviews_df["date"] = reviews_df["at"].dt.date
    daily_metrics = (
        reviews_df.groupby("date")
        .agg({"reviewId": "count", "score": "mean"})
        .reset_index()
    )

    daily_metrics.columns = ["date", "daily_reviews", "daily_avg_rating"]
    daily_metrics["daily_avg_rating"] = daily_metrics["daily_avg_rating"].round(2)
    daily_metrics.sort_values("date", inplace=True)

    daily_metrics.to_csv("../data/processed/daily_metrics.csv", index=False)
    print(f"Saved daily_metrics.csv ({len(daily_metrics)} days)")


if __name__ == "__main__":
    main()

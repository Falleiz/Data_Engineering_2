import json
import pandas as pd


def clean_installs(val):
    if pd.isna(val):
        return None
    return (
        int(str(val).replace(",", "").replace("+", ""))
        if str(val).replace(",", "").replace("+", "").isdigit()
        else None
    )


def main():
    print("Transforming data...")

    # 1. Apps Metadata
    try:
        with open("../data/raw/apps_metadata.json", "r", encoding="utf-8") as f:
            apps_raw = json.load(f)
    except FileNotFoundError:
        print("Metadata file not found.")
        return

    apps_clean = []
    for app in apps_raw:
        apps_clean.append(
            {
                "appId": app.get("appId"),
                "title": app.get("title"),
                "developer": app.get("developer"),
                "score": (
                    round(float(app.get("score")), 2) if app.get("score") else None
                ),
                "ratings": app.get("ratings"),
                "installs": clean_installs(app.get("installs")),
                "genre": app.get("genre"),
                "price": float(app.get("price")) if app.get("price") else 0.0,
            }
        )

    apps_df = pd.DataFrame(apps_clean)
    apps_df.to_csv("../data/processed/apps_catalog.csv", index=False)
    print(f"Saved apps_catalog.csv ({len(apps_df)} apps)")

    # 2. Reviews
    try:
        data = []
        with open("../data/raw/apps_reviews.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
    except FileNotFoundError:
        print("Reviews file not found.")
        return

    reviews_clean = []
    for r in data:
        reviews_clean.append(
            {
                "app_id": r.get("appId"),
                "app_name": r.get("app_title"),
                "reviewId": r.get("reviewId"),
                "userName": r.get("userName"),
                "score": r.get("score"),
                "content": r.get("content"),
                "thumbsUpCount": r.get("thumbsUpCount"),
                "at": r.get("at"),
            }
        )

    reviews_df = pd.DataFrame(reviews_clean)
    reviews_df["at"] = pd.to_datetime(reviews_df["at"])

    reviews_df.to_csv("../data/processed/apps_reviews.csv", index=False)
    print(f"Saved apps_reviews.csv ({len(reviews_df)} reviews)")


if __name__ == "__main__":
    main()

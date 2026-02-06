import json
import pandas as pd


def main():
    print("Inspecting data files...")

    # Apps Metadata
    try:
        with open("../data/raw/apps_metadata.json", "r", encoding="utf-8") as f:
            apps = json.load(f)
        print(f"\nMetadata: {len(apps)} apps loaded.")

        # Quick check of key fields
        df = pd.DataFrame(apps)
        print(f"Columns: {list(df.columns)}")
        print(f"Missing scores: {df['score'].isna().sum()}")

    except FileNotFoundError:
        print("apps_metadata.json not found.")

    # Reviews
    try:
        reviews = []
        with open("../data/raw/apps_reviews.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                reviews.append(json.loads(line))

        print(f"\nReviews: {len(reviews)} loaded.")
        if reviews:
            print(f"Sample review keys: {list(reviews[0].keys())}")

    except FileNotFoundError:
        print("apps_reviews.jsonl not found.")


if __name__ == "__main__":
    main()

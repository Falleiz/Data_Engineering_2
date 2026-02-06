import json
import time
from datetime import datetime
from google_play_scraper import reviews, Sort

# Configuration
LANG = "en"
COUNTRY = "us"
MAX_REVIEWS_PER_APP = 500
INPUT_FILE = "../data/raw/apps_metadata.json"
OUTPUT_FILE = "../data/raw/apps_reviews.jsonl"
STATS_FILE = "../data/raw/reviews_extraction_stats.json"


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            apps_metadata = json.load(f)
    except FileNotFoundError:
        print(f"Error: Not found {INPUT_FILE}")
        return

    output_file = open(OUTPUT_FILE, "w", encoding="utf-8")
    total_reviews = 0
    reviews_stats = []

    for i, app_data in enumerate(apps_metadata, 1):
        app_id = app_data["appId"]
        app_title = app_data.get("title", "N/A")
        print(f"[{i}/{len(apps_metadata)}] {app_title} ({app_id})")

        try:
            reviews_collected = 0
            continuation_token = None

            # Pagination loop
            while reviews_collected < MAX_REVIEWS_PER_APP:
                count_to_fetch = min(100, MAX_REVIEWS_PER_APP - reviews_collected)

                result, continuation_token = reviews(
                    app_id,
                    lang=LANG,
                    country=COUNTRY,
                    count=count_to_fetch,
                    sort=Sort.NEWEST,
                    continuation_token=continuation_token,
                )

                if not result:
                    break

                for review in result:
                    review["appId"] = app_id
                    review["app_title"] = app_title
                    review["extraction_date"] = datetime.now().isoformat()

                    # Convert datetimes
                    if "at" in review and hasattr(review["at"], "isoformat"):
                        review["at"] = review["at"].isoformat()
                    if (
                        "repliedAt" in review
                        and review["repliedAt"]
                        and hasattr(review["repliedAt"], "isoformat")
                    ):
                        review["repliedAt"] = review["repliedAt"].isoformat()

                    output_file.write(json.dumps(review, ensure_ascii=False) + "\n")
                    reviews_collected += 1
                    total_reviews += 1

                if not continuation_token:
                    break
                time.sleep(0.5)

            stats = {
                "appId": app_id,
                "app_title": app_title,
                "reviews_count": reviews_collected,
                "has_more": continuation_token is not None,
            }
            reviews_stats.append(stats)
            print(f"  - Extracted {reviews_collected} reviews")

        except Exception as e:
            print(f"  - Error: {str(e)}")
            reviews_stats.append({"appId": app_id, "error": str(e)})

        if i < len(apps_metadata):
            time.sleep(1)

    output_file.close()

    # Save stats
    stats_summary = {
        "extraction_date": datetime.now().isoformat(),
        "total_apps": len(apps_metadata),
        "total_reviews": total_reviews,
        "reviews_per_app": reviews_stats,
    }

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats_summary, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Saved to {OUTPUT_FILE}")
    print(f"Total reviews: {total_reviews}")


if __name__ == "__main__":
    main()

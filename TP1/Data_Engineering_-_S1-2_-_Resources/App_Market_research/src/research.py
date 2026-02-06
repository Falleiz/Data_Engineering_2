from google_play_scraper import search
import json

# Configuration
LANG = "en"
COUNTRY = "us"
OUTPUT_FILE = "../data/raw/apps_found.json"

SEARCH_QUERIES = [
    "AI note taking",
    "AI notes",
    "smart notes AI",
    "voice notes AI",
]


def main():
    all_app_ids = set()
    all_apps = []

    print("Searching for apps...")

    for query in SEARCH_QUERIES:
        print(f"Query: '{query}'")
        try:
            results = search(query, lang=LANG, country=COUNTRY, n_hits=30)

            for result in results:
                app_id = result.get("appId")
                if app_id and app_id not in all_app_ids:
                    all_app_ids.add(app_id)
                    all_apps.append(
                        {
                            "appId": app_id,
                            "title": result.get("title"),
                            "developer": result.get("developer"),
                            "score": result.get("score"),
                            "found_with_query": query,
                        }
                    )
        except Exception as e:
            print(f"  Error: {str(e)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_apps, f, ensure_ascii=False, indent=2)

    print(f"\nFound {len(all_apps)} unique apps. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

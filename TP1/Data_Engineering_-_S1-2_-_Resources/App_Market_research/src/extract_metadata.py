import json
import time
from datetime import datetime
from google_play_scraper import app

# Configuration
LANG = "en"
COUNTRY = "us"
INPUT_FILE = "../data/raw/apps_found.json"
OUTPUT_FILE = "../data/raw/apps_metadata.json"
ERRORS_FILE = "../data/raw/apps_metadata_errors.json"


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            apps_found = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
        return

    apps_metadata = []
    apps_errors = []

    print(f"Extracting metadata for {len(apps_found)} apps...")

    for i, app_info in enumerate(apps_found, 1):
        app_id = app_info["appId"]
        print(f"[{i}/{len(apps_found)}] {app_info.get('title', 'N/A')}")

        try:
            app_data = app(app_id, lang=LANG, country=COUNTRY)

            app_data["extraction_date"] = datetime.now().isoformat()
            app_data["extraction_source"] = "google_play_scraper"
            apps_metadata.append(app_data)

        except Exception as e:
            print(f"  Error: {str(e)}")
            apps_errors.append(
                {
                    "appId": app_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        if i < len(apps_found):
            time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(apps_metadata, f, ensure_ascii=False, indent=2)

    if apps_errors:
        with open(ERRORS_FILE, "w", encoding="utf-8") as f:
            json.dump(apps_errors, f, ensure_ascii=False, indent=2)

    print(f"\nSaved metadata to {OUTPUT_FILE}")
    print(f"Success: {len(apps_metadata)}, Errors: {len(apps_errors)}")


if __name__ == "__main__":
    main()

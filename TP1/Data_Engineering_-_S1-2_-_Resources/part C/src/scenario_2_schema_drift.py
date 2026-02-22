"""
Scenario 2 — Schema Drift in Reviews
======================================
Run the pipeline with `note_taking_ai_reviews_schema_drift.csv`.

Schema changes vs original:
  Original col   →  Drifted col
  app_id         →  appId
  app_name       →  appTitle
  reviewId       →  review_id
  userName       →  username
  score          →  rating
  content        →  review_text
  thumbsUpCount  →  likes
  at             →  review_time  (also different date format: YYYY/MM/DD HH:MM)

Observations documented at the bottom of this script.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    DATA_DIR,
    OUT_DIR,
    clean_reviews_df,
    clean_apps_df,
    normalize_reviews_columns,
    filter_unknown_apps,
    build_serving_layer,
    log_issues,
)

APPS_CATALOG = Path("../../App_Market_research/data/processed/apps_catalog.csv")
REVIEWS_FILE = DATA_DIR / "note_taking_ai_reviews_schema_drift.csv"
OUT_REVIEWS = OUT_DIR / "s2_reviews.csv"
OUT_KPIS = OUT_DIR / "s2_app_kpis.csv"
OUT_DAILY = OUT_DIR / "s2_daily_metrics.csv"


def run():
    print("\n>>> SCENARIO 2: Schema Drift\n")

    apps_df = pd.read_csv(APPS_CATALOG)
    apps_df = clean_apps_df(apps_df)

    # Load with drifted schema — raw column names kept intentionally
    reviews_df = pd.read_csv(REVIEWS_FILE, dtype=str)
    print(f"  [schema] Columns received: {reviews_df.columns.tolist()}")

    # Step 1: Remap drifted columns to standard names
    # This is the ONLY required code change for schema drift.
    # All downstream logic remains untouched.
    reviews_df = normalize_reviews_columns(reviews_df)
    print(f"  [schema] Columns after normalization: {reviews_df.columns.tolist()}")

    # Step 2: Filter unknown apps
    reviews_df = filter_unknown_apps(reviews_df, apps_df)

    # Step 3: Clean — clean_timestamp handles YYYY/MM/DD HH:MM format automatically
    reviews_df = clean_reviews_df(reviews_df)

    reviews_df.to_csv(OUT_REVIEWS, index=False)
    app_kpis, daily = build_serving_layer(reviews_df, apps_df)
    app_kpis.to_csv(OUT_KPIS, index=False)
    daily.to_csv(OUT_DAILY, index=False)

    log_issues("Scenario 2 — Schema Drift", reviews_df, apps_df)
    print(f"  Output: {OUT_REVIEWS}")

    # -----------------------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------------------
    print(
        """
OBSERVATIONS:
  Q: Which parts of the pipeline relied on hard-coded column names?
     → The original transform_data.py used hard-coded keys like r.get('reviewId'),
       r.get('score'), etc. Each of them would silently return None without error
       when the column is renamed, producing a DataFrame full of nulls.

  Q: Does the pipeline fail explicitly or produce incorrect results silently?
     → SILENT FAILURE in the original code — all columns would be None.
       With normalize_reviews_columns(), the drift is caught and remapped
       at a single, explicit entry point before any downstream logic runs.

  Q: How localized are the required code changes?
     → With the normalize_reviews_columns() utility: 1 line of code in this
       script. Without it: every r.get() call in transform_data.py would need
       to be updated — a widespread, error-prone change.
"""
    )


if __name__ == "__main__":
    run()

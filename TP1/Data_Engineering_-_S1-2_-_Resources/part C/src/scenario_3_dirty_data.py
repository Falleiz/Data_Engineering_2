"""
Scenario 3 — Dirty and Inconsistent Data Records
==================================================
Run the pipeline with `note_taking_ai_reviews_dirty.csv`.

Issues this file contains:
  r_2101 — score = "five"       (string instead of int)
  r_2102 — score = -1           (out of valid range [0, 5])
  r_2103 — at = "not_a_date"    (unparseable timestamp)
  r_2104 — content = "NULL"     (literal string "NULL")
  r_2104 — thumbsUpCount = NULL (missing numeric field)
  r_2105 — score = ""           (empty string)
  r_2107 — thumbsUpCount = ""   (empty string)

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
    filter_unknown_apps,
    build_serving_layer,
    log_issues,
)

APPS_CATALOG = Path("../../App_Market_research/data/processed/apps_catalog.csv")
REVIEWS_FILE = DATA_DIR / "note_taking_ai_reviews_dirty.csv"
OUT_REVIEWS = OUT_DIR / "s3_reviews.csv"
OUT_KPIS = OUT_DIR / "s3_app_kpis.csv"
OUT_DAILY = OUT_DIR / "s3_daily_metrics.csv"


def run():
    print("\n>>> SCENARIO 3: Dirty and Inconsistent Data\n")

    apps_df = pd.read_csv(APPS_CATALOG)
    apps_df = clean_apps_df(apps_df)

    # Load all columns as strings to prevent pandas from silently coercing
    # 'five' to NaN before we can log it properly
    reviews_df = pd.read_csv(REVIEWS_FILE, dtype=str)

    # Log raw dirty values before cleaning
    print("  [pre-clean] Raw score values:", reviews_df["score"].tolist())
    print("  [pre-clean] Raw timestamp values:", reviews_df["at"].tolist())

    # Filter unknown apps
    reviews_df = filter_unknown_apps(reviews_df, apps_df)

    # Apply cleaning — invalid scores and timestamps become None/NaT
    reviews_df = clean_reviews_df(reviews_df)

    # Show what survived
    print(
        f"\n  [post-clean] Valid scores: {reviews_df['score'].notna().sum()}/{len(reviews_df)}"
    )
    print(
        f"  [post-clean] Valid timestamps: {reviews_df['at'].notna().sum()}/{len(reviews_df)}"
    )
    print(
        f"  [post-clean] Content 'NULL' → NaN: {'NULL' not in reviews_df['content'].values}"
    )

    reviews_df.to_csv(OUT_REVIEWS, index=False)

    # Serving layer uses only rows with valid score AND timestamp
    app_kpis, daily = build_serving_layer(reviews_df, apps_df)
    app_kpis.to_csv(OUT_KPIS, index=False)
    daily.to_csv(OUT_DAILY, index=False)

    log_issues("Scenario 3 — Dirty Data", reviews_df, apps_df)
    print(f"  Output: {OUT_REVIEWS}")

    # -----------------------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------------------
    print(
        """
OBSERVATIONS:
  Q: How does the pipeline handle invalid ratings or timestamps?
     → clean_score() explicitly validates the range [0, 5] and type.
       Strings like 'five' and values like -1 → None.
       clean_timestamp() returns NaT for 'not_a_date'.

  Q: Are problematic records filtered or propagated?
     → Records with invalid scores or timestamps are kept in the processed
       dataset (with None/NaT) but EXCLUDED from serving layer aggregations
       (build_serving_layer calls dropna(subset=['score', 'at'])).
       This makes the decision explicit and traceable.

  Q: Do data quality issues surface early or affect metrics silently?
     → With the original pipeline (pd.to_datetime without errors='coerce'),
       a single bad timestamp crashes the entire pipeline.
       With our explicit cleaning, errors surface immediately with clear
       per-record logging, and valid records are unaffected.
"""
    )


if __name__ == "__main__":
    run()

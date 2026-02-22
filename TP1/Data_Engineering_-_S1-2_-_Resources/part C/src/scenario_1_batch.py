"""
Scenario 1 — New Reviews Batch
================================
Run the pipeline with `note_taking_ai_reviews_batch2.csv` as the reviews source.

Issues this file contains:
- Duplicate reviewId: r_2002 appears twice (exact duplicate)
- Unknown app: com.ghost.notes is not in the original apps catalog

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
    deduplicate_reviews,
    filter_unknown_apps,
    build_serving_layer,
    log_issues,
)

APPS_CATALOG = Path("../../App_Market_research/data/processed/apps_catalog.csv")
REVIEWS_FILE = DATA_DIR / "note_taking_ai_reviews_batch2.csv"
OUT_REVIEWS = OUT_DIR / "s1_reviews.csv"
OUT_KPIS = OUT_DIR / "s1_app_kpis.csv"
OUT_DAILY = OUT_DIR / "s1_daily_metrics.csv"


def run():
    print("\n>>> SCENARIO 1: New Reviews Batch\n")

    # --- Load apps catalog (original) ---
    apps_df = pd.read_csv(APPS_CATALOG)
    apps_df = clean_apps_df(apps_df)

    # --- Load new reviews batch ---
    reviews_df = pd.read_csv(REVIEWS_FILE, dtype=str)

    # Step 1: Remove exact duplicate reviewIds
    reviews_df = deduplicate_reviews(reviews_df)

    # Step 2: Filter out reviews for apps not in our catalog
    # Observation: com.ghost.notes has reviews but is unknown → dropped
    reviews_df = filter_unknown_apps(reviews_df, apps_df)

    # Step 3: Clean data types
    reviews_df = clean_reviews_df(reviews_df)

    # Step 4: Save processed reviews (full refresh — no state carried over)
    reviews_df.to_csv(OUT_REVIEWS, index=False)

    # Step 5: Build serving layer
    app_kpis, daily = build_serving_layer(reviews_df, apps_df)
    app_kpis.to_csv(OUT_KPIS, index=False)
    daily.to_csv(OUT_DAILY, index=False)

    log_issues("Scenario 1 — New Reviews Batch", reviews_df, apps_df)
    print(f"  Output: {OUT_REVIEWS}")
    print(f"  Output: {OUT_KPIS}")
    print(f"  Output: {OUT_DAILY}")

    # -----------------------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------------------
    print(
        """
OBSERVATIONS:
  Q: How many changes were required to support this new batch?
     → 2 code-level changes: deduplication by reviewId, unknown-app filtering.
       The existing cleaning logic required no changes.

  Q: Is the pipeline performing a full refresh?
     → YES — this is an explicit full refresh. The batch replaces the previous
       reviews dataset; no state from prior runs is assumed or preserved.

  Q: How are duplicate reviews handled?
     → drop_duplicates(subset=['reviewId'], keep='first') — deterministic and explicit.

  Q: What happens to reviews referencing unknown apps?
     → They are filtered out with a logged warning. The pipeline does not crash,
       but the orphaned reviews are not included in downstream aggregations.
"""
    )


if __name__ == "__main__":
    run()

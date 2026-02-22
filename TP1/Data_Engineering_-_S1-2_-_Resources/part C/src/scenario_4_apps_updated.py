"""
Scenario 4 — Updated Applications Metadata
============================================
Run the pipeline with `note_taking_ai_apps_updated.csv` as the apps source.

Issues this file contains:
  - com.otter.ai appears TWICE with different titles/developers (duplicate appId)
  - com.unknown.ai has empty score, ratings, installs, price, genre
  - installs = '500000' (no commas/+) — handled by clean_installs
  - installs = '1,000,000+' — handled by clean_installs
  - price = '' (empty) for one app

Observations documented at the bottom of this script.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    DATA_DIR,
    OUT_DIR,
    clean_apps_df,
    clean_reviews_df,
    deduplicate_apps,
    filter_unknown_apps,
    build_serving_layer,
    log_issues,
)

APPS_FILE = DATA_DIR / "note_taking_ai_apps_updated.csv"
REVIEWS_ORIGINAL = Path("../../App_Market_research/data/processed/apps_reviews.csv")
OUT_APPS = OUT_DIR / "s4_apps_catalog.csv"
OUT_KPIS = OUT_DIR / "s4_app_kpis.csv"
OUT_DAILY = OUT_DIR / "s4_daily_metrics.csv"


def run():
    print("\n>>> SCENARIO 4: Updated Apps Metadata\n")

    # --- Load updated apps catalog ---
    apps_df = pd.read_csv(APPS_FILE, dtype=str)
    print(f"  [apps] Raw shape: {apps_df.shape}")
    print(f"  [apps] Columns: {apps_df.columns.tolist()}")

    # Step 1: Deduplicate by appId (keep first = original entry)
    apps_df = deduplicate_apps(apps_df, id_col="appId")

    # Step 2: Clean numeric fields (score, installs, ratings, price)
    apps_df = clean_apps_df(apps_df)

    print(f"\n  [apps] After dedup + clean:")
    print(
        apps_df[["appId", "title", "score", "installs", "price"]].to_string(index=False)
    )

    apps_df.to_csv(OUT_APPS, index=False)

    # --- Load processed original reviews ---
    if not REVIEWS_ORIGINAL.exists():
        print(f"\n  [skip] Original reviews not found at {REVIEWS_ORIGINAL}")
        print("  Run the original pipeline first to generate apps_reviews.csv")
        return

    reviews_df = pd.read_csv(REVIEWS_ORIGINAL, dtype=str)
    reviews_df = filter_unknown_apps(reviews_df, apps_df)
    reviews_df = clean_reviews_df(reviews_df)

    app_kpis, daily = build_serving_layer(reviews_df, apps_df)
    app_kpis.to_csv(OUT_KPIS, index=False)
    daily.to_csv(OUT_DAILY, index=False)

    log_issues("Scenario 4 — Updated Apps Metadata", reviews_df, apps_df)
    print(f"  Output: {OUT_APPS}")
    print(f"  Output: {OUT_KPIS}")

    # -----------------------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------------------
    print(
        """
OBSERVATIONS:
  Q: How are duplicate application IDs handled?
     → deduplicate_apps() logs every duplicate with its count, then keeps
       the first occurrence. The 'fake' Otter AI entry is dropped explicitly.
       Without this step, a join on appId would produce duplicated rows
       downstream and inflate aggregated metrics.

  Q: What happens during joins between reviews and applications?
     → After dedup, each appId maps to exactly one app row, preserving
       join integrity. Without dedup, a many-to-one join becomes many-to-many.

  Q: Are downstream aggregates affected in ways immediately visible?
     → With dedup: KPIs are computed correctly per unique app.
       Without dedup: avg_rating and num_reviews would be artificially doubled
       for Otter AI. This kind of silent inflation is one of the most dangerous
       data quality issues because the output still "looks right".
"""
    )


if __name__ == "__main__":
    run()

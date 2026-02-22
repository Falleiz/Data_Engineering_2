"""
Stress Test Pipeline — Part C
Lab 1 — Data Engineering

This module provides shared utilities for all 5 stress test scenarios:
- clean_installs: normalize install count strings to integers
- clean_score: safely coerce score to float (1-5), return None if invalid
- clean_timestamp: parse timestamps flexibly, return NaT if unparseable
- normalize_reviews_columns: remap schema-drifted column names to standard names
- deduplicate: drop duplicate rows based on reviewId (keep first)
- log_issues: print a structured summary of data quality findings
"""

import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

APPS_ORIGINAL = Path("../App_Market_research/data/processed/apps_catalog.csv")

# ── Column mapping for schema drift scenario ───────────────────────────────
SCHEMA_DRIFT_MAP = {
    "appId": "app_id",
    "appTitle": "app_name",
    "review_id": "reviewId",
    "username": "userName",
    "rating": "score",
    "review_text": "content",
    "likes": "thumbsUpCount",
    "review_time": "at",
}

STANDARD_REVIEW_COLS = [
    "app_id",
    "app_name",
    "reviewId",
    "userName",
    "score",
    "content",
    "thumbsUpCount",
    "at",
]


# ── Cleaning functions ─────────────────────────────────────────────────────


def clean_installs(val):
    """Normalize install strings like '1,000,000+' or '500000' to int."""
    if pd.isna(val) or str(val).strip() == "":
        return None
    cleaned = str(val).replace(",", "").replace("+", "").strip()
    return int(cleaned) if cleaned.isdigit() else None


def clean_score(val):
    """
    Coerce score to float in range [0, 5].
    Returns None for: strings like 'five', negative values, empty.
    """
    if pd.isna(val) or str(val).strip() == "":
        return None
    try:
        s = float(val)
        return s if 0 <= s <= 5 else None
    except (ValueError, TypeError):
        return None


def clean_timestamp(val, formats=None):
    """
    Parse timestamp flexibly. Returns NaT if unparseable.
    Handles: ISO format, 'YYYY/MM/DD HH:MM', and common variants.
    """
    if pd.isna(val) or str(val).strip() in ("", "not_a_date", "NULL"):
        return pd.NaT
    if formats is None:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]
    for fmt in formats:
        try:
            return pd.to_datetime(str(val), format=fmt)
        except ValueError:
            continue
    return pd.NaT


def normalize_reviews_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap schema-drifted column names to the standard pipeline schema."""
    df = df.rename(columns=SCHEMA_DRIFT_MAP)
    # Ensure all standard columns exist (fill missing ones with None)
    for col in STANDARD_REVIEW_COLS:
        if col not in df.columns:
            df[col] = None
    return df[STANDARD_REVIEW_COLS]


def deduplicate_reviews(df: pd.DataFrame, id_col="reviewId") -> pd.DataFrame:
    """Drop exact duplicate review IDs, keep first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset=[id_col], keep="first")
    after = len(df)
    if before != after:
        print(f"  [dedup] Removed {before - after} duplicate(s) on '{id_col}'")
    return df


def filter_unknown_apps(
    reviews_df: pd.DataFrame, apps_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Filter reviews to only include apps present in the apps catalog.
    Logs orphaned reviews for observability.
    """
    known_ids = set(apps_df["appId"].dropna())
    mask = reviews_df["app_id"].isin(known_ids)
    orphaned = reviews_df[~mask]
    if not orphaned.empty:
        print(f"  [filter] {len(orphaned)} review(s) reference unknown apps:")
        for app_id in orphaned["app_id"].unique():
            print(f"    - {app_id}")
    return reviews_df[mask].reset_index(drop=True)


def deduplicate_apps(apps_df: pd.DataFrame, id_col="appId") -> pd.DataFrame:
    """
    Remove duplicate appIds, keeping the first occurrence.
    Logs which apps were deduplicated.
    """
    before = len(apps_df)
    dups = apps_df[apps_df.duplicated(subset=[id_col], keep=False)]
    if not dups.empty:
        print(f"  [dedup_apps] Duplicate appId(s) found:")
        for aid in dups[id_col].unique():
            print(f"    - {aid} ({len(dups[dups[id_col]==aid])} rows)")
    apps_df = apps_df.drop_duplicates(subset=[id_col], keep="first")
    print(f"  [dedup_apps] Kept {len(apps_df)}/{before} apps after dedup")
    return apps_df


def clean_apps_df(apps_df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning to apps catalog DataFrame."""
    apps_df = apps_df.copy()
    apps_df["score"] = apps_df["score"].apply(clean_score)
    apps_df["installs"] = apps_df["installs"].apply(clean_installs)
    apps_df["price"] = pd.to_numeric(apps_df["price"], errors="coerce").fillna(0.0)
    apps_df["ratings"] = pd.to_numeric(apps_df["ratings"], errors="coerce")
    return apps_df


def clean_reviews_df(reviews_df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning to reviews DataFrame."""
    reviews_df = reviews_df.copy()

    # Replace string "NULL" with real NaN
    reviews_df.replace("NULL", pd.NA, inplace=True)

    reviews_df["score"] = reviews_df["score"].apply(clean_score)
    reviews_df["thumbsUpCount"] = (
        pd.to_numeric(reviews_df["thumbsUpCount"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    reviews_df["at"] = reviews_df["at"].apply(clean_timestamp)

    # Log quality issues
    invalid_scores = reviews_df["score"].isna().sum()
    invalid_dates = reviews_df["at"].isna().sum()
    if invalid_scores:
        print(
            f"  [quality] {invalid_scores} review(s) with invalid/missing score → set to None"
        )
    if invalid_dates:
        print(
            f"  [quality] {invalid_dates} review(s) with unparseable timestamp → set to NaT"
        )

    return reviews_df


def build_serving_layer(reviews_df: pd.DataFrame, apps_df: pd.DataFrame) -> tuple:
    """
    Build app-level KPIs and daily metrics from cleaned DataFrames.
    Returns (app_kpis_df, daily_metrics_df).
    """
    valid = reviews_df.dropna(subset=["score", "at"])

    # App-level KPIs
    app_kpis = (
        valid.groupby("app_id")
        .agg(
            num_reviews=("reviewId", "count"),
            avg_rating=("score", "mean"),
            pct_low_rating=("score", lambda x: round((x <= 2).sum() / len(x) * 100, 2)),
            first_review_date=("at", "min"),
            latest_review_date=("at", "max"),
        )
        .reset_index()
    )
    app_kpis = app_kpis.merge(
        apps_df[["appId", "title"]].rename(columns={"appId": "app_id"}),
        on="app_id",
        how="left",
    )

    # Daily metrics
    valid = valid.copy()
    valid["date"] = pd.to_datetime(valid["at"]).dt.date
    daily = (
        valid.groupby("date")
        .agg(
            daily_reviews=("reviewId", "count"),
            daily_avg_rating=("score", "mean"),
        )
        .reset_index()
    )

    return app_kpis, daily


def log_issues(label: str, reviews_df: pd.DataFrame, apps_df: pd.DataFrame = None):
    """Print a structured quality summary after cleaning."""
    print(f"\n{'='*55}")
    print(f"  SCENARIO: {label}")
    print(f"{'='*55}")
    print(f"  Reviews shape    : {reviews_df.shape}")
    print(f"  Null scores      : {reviews_df['score'].isna().sum()}")
    print(f"  Null timestamps  : {reviews_df['at'].isna().sum()}")
    print(f"  Unique apps      : {reviews_df['app_id'].nunique()}")
    if apps_df is not None:
        print(f"  Apps catalog     : {len(apps_df)} rows")
    print(f"{'='*55}\n")

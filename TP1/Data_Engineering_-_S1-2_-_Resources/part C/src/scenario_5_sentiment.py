"""
Scenario 5 — New Business Logic: Sentiment vs Rating Contradiction
===================================================================
Business request:
  "We want to identify applications where the sentiment expressed in review text
   appears to contradict the numeric rating (e.g., highly negative text paired
   with a high score, or positive text paired with a low score)."

Design Approach:
  We use a simple keyword-based heuristic to label each review as
  'positive', 'negative', or 'neutral' based on word presence.
  We then flag reviews where the text sentiment contradicts the numeric rating.

  A contradiction is defined as:
    - text_sentiment = 'positive' AND score <= 2  (positive text, low score)
    - text_sentiment = 'negative' AND score >= 4  (negative text, high score)

Where in the pipeline does this logic belong?
  → In the SERVING LAYER, not in the transformation layer.
    The raw review content is already preserved in apps_reviews.csv.
    This is purely derived analytical logic that produces a new output.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import DATA_DIR, OUT_DIR, clean_reviews_df, clean_apps_df

APPS_CATALOG = Path("../../App_Market_research/data/processed/apps_catalog.csv")
REVIEWS_ORIGINAL = Path("../../App_Market_research/data/processed/apps_reviews.csv")
OUT_CONTRADICTIONS = OUT_DIR / "s5_sentiment_contradictions.csv"
OUT_SUMMARY = OUT_DIR / "s5_sentiment_summary.csv"

# ── Keyword heuristic ─────────────────────────────────────────────────────
POSITIVE_KEYWORDS = {
    "great",
    "love",
    "excellent",
    "amazing",
    "good",
    "best",
    "fantastic",
    "perfect",
    "awesome",
    "nice",
    "useful",
    "helpful",
    "clean",
    "fast",
    "smooth",
    "easy",
    "reliable",
    "works",
    "quality",
    "recommend",
}
NEGATIVE_KEYWORDS = {
    "terrible",
    "bad",
    "worst",
    "crash",
    "bug",
    "broken",
    "slow",
    "useless",
    "horrible",
    "awful",
    "laggy",
    "unstable",
    "poor",
    "freeze",
    "annoying",
    "disappointed",
    "waste",
    "problem",
    "error",
    "fail",
    "issue",
    "stopped",
    "drain",
    "expensive",
}


def classify_sentiment(text: str) -> str:
    """
    Simple keyword-based classifier.
    Returns 'positive', 'negative', or 'neutral'.
    """
    if not isinstance(text, str) or text.strip() == "":
        return "neutral"
    words = set(text.lower().split())
    pos_hits = len(words & POSITIVE_KEYWORDS)
    neg_hits = len(words & NEGATIVE_KEYWORDS)
    if pos_hits > neg_hits:
        return "positive"
    elif neg_hits > pos_hits:
        return "negative"
    return "neutral"


def is_contradiction(row) -> bool:
    """
    Returns True if sentiment label contradicts numeric score.
    """
    if pd.isna(row["score"]):
        return False
    return (row["text_sentiment"] == "positive" and row["score"] <= 2) or (
        row["text_sentiment"] == "negative" and row["score"] >= 4
    )


def run():
    print("\n>>> SCENARIO 5: Sentiment vs Rating Contradiction\n")

    if not REVIEWS_ORIGINAL.exists():
        print(f"  [skip] Processed reviews not found at {REVIEWS_ORIGINAL}")
        print("  Run the original pipeline first.")
        return

    # --- Load existing processed data (no raw file modification needed) ---
    reviews_df = pd.read_csv(REVIEWS_ORIGINAL, dtype=str)
    reviews_df = clean_reviews_df(reviews_df)

    apps_df = pd.read_csv(APPS_CATALOG)
    apps_df = clean_apps_df(apps_df)

    print(f"  [input] {len(reviews_df)} reviews loaded")

    # --- Step 1: Classify sentiment from text ---
    reviews_df["text_sentiment"] = reviews_df["content"].apply(classify_sentiment)

    # --- Step 2: Flag contradictions ---
    reviews_df["is_contradiction"] = reviews_df.apply(is_contradiction, axis=1)

    # --- Step 3: Extract contradictions ---
    contradictions = reviews_df[reviews_df["is_contradiction"]].copy()
    print(
        f"  [result] {len(contradictions)} contradiction(s) detected "
        f"out of {len(reviews_df)} reviews "
        f"({len(contradictions)/len(reviews_df)*100:.1f}%)"
    )

    # --- Step 4: Summary by app ---
    summary = (
        reviews_df.groupby("app_id")
        .agg(
            total_reviews=("reviewId", "count"),
            contradictions=("is_contradiction", "sum"),
            pct_contradiction=(
                "is_contradiction",
                lambda x: round(x.sum() / len(x) * 100, 1),
            ),
        )
        .reset_index()
        .merge(
            apps_df[["appId", "title"]].rename(columns={"appId": "app_id"}),
            on="app_id",
            how="left",
        )
        .sort_values("pct_contradiction", ascending=False)
    )

    contradictions.to_csv(OUT_CONTRADICTIONS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n  Per-app contradiction summary:")
    print(
        summary[
            ["app_id", "total_reviews", "contradictions", "pct_contradiction"]
        ].to_string(index=False)
    )

    print(f"\n  Output: {OUT_CONTRADICTIONS}")
    print(f"  Output: {OUT_SUMMARY}")

    # -----------------------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------------------
    print(
        """
OBSERVATIONS:
  Q: Where in the pipeline does this logic naturally belong?
     → In the SERVING LAYER. The raw content field already exists in
       apps_reviews.csv. No change to raw data or transformation logic is needed.
       This is a pure analytical derivation, just like pct_low_rating.

  Q: How many parts of the pipeline would need to change?
     → Only one: a new serving-layer script (this file). The transformation
       and ingestion layers remain completely untouched.

  Q: Is this logic easy to reuse or maintain?
     → Moderately. The keyword heuristic is fast and interpretable but brittle
       (sarcasm, negation like 'not great' are not handled). For production,
       a pre-trained sentiment model (e.g. VADER, TextBlob, or a fine-tuned
       classifier) would replace classify_sentiment() with no change to
       the surrounding pipeline structure.

  Q: Does the current structure clearly separate data preparation from analytics?
     → YES — the processed CSV is the stable interface between the two layers.
       Adding new analytical metrics never requires touching transform_data.py.
"""
    )


if __name__ == "__main__":
    run()

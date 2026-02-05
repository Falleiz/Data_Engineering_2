# Script d'inspection des donnees brutes
# Identifie les problemes dans apps_metadata.json et apps_reviews.jsonl

import json
import pandas as pd
from collections import Counter

print("=" * 80)
print("INSPECTION DES DONNEES BRUTES")
print("=" * 80)

# ============================================================================
# 1. INSPECTION DES METADONNEES DES APPLICATIONS
# ============================================================================

print("\n1. APPS METADATA (apps_metadata.json)")
print("-" * 80)

with open('../data/raw/apps_metadata.json', 'r', encoding='utf-8') as f:
    apps_data = json.load(f)

print(f"Nombre d'apps: {len(apps_data)}")
print(f"\nChamps disponibles dans la premiere app:")
for key in sorted(apps_data[0].keys()):
    print(f"  - {key}")

# Analyser les champs cles
print("\n--- Analyse des champs cles ---")

# appId
print(f"\nappId:")
print(f"  Total: {len(apps_data)}")
print(f"  Uniques: {len(set(app['appId'] for app in apps_data))}")
print(f"  Doublons: {len(apps_data) - len(set(app['appId'] for app in apps_data))}")

# score
scores = [app.get('score') for app in apps_data]
print(f"\nScore:")
print(f"  Valeurs manquantes: {scores.count(None)}")
print(f"  Min: {min([s for s in scores if s is not None]):.2f}")
print(f"  Max: {max([s for s in scores if s is not None]):.2f}")
print(f"  Type: {type(scores[0])}")

# ratings
ratings = [app.get('ratings') for app in apps_data]
print(f"\nRatings:")
print(f"  Valeurs manquantes: {ratings.count(None)}")
print(f"  Type: {type(ratings[0]) if ratings[0] else 'None'}")

# installs
installs = [app.get('installs') for app in apps_data]
print(f"\nInstalls:")
print(f"  Valeurs manquantes: {installs.count(None)}")
print(f"  Exemples de valeurs: {list(set(installs))[:5]}")
print(f"  Type: {type(installs[0]) if installs[0] else 'None'}")
print(f"  PROBLEME: Format texte avec virgules et '+' (ex: '1,000,000+')")

# price
prices = [app.get('price') for app in apps_data]
print(f"\nPrice:")
print(f"  Valeurs manquantes: {prices.count(None)}")
print(f"  Type: {type(prices[0]) if prices[0] else 'None'}")

# genre
genres = [app.get('genre') for app in apps_data]
print(f"\nGenre:")
print(f"  Valeurs manquantes: {genres.count(None)}")
print(f"  Genres uniques: {len(set(genres))}")
print(f"  Top genres: {Counter(genres).most_common(3)}")

# ============================================================================
# 2. INSPECTION DES REVIEWS
# ============================================================================

print("\n\n2. APPS REVIEWS (apps_reviews.jsonl)")
print("-" * 80)

reviews = []
with open('../data/raw/apps_reviews.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        reviews.append(json.loads(line))

print(f"Nombre de reviews: {len(reviews)}")
print(f"\nChamps disponibles dans la premiere review:")
for key in sorted(reviews[0].keys()):
    print(f"  - {key}")

# Analyser les champs cles
print("\n--- Analyse des champs cles ---")

# reviewId
review_ids = [r.get('reviewId') for r in reviews]
print(f"\nreviewId:")
print(f"  Total: {len(review_ids)}")
print(f"  Uniques: {len(set(review_ids))}")
print(f"  Doublons: {len(review_ids) - len(set(review_ids))}")

# score
review_scores = [r.get('score') for r in reviews]
print(f"\nScore:")
print(f"  Valeurs manquantes: {review_scores.count(None)}")
print(f"  Distribution: {Counter(review_scores)}")

# content
contents = [r.get('content') for r in reviews]
print(f"\nContent:")
print(f"  Valeurs manquantes: {contents.count(None)}")
print(f"  Vides: {contents.count('')}")

# at (timestamp)
timestamps = [r.get('at') for r in reviews]
print(f"\nTimestamp (at):")
print(f"  Valeurs manquantes: {timestamps.count(None)}")
print(f"  Type: {type(timestamps[0])}")
print(f"  Exemple: {timestamps[0]}")

# thumbsUpCount
thumbs = [r.get('thumbsUpCount') for r in reviews]
print(f"\nthumbsUpCount:")
print(f"  Valeurs manquantes: {thumbs.count(None)}")
print(f"  Type: {type(thumbs[0])}")

# ============================================================================
# 3. PROBLEMES IDENTIFIES
# ============================================================================

print("\n\n3. PROBLEMES IDENTIFIES")
print("=" * 80)

problemes = [
    "1. INSTALLS: Format texte avec virgules et '+' (ex: '1,000,000+') - Besoin de conversion numerique",
    "2. SCORE: Type float - Peut necessiter arrondi pour certaines analyses",
    "3. TIMESTAMPS: Format ISO string - Besoin de conversion en datetime pour agregation",
    "4. VALEURS MANQUANTES: Certains champs ont des None - Besoin de strategie de gestion",
    "5. CHAMPS INUTILES: Beaucoup de champs dans metadata non necessaires pour analytics",
    "6. DOUBLONS POTENTIELS: Verifier si appId ou reviewId ont des doublons",
    "7. TYPES INCOHERENTS: Certains champs numeriques peuvent etre stockes comme strings"
]

for probleme in problemes:
    print(f"\n{probleme}")

print("\n" + "=" * 80)
print("INSPECTION TERMINEE")
print("=" * 80)

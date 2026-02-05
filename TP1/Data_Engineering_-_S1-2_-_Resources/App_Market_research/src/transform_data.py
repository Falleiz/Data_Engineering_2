# Script de transformation des donnees brutes
# Convertit JSON/JSONL en CSV structure pour analytics

import json
import pandas as pd
import re
from datetime import datetime

print("=" * 80)
print("TRANSFORMATION DES DONNEES")
print("=" * 80)

# ============================================================================
# FONCTIONS DE TRANSFORMATION
# ============================================================================

def clean_installs(installs_str):
    """
    Convertit '1,000,000+' en nombre entier
    PROBLEME IDENTIFIE: Format texte avec virgules et '+'
    """
    if pd.isna(installs_str) or installs_str is None:
        return None
    
    # Retirer les virgules et le '+'
    clean = str(installs_str).replace(',', '').replace('+', '')
    
    try:
        return int(clean)
    except:
        return None

def clean_price(price):
    """
    S'assure que price est un nombre
    """
    if pd.isna(price) or price is None:
        return 0.0
    
    try:
        return float(price)
    except:
        return 0.0

def clean_score(score):
    """
    Arrondit le score a 2 decimales
    """
    if pd.isna(score) or score is None:
        return None
    
    try:
        return round(float(score), 2)
    except:
        return None

def parse_timestamp(timestamp_str):
    """
    Convertit ISO string en datetime
    PROBLEME IDENTIFIE: Timestamps en string, pas en datetime
    """
    if pd.isna(timestamp_str) or timestamp_str is None:
        return None
    
    try:
        return pd.to_datetime(timestamp_str)
    except:
        return None

# ============================================================================
# 1. TRANSFORMATION DES METADONNEES DES APPLICATIONS
# ============================================================================

print("\n1. Transformation: Apps Metadata")
print("-" * 80)

# Lire les donnees brutes
with open('../data/raw/apps_metadata.json', 'r', encoding='utf-8') as f:
    apps_raw = json.load(f)

print(f"Apps brutes: {len(apps_raw)}")

# Extraire uniquement les champs necessaires
apps_clean = []

for app in apps_raw:
    clean_app = {
        'appId': app.get('appId'),
        'title': app.get('title'),
        'developer': app.get('developer'),
        'score': clean_score(app.get('score')),
        'ratings': app.get('ratings'),
        'installs': clean_installs(app.get('installs')),
        'genre': app.get('genre'),
        'price': clean_price(app.get('price'))
    }
    apps_clean.append(clean_app)

# Convertir en DataFrame
apps_df = pd.DataFrame(apps_clean)

# Verifications
print(f"\nApres transformation:")
print(f"  Lignes: {len(apps_df)}")
print(f"  Colonnes: {list(apps_df.columns)}")
print(f"  Doublons (appId): {apps_df['appId'].duplicated().sum()}")
print(f"  Valeurs manquantes par colonne:")
for col in apps_df.columns:
    missing = apps_df[col].isna().sum()
    if missing > 0:
        print(f"    - {col}: {missing}")

# Sauvegarder
output_path = '../data/processed/apps_catalog.csv'
apps_df.to_csv(output_path, index=False, encoding='utf-8')
print(f"\nSauvegarde: {output_path}")

# ============================================================================
# 2. TRANSFORMATION DES REVIEWS
# ============================================================================

print("\n\n2. Transformation: Apps Reviews")
print("-" * 80)

# Lire les reviews (JSONL)
reviews_raw = []
with open('../data/raw/apps_reviews.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        reviews_raw.append(json.loads(line))

print(f"Reviews brutes: {len(reviews_raw)}")

# Extraire uniquement les champs necessaires
reviews_clean = []

for review in reviews_raw:
    clean_review = {
        'app_id': review.get('appId'),
        'app_name': review.get('app_title'),
        'reviewId': review.get('reviewId'),
        'userName': review.get('userName'),
        'score': review.get('score'),
        'content': review.get('content'),
        'thumbsUpCount': review.get('thumbsUpCount'),
        'at': review.get('at')  # Garder en string pour l'instant
    }
    reviews_clean.append(clean_review)

# Convertir en DataFrame
reviews_df = pd.DataFrame(reviews_clean)

# Convertir les timestamps
reviews_df['at'] = reviews_df['at'].apply(parse_timestamp)

# Verifications
print(f"\nApres transformation:")
print(f"  Lignes: {len(reviews_df)}")
print(f"  Colonnes: {list(reviews_df.columns)}")
print(f"  Doublons (reviewId): {reviews_df['reviewId'].duplicated().sum()}")
print(f"  Valeurs manquantes par colonne:")
for col in reviews_df.columns:
    missing = reviews_df[col].isna().sum()
    if missing > 0:
        print(f"    - {col}: {missing}")

# Sauvegarder
output_path = '../data/processed/apps_reviews.csv'
reviews_df.to_csv(output_path, index=False, encoding='utf-8')
print(f"\nSauvegarde: {output_path}")

# ============================================================================
# 3. VERIFICATION FINALE
# ============================================================================

print("\n\n3. Verification Finale")
print("=" * 80)

print("\nApps Catalog:")
print(f"  Format: CSV tabulaire")
print(f"  Lignes: {len(apps_df)}")
print(f"  Types de donnees:")
for col in apps_df.columns:
    print(f"    - {col}: {apps_df[col].dtype}")

print("\nApps Reviews:")
print(f"  Format: CSV tabulaire")
print(f"  Lignes: {len(reviews_df)}")
print(f"  Types de donnees:")
for col in reviews_df.columns:
    print(f"    - {col}: {reviews_df[col].dtype}")

print("\nJointure possible:")
common_apps = set(apps_df['appId']) & set(reviews_df['app_id'])
print(f"  Apps communes: {len(common_apps)}")

print("\n" + "=" * 80)
print("TRANSFORMATION TERMINEE")
print("=" * 80)

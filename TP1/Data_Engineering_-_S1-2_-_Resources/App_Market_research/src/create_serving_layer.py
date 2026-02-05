# Script de creation du Serving Layer
# Cree des agregations prete pour l'analyse et les dashboards

import pandas as pd
from datetime import datetime

print("=" * 80)
print("CREATION DU SERVING LAYER")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# CHARGEMENT DES DONNEES TRANSFORMEES
# ============================================================================

print("\nChargement des donnees transformees...")

# Lire les reviews transformees
reviews_df = pd.read_csv('../data/processed/apps_reviews.csv')

# Convertir la colonne 'at' en datetime si ce n'est pas deja fait
reviews_df['at'] = pd.to_datetime(reviews_df['at'])

print(f"Reviews chargees: {len(reviews_df)} lignes")
print(f"Colonnes: {list(reviews_df.columns)}")

# ============================================================================
# OUTPUT 1: APP-LEVEL KPIs (Metriques par Application)
# ============================================================================

print("\n\n1. Creation: App-Level KPIs")
print("-" * 80)

# Grouper par app_id et calculer les metriques
print("\nCalcul des metriques par application...")

# Nombre de reviews par app
num_reviews = reviews_df.groupby('app_id').size().reset_index(name='num_reviews')

# Note moyenne par app
avg_rating = reviews_df.groupby('app_id')['score'].mean().reset_index(name='avg_rating')
avg_rating['avg_rating'] = avg_rating['avg_rating'].round(2)  # Arrondir a 2 decimales

# Pourcentage de reviews negatives (score <= 2)
reviews_low = reviews_df[reviews_df['score'] <= 2]
low_rating_count = reviews_low.groupby('app_id').size().reset_index(name='low_rating_count')

# Date de la premiere review
first_review = reviews_df.groupby('app_id')['at'].min().reset_index(name='first_review_date')

# Date de la derniere review
last_review = reviews_df.groupby('app_id')['at'].max().reset_index(name='last_review_date')

# Fusionner toutes les metriques
print("Fusion des metriques...")
app_kpis = num_reviews
app_kpis = app_kpis.merge(avg_rating, on='app_id', how='left')
app_kpis = app_kpis.merge(low_rating_count, on='app_id', how='left')
app_kpis = app_kpis.merge(first_review, on='app_id', how='left')
app_kpis = app_kpis.merge(last_review, on='app_id', how='left')

# Calculer le pourcentage de reviews negatives
app_kpis['low_rating_count'] = app_kpis['low_rating_count'].fillna(0)  # Remplacer NaN par 0
app_kpis['pct_low_rating'] = (app_kpis['low_rating_count'] / app_kpis['num_reviews'] * 100).round(2)

# Supprimer la colonne intermediaire
app_kpis = app_kpis.drop('low_rating_count', axis=1)

# Ajouter le nom de l'app pour plus de lisibilite
app_names = reviews_df[['app_id', 'app_name']].drop_duplicates()
app_kpis = app_kpis.merge(app_names, on='app_id', how='left')

# Reordonner les colonnes
app_kpis = app_kpis[['app_id', 'app_name', 'num_reviews', 'avg_rating', 
                      'pct_low_rating', 'first_review_date', 'last_review_date']]

# Trier par nombre de reviews (decroissant)
app_kpis = app_kpis.sort_values('num_reviews', ascending=False)

print(f"\nApp-Level KPIs crees:")
print(f"  Nombre d'apps: {len(app_kpis)}")
print(f"  Colonnes: {list(app_kpis.columns)}")

# Afficher un apercu
print("\nApercu (Top 5 apps par nombre de reviews):")
print(app_kpis.head().to_string(index=False))

# Sauvegarder
output_path = '../data/processed/app_level_kpis.csv'
app_kpis.to_csv(output_path, index=False)
print(f"\nSauvegarde: {output_path}")

# ============================================================================
# OUTPUT 2: DAILY METRICS (Metriques Quotidiennes)
# ============================================================================

print("\n\n2. Creation: Daily Metrics")
print("-" * 80)

# Extraire la date (sans l'heure) de chaque review
reviews_df['date'] = reviews_df['at'].dt.date

print("\nCalcul des metriques quotidiennes...")

# Nombre de reviews par jour
daily_reviews = reviews_df.groupby('date').size().reset_index(name='daily_reviews')

# Note moyenne par jour
daily_avg_rating = reviews_df.groupby('date')['score'].mean().reset_index(name='daily_avg_rating')
daily_avg_rating['daily_avg_rating'] = daily_avg_rating['daily_avg_rating'].round(2)

# Fusionner
daily_metrics = daily_reviews.merge(daily_avg_rating, on='date', how='left')

# Trier par date
daily_metrics = daily_metrics.sort_values('date')

print(f"\nDaily Metrics crees:")
print(f"  Nombre de jours: {len(daily_metrics)}")
print(f"  Colonnes: {list(daily_metrics.columns)}")
print(f"  Periode: {daily_metrics['date'].min()} a {daily_metrics['date'].max()}")

# Afficher un apercu
print("\nApercu (5 premiers jours):")
print(daily_metrics.head().to_string(index=False))

# Sauvegarder
output_path = '../data/processed/daily_metrics.csv'
daily_metrics.to_csv(output_path, index=False)
print(f"\nSauvegarde: {output_path}")

# ============================================================================
# STATISTIQUES FINALES
# ============================================================================

print("\n\n3. Statistiques Finales")
print("=" * 80)

print("\nApp-Level KPIs:")
print(f"  Total apps: {len(app_kpis)}")
print(f"  App avec le plus de reviews: {app_kpis.iloc[0]['app_name']} ({app_kpis.iloc[0]['num_reviews']} reviews)")
print(f"  Meilleure note moyenne: {app_kpis['avg_rating'].max()}")
print(f"  Pire note moyenne: {app_kpis['avg_rating'].min()}")

print("\nDaily Metrics:")
print(f"  Total jours: {len(daily_metrics)}")
print(f"  Moyenne de reviews par jour: {daily_metrics['daily_reviews'].mean():.1f}")
print(f"  Jour avec le plus de reviews: {daily_metrics.loc[daily_metrics['daily_reviews'].idxmax(), 'date']} ({daily_metrics['daily_reviews'].max()} reviews)")

print("\n" + "=" * 80)
print("SERVING LAYER CREE AVEC SUCCES")
print("=" * 80)
print("\nFichiers crees:")
print("  1. data/processed/app_level_kpis.csv")
print("  2. data/processed/daily_metrics.csv")
print("\nCes fichiers sont prets pour:")
print("  - Dashboards")
print("  - Rapports")
print("  - Analyses rapides")
print("=" * 80)

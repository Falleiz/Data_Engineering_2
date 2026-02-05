# Script pour preparer les donnees pour Looker Studio
# Cree des fichiers CSV optimises pour l'upload sur Google Sheets

import pandas as pd
from datetime import datetime

print("=" * 80)
print("PREPARATION DES DONNEES POUR LOOKER STUDIO")
print("=" * 80)

# ============================================================================
# CHARGER LES DONNEES DU SERVING LAYER
# ============================================================================

print("\nChargement des donnees...")

# App-Level KPIs
app_kpis = pd.read_csv('../data/processed/app_level_kpis.csv')
print(f"App-Level KPIs: {len(app_kpis)} lignes")

# Daily Metrics
daily_metrics = pd.read_csv('../data/processed/daily_metrics.csv')
print(f"Daily Metrics: {len(daily_metrics)} lignes")

# Apps Catalog
apps_catalog = pd.read_csv('../data/processed/apps_catalog.csv')
print(f"Apps Catalog: {len(apps_catalog)} lignes")

# ============================================================================
# ENRICHIR LES DONNEES POUR LOOKER STUDIO
# ============================================================================

print("\nEnrichissement des donnees...")

# Fusionner app_kpis avec apps_catalog pour avoir toutes les infos
app_kpis_enriched = app_kpis.merge(
    apps_catalog[['appId', 'developer', 'genre', 'price', 'installs', 'ratings']], 
    left_on='app_id', 
    right_on='appId', 
    how='left'
)

# Supprimer la colonne dupliquee
app_kpis_enriched = app_kpis_enriched.drop('appId', axis=1)

# Reordonner les colonnes pour plus de clarte
app_kpis_enriched = app_kpis_enriched[[
    'app_id', 'app_name', 'developer', 'genre', 'price',
    'num_reviews', 'avg_rating', 'pct_low_rating',
    'installs', 'ratings',
    'first_review_date', 'last_review_date'
]]

print(f"App KPIs enrichies: {len(app_kpis_enriched)} lignes, {len(app_kpis_enriched.columns)} colonnes")

# ============================================================================
# SAUVEGARDER LES FICHIERS POUR LOOKER STUDIO
# ============================================================================

print("\nSauvegarde des fichiers pour Looker Studio...")

# Fichier 1: App KPIs enrichies
output_path_1 = '../data/processed/looker_app_kpis.csv'
app_kpis_enriched.to_csv(output_path_1, index=False)
print(f"1. {output_path_1}")

# Fichier 2: Daily Metrics (deja pret)
output_path_2 = '../data/processed/looker_daily_metrics.csv'
daily_metrics.to_csv(output_path_2, index=False)
print(f"2. {output_path_2}")

print("\n" + "=" * 80)
print("FICHIERS PRETS POUR LOOKER STUDIO")
print("=" * 80)
print(f"\n1. {output_path_1}")
print(f"2. {output_path_2}")
print("\nUploadez ces fichiers sur Google Sheets, puis creez votre dashboard Looker Studio !")
print("=" * 80)

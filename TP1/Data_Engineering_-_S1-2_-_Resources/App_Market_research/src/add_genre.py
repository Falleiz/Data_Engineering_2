# Script pour ajouter le champ "genre" a app_level_kpis

import pandas as pd

print("Ajout du champ 'genre' a app_level_kpis...")

# Charger les fichiers
app_kpis = pd.read_csv('../data/processed/app_level_kpis.csv')
apps_catalog = pd.read_csv('../data/processed/apps_catalog.csv')

# Fusionner pour ajouter le genre
app_kpis_with_genre = app_kpis.merge(
    apps_catalog[['appId', 'genre']], 
    left_on='app_id', 
    right_on='appId', 
    how='left'
)

# Supprimer la colonne dupliquee
app_kpis_with_genre = app_kpis_with_genre.drop('appId', axis=1)

# Sauvegarder
app_kpis_with_genre.to_csv('../data/processed/app_level_kpis.csv', index=False)

print("OK - 'genre' ajoute a app_level_kpis.csv")
print(f"Colonnes: {list(app_kpis_with_genre.columns)}")

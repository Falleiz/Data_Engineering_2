# Etape 3: Extraction des avis utilisateurs (reviews)
# Lit apps_metadata.json et extrait les reviews pour chaque app

import json
import time
from datetime import datetime
from google_play_scraper import reviews, Sort

# Configuration
LANG = 'en'
COUNTRY = 'us'
MAX_REVIEWS_PER_APP = 500  # Maximum de reviews par app
INPUT_FILE = '../data/raw/apps_metadata.json'
OUTPUT_FILE = '../data/raw/apps_reviews.jsonl'
STATS_FILE = '../data/raw/reviews_extraction_stats.json'

print("=" * 80)
print("EXTRACTION DES AVIS UTILISATEURS")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Reviews max par app: {MAX_REVIEWS_PER_APP}")
print("=" * 80)

# Lire les metadonnees des apps
print(f"\nLecture de: {INPUT_FILE}")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    apps_metadata = json.load(f)

print(f"Nombre d'apps: {len(apps_metadata)}")

# Ouvrir le fichier de sortie en mode ecriture
output_file = open(OUTPUT_FILE, 'w', encoding='utf-8')

# Statistiques
total_reviews = 0
reviews_stats = []

for i, app_data in enumerate(apps_metadata, 1):
    app_id = app_data['appId']
    app_title = app_data.get('title', 'N/A')
    
    print(f"\n[{i}/{len(apps_metadata)}] {app_title}")
    print(f"  App ID: {app_id}")
    
    try:
        # Recuperer les reviews
        result, continuation_token = reviews(
            app_id,
            lang=LANG,
            country=COUNTRY,
            count=MAX_REVIEWS_PER_APP,
            sort=Sort.NEWEST  # Les plus recentes d'abord
        )
        
        # Ecrire chaque review dans le fichier JSONL (1 review par ligne)
        for review in result:
            # Ajouter des metadonnees
            review['appId'] = app_id
            review['app_title'] = app_title
            review['extraction_date'] = datetime.now().isoformat()
            
            # Convertir les datetime en string pour JSON
            if 'at' in review and hasattr(review['at'], 'isoformat'):
                review['at'] = review['at'].isoformat()
            if 'repliedAt' in review and review['repliedAt'] and hasattr(review['repliedAt'], 'isoformat'):
                review['repliedAt'] = review['repliedAt'].isoformat()
            
            # Ecrire en JSONL (1 ligne = 1 review)
            output_file.write(json.dumps(review, ensure_ascii=False) + '\n')
            total_reviews += 1
        
        # Statistiques pour cette app
        stats = {
            'appId': app_id,
            'app_title': app_title,
            'reviews_count': len(result),
            'has_more': continuation_token is not None
        }
        reviews_stats.append(stats)
        
        print(f"  OK - {len(result)} reviews extraites")
        if continuation_token:
            print(f"       (Plus de reviews disponibles)")
        
    except Exception as e:
        print(f"  ERREUR: {str(e)}")
        stats = {
            'appId': app_id,
            'app_title': app_title,
            'reviews_count': 0,
            'error': str(e)
        }
        reviews_stats.append(stats)
    
    # Pause pour eviter de surcharger l'API
    if i < len(apps_metadata):  # Pas de pause apres la derniere
        time.sleep(2)

# Fermer le fichier de sortie
output_file.close()

print(f"\n\nSauvegarde des reviews...")
print(f"OK - Fichier cree: {OUTPUT_FILE}")
print(f"     Format: JSONL (1 review par ligne)")
print(f"     Total reviews: {total_reviews}")

# Sauvegarder les statistiques
stats_summary = {
    'extraction_date': datetime.now().isoformat(),
    'total_apps': len(apps_metadata),
    'total_reviews': total_reviews,
    'average_reviews_per_app': total_reviews / len(apps_metadata) if apps_metadata else 0,
    'reviews_per_app': reviews_stats
}

with open(STATS_FILE, 'w', encoding='utf-8') as f:
    json.dump(stats_summary, f, ensure_ascii=False, indent=2)

print(f"\nStatistiques sauvegardees: {STATS_FILE}")

# Resume
print("\n" + "=" * 80)
print("RESUME")
print("=" * 80)
print(f"Apps traitees: {len(apps_metadata)}")
print(f"Total reviews extraites: {total_reviews}")
print(f"Moyenne par app: {total_reviews / len(apps_metadata):.1f}")

print("\nTop 10 apps par nombre de reviews:")
sorted_stats = sorted(reviews_stats, key=lambda x: x.get('reviews_count', 0), reverse=True)
for j, stat in enumerate(sorted_stats[:10], 1):
    print(f"  {j}. {stat['app_title']}: {stat.get('reviews_count', 0)} reviews")

print("=" * 80)

# Etape 2: Extraction des metadonnees completes des applications
# Lit apps_found.json et extrait toutes les donnees disponibles pour chaque app

import json
import time
from datetime import datetime
from google_play_scraper import app

# Configuration
LANG = 'en'
COUNTRY = 'us'
INPUT_FILE = '../data/raw/apps_found.json'
OUTPUT_FILE = '../data/raw/apps_metadata.json'
ERRORS_FILE = '../data/raw/apps_metadata_errors.json'

print("=" * 80)
print("EXTRACTION DES METADONNEES DES APPLICATIONS")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Lire la liste des apps trouvees
print(f"\nLecture de: {INPUT_FILE}")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    apps_found = json.load(f)

print(f"Nombre d'apps a extraire: {len(apps_found)}")

# Extraction des metadonnees
apps_metadata = []
apps_errors = []

for i, app_info in enumerate(apps_found, 1):
    app_id = app_info['appId']
    app_title = app_info.get('title', 'N/A')
    
    print(f"\n[{i}/{len(apps_found)}] {app_title}")
    print(f"  App ID: {app_id}")
    
    try:
        # Recuperer TOUTES les donnees de l'application
        app_data = app(
            app_id,
            lang=LANG,
            country=COUNTRY
        )
        
        # Ajouter des metadonnees d'extraction
        app_data['extraction_date'] = datetime.now().isoformat()
        app_data['extraction_source'] = 'google_play_scraper'
        
        apps_metadata.append(app_data)
        
        # Afficher quelques infos cles
        print(f"  OK - Score: {app_data.get('score', 'N/A')}")
        print(f"       Installs: {app_data.get('installs', 'N/A')}")
        print(f"       Reviews: {app_data.get('reviews', 'N/A')}")
        
    except Exception as e:
        error_info = {
            'appId': app_id,
            'title': app_title,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        apps_errors.append(error_info)
        print(f"  ERREUR: {str(e)}")
    
    # Pause pour eviter de surcharger l'API
    if i < len(apps_found):  # Pas de pause apres la derniere
        time.sleep(2)

# Sauvegarder les metadonnees
print(f"\n\nSauvegarde des metadonnees...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(apps_metadata, f, ensure_ascii=False, indent=2)

print(f"OK - Fichier cree: {OUTPUT_FILE}")
print(f"     Nombre d'apps: {len(apps_metadata)}")
if apps_metadata:
    print(f"     Nombre de champs par app: {len(apps_metadata[0].keys())}")

# Sauvegarder les erreurs si presentes
if apps_errors:
    print(f"\nSauvegarde des erreurs...")
    with open(ERRORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps_errors, f, ensure_ascii=False, indent=2)
    print(f"OK - Fichier cree: {ERRORS_FILE}")
    print(f"     Nombre d'erreurs: {len(apps_errors)}")

# Resume
print("\n" + "=" * 80)
print("RESUME")
print("=" * 80)
print(f"Apps extraites avec succes: {len(apps_metadata)}")
print(f"Apps en erreur: {len(apps_errors)}")
print(f"Taux de succes: {len(apps_metadata) / len(apps_found) * 100:.1f}%")
print("=" * 80)

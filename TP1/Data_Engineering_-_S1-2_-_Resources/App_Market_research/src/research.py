# Etape 1: Recherche des applications de prise de notes avec IA
# On cherche d'abord les apps sans les extraire

from google_play_scraper import search
import json

# Configuration
LANG = 'en'
COUNTRY = 'us'

# Mots-cles pour rechercher des apps de prise de notes avec IA
SEARCH_QUERIES = [
    "AI note taking",
    "AI notes",
    "smart notes AI",
    "voice notes AI",
    "AI notebook"
]

print("=" * 80)
print("RECHERCHE DES APPLICATIONS DE PRISE DE NOTES AVEC IA")
print("=" * 80)

all_apps = []
all_app_ids = set()

for query in SEARCH_QUERIES:
    print(f"\nRecherche: '{query}'")
    
    try:
        results = search(
            query,
            lang=LANG,
            country=COUNTRY,
            n_hits=30  # Maximum autorise par Google
        )
        
        print(f"  Trouve: {len(results)} apps")
        
        for result in results:
            app_id = result.get('appId')
            if app_id and app_id not in all_app_ids:
                all_app_ids.add(app_id)
                app_info = {
                    'appId': app_id,
                    'title': result.get('title'),
                    'developer': result.get('developer'),
                    'score': result.get('score'),
                    'found_with_query': query
                }
                all_apps.append(app_info)
                print(f"  - {result.get('title')} ({app_id})")
        
    except Exception as e:
        print(f"  ERREUR: {str(e)}")

        

print("\n" + "=" * 80)
print("RESUME")
print("=" * 80)
print(f"Total d'apps uniques trouvees: {len(all_apps)}")

# Sauvegarder la liste des apps trouvees
output_path = "../data/raw/apps_found.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_apps, f, ensure_ascii=False, indent=2)

print(f"\nListe sauvegardee dans: apps_found.json")
print(f"\nTop 10 apps trouvees:")
for i, app in enumerate(all_apps[:10], 1):
    print(f"  {i}. {app['title']} - Score: {app['score']}")

if len(all_apps) > 10:
    print(f"  ... et {len(all_apps) - 10} autres apps")

print("\n" + "=" * 80)

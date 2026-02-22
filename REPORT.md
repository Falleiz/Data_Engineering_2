# 📄 Rapport de Projet : Modern Data Pipeline (dbt & DuckDB)

**Auteurs :** [Vos Noms]
**Date :** 22 Février 2026

---

## 1. Description de l'Architecture Finale

Notre pipeline de données a évolué d'une approche ETL Python classique vers une architecture **ELT moderne** basée sur **dbt (data build tool)** et **DuckDB**.

### Schéma en Flocon (Snowflake Schema)
Contrairement au TP1 (Star Schema simple), nous avons opté pour un **Snowflake Schema** normalisé pour garantir une meilleure intégrité des données et réduire la redondance.

*   **Fact Table (`fact_reviews`)** : Contient les métriques (notes, avis) et les clés étrangères. Elle est chargée de manière **incrémentale**.
*   **Dimensions Normalisées** :
    *   `dim_apps` : Informations sur les applications, historisées via **SCD2**.
    *   `dim_developers` : Dimension séparée pour les développeurs (liée à `dim_apps`).
    *   `dim_categories` : Dimension séparée pour les genres (liée à `dim_apps`).
    *   `dim_date` : Calendrier analytique généré automatiquement par dbt.

![Architecture Diagram](TP1/assets/dbt-dag.png)
*(Voir le diagramme de lignage complet dans la documentation dbt)*

---

## 2. Implémentation des Fonctionnalités Avancées

### A. SCD2 (Slowly Changing Dimensions)
Pour suivre l'évolution des métriques clés des applications (comme le prix ou le changement de genre), nous avons mis en place un **SCD Type 2**.

*   **Méthode :** Utilisation de `dbt snapshots`.
*   **Implémentation :** Le fichier `snapshots/apps_snapshot.sql` surveille les colonnes `price`, `genre` et `app_name`.
*   **Résultat :** Au lieu d'écraser les données, dbt crée une nouvelle ligne avec des colonnes `dbt_valid_from` et `dbt_valid_to`, préservant ainsi l'historique complet pour les analyses temporelles.

### B. Chargement Incrémental (Incremental Loading)
La table `fact_reviews` pouvant devenir volumineuse, nous avons abandonné le *Full Refresh* pour un chargement incrémental optimisé.

*   **Méthode :** Configuration `materialized='incremental'` dans dbt.
*   **Logique :** 
    ```sql
    {% if is_incremental() %}
      AND review_timestamp > (select max(review_timestamp) from {{ this }})
    {% endif %}
    ```
*   **Bénéfice :** Seules les nouvelles reviews (basées sur le `review_timestamp`) sont traitées et insérées lors des exécutions quotidiennes, réduisant drastiquement le temps de calcul.

### C. Data Quality & Testing
Nous avons intégré des tests automatiques à chaque étape du pipeline via `schema.yml` :
*   **Tests Génériques :** `unique`, `not_null` sur toutes les clés primaires.
*   **Intégrité Référentielle :** Tests de `relationships` pour garantir que chaque review pointe vers une app et une date existantes.

---

## 3. Comparaison : Python-Only vs dbt-Based Pipeline

| Critère | Pipeline Python (TP1) | Pipeline dbt (TP2) |
| :--- | :--- | :--- |
| **Paradigme** | Impératif (Comment faire) | Déclaratif (Quoi faire) |
| **Transformation** | Pandas (en mémoire, difficile à scaler) | SQL (exécuté par le moteur DB, performant) |
| **Gestion des Dépendances** | Manuelle (ordre des scripts) | Automatique (DAG généré par dbt) |
| **SCD2 & Incrémental** | Complexe à coder "from scratch" | Séparé de la logique métier (Configs simples) |
| **Documentation** | Souvent obsolète ou externe | Générée automatiquement depuis le code |
| **Tests** | À écrire manuellement (Unit tests) | Intégrés et configurables en YAML |

**Conclusion :** L'approche dbt permet de se concentrer sur la **logique métier** (SQL) plutôt que sur l'orchestration technique, rendant le projet plus maintenable et scalable.

---

## 4. Réflexions & Retour d'Expérience

### ⚠️ The Most Fragile Part
La partie la plus fragile reste l'ingestion des **fichiers JSON bruts**.
*   Si le schéma du JSON change (ex: un champ renommé ou un type de données modifié), le modèle de *Staging* cassera.
*   *Solution potentielle :* Ajouter une étape de validation de schéma en amont (contract testing) ou utiliser un outil d'ingestion comme Airbyte.

### 🏛️ Biggest Architectural Insight
La séparation entre le **Stockage/Calcul** (DuckDB) et la **Logique de Transformation** (dbt). 
Nous avons réalisé que dbt n'est "que" un compilateur SQL : il ne touche pas aux données lui-même, il donne des ordres à la base de données. Cela signifie qu'on peut changer de moteur (passer de DuckDB à Snowflake ou BigQuery) en changeant simplement la configuration dbt, sans réécrire toute la logique métier.

### 🔄 One Design Decision to Change
Si c'était à refaire, nous gérerions mieux la **Dimension Date**.
Au lieu de la générer "à la volée" dans dbt à partir des données existantes (ce qui limite le calendrier aux dates où il y a des reviews), nous utiliserions un package dbt comme `dbt-date` ou un script dédié pour générer un calendrier complet (passé et futur) sur 20 ans. Cela éviterait des trous dans les analyses temporelles s'il n'y a pas de ventes certains jours.

---

*Fin du rapport.*

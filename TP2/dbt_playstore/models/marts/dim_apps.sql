with stg_apps as (
    -- On lit maintenant dans le Snapshot pour avoir l'historique
    select * from {{ ref('apps_snapshot') }}
),

developers as (
    select * from {{ ref('dim_developers') }}
),

categories as (
    select * from {{ ref('dim_categories') }}
)

select
    -- Génération d'une clé artificielle entière pour l'App (Surrogate Key)
    row_number() over (order by stg_apps.app_id) as app_key,
    
    stg_apps.app_id,
    stg_apps.app_name,
    
    -- Récupération des clés étrangères depuis les nouvelles dimensions
    developers.developer_key,
    categories.category_key,
    
    stg_apps.price,
    -- Logique pour déterminer si payant (TRUE) ou gratuit (FALSE)
    case when stg_apps.price > 0 then true else false end as is_paid,
    
    stg_apps.installs,
    stg_apps.rating as catalog_rating,
    stg_apps.ratings_count

from stg_apps
-- Jointure avec les dimensions pour récupérer les clés (Snowflake Schema)
left join developers on stg_apps.developer = developers.developer_name
left join categories on stg_apps.genre = categories.category_name
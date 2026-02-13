with stg_reviews as (
    select * from {{ ref('stg_playstore_reviews') }}
),

dim_apps as (
    select * from {{ ref('dim_apps') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
)

select
    stg_reviews.review_id, -- On garde l'ID technique
    
    -- Clés Étrangères (Surrogate Keys)
    dim_apps.app_key,         -- Lien vers l'application
    dim_apps.developer_key,   -- Lien direct vers le développeur (via l'app)
    dim_date.date_key,        -- Lien vers la date
    
    stg_reviews.rating,
    stg_reviews.thumbs_up_count,
    stg_reviews.review_text,
    stg_reviews.app_version as review_version

from stg_reviews
-- Jointure pour récupérer les clés de l'app et du dev
inner join dim_apps on stg_reviews.app_id = dim_apps.app_id
-- Jointure pour récupérer la clé de date
inner join dim_date on stg_reviews.review_timestamp::date = dim_date.date
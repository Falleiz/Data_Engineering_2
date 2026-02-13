with stg_reviews as (
    select * from {{ ref('stg_playstore_reviews') }}
),

stg_apps as (
    select * from {{ ref('stg_playstore_apps') }}
)

select
    r.review_id,
    r.review_text,
    r.rating,
    r.thumbs_up_count,
    r.review_timestamp,
    -- Clés Étrangères vers les dimensions (Les branches de l'étoile)
    r.app_id,           -- Lien vers dim_apps
    r.review_timestamp::date as date_day -- Lien vers dim_dates
from stg_reviews r
-- On ne garde que les reviews qui ont une app valide (Inner Join)
join stg_apps a on r.app_id = a.app_id
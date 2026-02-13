{{
    config(
        materialized='incremental',
        unique_key='review_id'
    )
}}

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
    stg_reviews.review_id,
    
    dim_apps.app_key,
    dim_apps.developer_key,
    dim_date.date_key,
    
    stg_reviews.rating,
    stg_reviews.thumbs_up_count,
    stg_reviews.review_text,
    stg_reviews.app_version as review_version,
    stg_reviews.review_timestamp -- AJOUTÉ : Indispensable pour l'incrémental

from stg_reviews
inner join dim_apps on stg_reviews.app_id = dim_apps.app_id
inner join dim_date on stg_reviews.review_timestamp::date = dim_date.date

{% if is_incremental() %}
  -- On ne prend que les nouveaux enregistrements (ceux qui sont plus récents que le max déjà chargé)
  AND stg_reviews.review_timestamp > (select max(review_timestamp) from {{ this }})
{% endif %}
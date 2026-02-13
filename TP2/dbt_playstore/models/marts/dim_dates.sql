with stg_reviews as (
    select * from {{ ref('stg_playstore_reviews') }}
),

date_range as (
    -- On récupère la date min et max pour savoir quelle période couvrir
    select
        min(review_timestamp::date) as min_date,
        max(review_timestamp::date) as max_date
    from stg_reviews
),

date_spine as (
    -- Génération automatique des jours entre min et max
    select
        range as date_day
    from range(
        (select min_date from date_range),
        (select max_date from date_range) + interval 1 day,
        interval 1 day
    )
)

select
    date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    dayname(date_day) as day_of_week
from date_spine
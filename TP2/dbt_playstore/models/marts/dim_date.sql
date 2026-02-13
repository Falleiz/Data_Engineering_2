with reviews as (
    select * from {{ ref('stg_playstore_reviews') }}
),

date_range as (
    select
        min(review_timestamp::date) as min_date,
        max(review_timestamp::date) as max_date
    from reviews
),

date_spine as (
    select range as date_day
    from range(
        (select min_date from date_range),
        (select max_date from date_range) + interval 1 day,
        interval 1 day
    )
)

select
    -- Clé entière YYYYMMDD (plus performante)
    (extract(year from date_day) * 10000 + extract(month from date_day) * 100 + extract(day from date_day))::int as date_key,
    date_day as date,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    case when extract(quarter from date_day) is null then 1 else extract(quarter from date_day) end as quarter,
    dayname(date_day) as day_of_week,
    -- Est-ce un weekend ? (Samedi=6, Dimanche=0 en DuckDB)
    case when dayofweek(date_day) in (0, 6) then true else false end as is_weekend
from date_spine
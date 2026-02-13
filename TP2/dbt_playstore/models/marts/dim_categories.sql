with stg_apps as (
    select * from {{ ref('stg_playstore_apps') }}
),

distinct_categories as (
    select distinct
        genre as category_name
    from stg_apps
    where genre is not null
)

select
    row_number() over (order by category_name) as category_key,
    category_name
from distinct_categories
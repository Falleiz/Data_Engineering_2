with stg_apps as (
    select * from {{ ref('stg_playstore_apps') }}
)

select
    app_id,
    app_name,
    genre,
    rating,
    reviews_count,
    installs,
    price,
    case
        when price = 0 then true
        else false
    end as is_free, -- On crée une colonne booléenne plus explicite
    currency,
    developer,
    developer_id,
    released_date,
    updated_timestamp
from stg_apps
with stg_apps as (
    select * from {{ ref('stg_playstore_apps') }}
),

distinct_developers as (
    -- On récupère la liste unique des développeurs et leurs infos
    select distinct
        developer as developer_name,
        developer_email,
        developer_website
    from stg_apps
    where developer is not null
)

select
    -- Génération d'une clé artificielle (1, 2, 3...)
    row_number() over (order by developer_name) as developer_key,
    developer_name,
    developer_website,
    developer_email
from distinct_developers
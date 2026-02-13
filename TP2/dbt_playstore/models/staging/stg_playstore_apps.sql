with source as (
    select * from read_json_auto('raw_data/apps_metadata.json')
),

renamed as (
    select
        appId as app_id,
        title as app_name,
        summary,
        realInstalls as installs,
        score as rating,
        ratings as ratings_count,
        reviews as reviews_count,
        price,
        free,
        currency,
        developer,
        developerId as developer_id,
        genre,
        released as released_date,
        updated as updated_timestamp,
        url
    from source
)

select * from renamed
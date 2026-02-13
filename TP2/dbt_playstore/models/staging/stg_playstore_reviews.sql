with source as (
    select * from read_json_auto('raw_data/apps_reviews.jsonl')
),

renamed as (
    select
        reviewId as review_id,
        appId as app_id,
        userName as user_name,
        content as review_text,
        score as rating,
        thumbsUpCount as thumbs_up_count,
        "at" as review_timestamp,
        replyContent as reply_content,
        repliedAt as replied_timestamp,
        appVersion as app_version
    from source
)

select * from renamed
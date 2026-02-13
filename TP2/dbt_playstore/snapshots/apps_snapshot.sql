{% snapshot apps_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='app_id',
      strategy='check',
      check_cols=['price', 'genre', 'app_name', 'installs'],
      invalidate_hard_deletes=True
    )
}}

select * from {{ ref('stg_playstore_apps') }}

{% endsnapshot %}
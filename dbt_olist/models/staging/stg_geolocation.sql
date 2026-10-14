select
    try_cast(geolocation_zip_code_prefix as integer) as zip_code_prefix,
    try_cast(geolocation_lat as double) as lat,
    try_cast(geolocation_lng as double) as lng,
    geolocation_city as city,
    geolocation_state as state
from {{ source('olist', 'raw_geolocation') }}

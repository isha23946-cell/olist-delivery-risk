select
    zip_code_prefix,
    avg(lat) as lat,
    avg(lng) as lng
from {{ ref('stg_geolocation') }}
where zip_code_prefix is not null
group by zip_code_prefix

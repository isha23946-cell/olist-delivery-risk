select
    zip_code_prefix,
    avg(lat) as lat,
    avg(lng) as lng
from {{ ref('stg_geolocation') }}
where zip_code_prefix is not null
  and lat between -34 and 6
  and lng between -74 and -34
group by zip_code_prefix

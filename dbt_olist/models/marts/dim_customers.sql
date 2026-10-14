select
    c.customer_id,
    c.customer_unique_id,
    c.zip_code_prefix,
    c.city,
    c.state,
    g.lat,
    g.lng
from {{ ref('stg_customers') }} c
left join {{ ref('dim_geo_zip') }} g
    on c.zip_code_prefix = g.zip_code_prefix

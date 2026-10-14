select
    seller_id,
    try_cast(seller_zip_code_prefix as integer) as zip_code_prefix,
    seller_city as city,
    seller_state as state
from {{ source('olist', 'raw_sellers') }}

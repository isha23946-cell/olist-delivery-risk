select
    customer_id,
    customer_unique_id,
    try_cast(customer_zip_code_prefix as integer) as zip_code_prefix,
    customer_city as city,
    customer_state as state
from {{ source('olist', 'raw_customers') }}

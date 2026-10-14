select
    order_id,
    try_cast(payment_sequential as integer) as payment_sequential,
    payment_type,
    try_cast(payment_installments as integer) as payment_installments,
    try_cast(payment_value as double) as payment_value
from {{ source('olist', 'raw_order_payments') }}

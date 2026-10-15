select
    a.order_id,
    count(b.order_id) as seller_prev_orders,
    avg(b.is_late) as seller_prev_late_rate
from {{ ref('fact_orders') }} a
left join {{ ref('fact_orders') }} b
    on a.primary_seller_id = b.primary_seller_id
    and b.delivered_to_customer_at < a.purchased_at
where a.is_late is not null
group by a.order_id

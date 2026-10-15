with vol as (
    select
        i.order_id,
        sum(p.volume_cm3) as total_volume_cm3
    from {{ ref('stg_order_items') }} i
    left join {{ ref('dim_products') }} p
        on i.product_id = p.product_id
    group by i.order_id
),

base as (
    select
        o.*,
        s.state as seller_state,
        c.state as customer_state,
        s.lat as seller_lat,
        s.lng as seller_lng,
        c.lat as customer_lat,
        c.lng as customer_lng,
        v.total_volume_cm3
    from {{ ref('fact_orders') }} o
    left join {{ ref('dim_sellers') }} s
        on o.primary_seller_id = s.seller_id
    left join {{ ref('dim_customers') }} c
        on o.customer_id = c.customer_id
    left join vol v
        on o.order_id = v.order_id
    where o.is_late is not null
)

select
    order_id,
    purchased_at,
    is_late,
    primary_category,
    primary_payment_type,
    max_installments,
    seller_state,
    customer_state,
    case when seller_state = customer_state then 1 else 0 end as same_state,
    n_items,
    n_sellers,
    items_price,
    items_freight,
    items_freight / nullif(items_price, 0) as freight_ratio,
    total_weight_g,
    total_volume_cm3,
    estimated_days,
    month(purchased_at) as purchase_month,
    dayofweek(purchased_at) as purchase_weekday,
    hour(purchased_at) as purchase_hour,
    date_diff('hour', purchased_at, approved_at) as approval_hours,
    6371 * 2 * asin(sqrt(
        power(sin(radians(customer_lat - seller_lat) / 2), 2)
        + cos(radians(seller_lat)) * cos(radians(customer_lat))
        * power(sin(radians(customer_lng - seller_lng) / 2), 2)
    )) as distance_km
from base

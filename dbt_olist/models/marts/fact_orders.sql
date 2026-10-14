with items as (
    select
        i.order_id,
        count(*) as n_items,
        count(distinct i.seller_id) as n_sellers,
        sum(i.price) as items_price,
        sum(i.freight_value) as items_freight,
        sum(p.weight_g) as total_weight_g,
        arg_min(i.seller_id, i.order_item_id) as primary_seller_id,
        arg_min(p.category_name, i.order_item_id) as primary_category
    from {{ ref('stg_order_items') }} i
    left join {{ ref('dim_products') }} p
        on i.product_id = p.product_id
    group by i.order_id
),

payments as (
    select
        order_id,
        sum(payment_value) as total_payment_value,
        max(payment_installments) as max_installments,
        arg_min(payment_type, payment_sequential) as primary_payment_type
    from {{ ref('stg_order_payments') }}
    group by order_id
),

reviews as (
    select
        order_id,
        avg(review_score) as review_score
    from {{ ref('stg_order_reviews') }}
    group by order_id
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    o.approved_at,
    o.delivered_to_carrier_at,
    o.delivered_to_customer_at,
    o.estimated_delivery_at,
    i.n_items,
    i.n_sellers,
    i.items_price,
    i.items_freight,
    i.total_weight_g,
    i.primary_seller_id,
    i.primary_category,
    p.total_payment_value,
    p.max_installments,
    p.primary_payment_type,
    r.review_score,
    date_diff('day', o.purchased_at, o.delivered_to_customer_at) as delivery_days,
    date_diff('day', o.purchased_at, o.estimated_delivery_at) as estimated_days,
    case
        when o.delivered_to_customer_at is null then null
        when o.delivered_to_customer_at > o.estimated_delivery_at then 1
        else 0
    end as is_late
from {{ ref('stg_orders') }} o
left join items i on o.order_id = i.order_id
left join payments p on o.order_id = p.order_id
left join reviews r on o.order_id = r.order_id

select
    p.product_id,
    p.product_category_name as category_name_pt,
    coalesce(t.product_category_name_english, p.product_category_name) as category_name,
    try_cast(p.product_name_lenght as integer) as name_length,
    try_cast(p.product_description_lenght as integer) as description_length,
    try_cast(p.product_photos_qty as integer) as photos_qty,
    try_cast(p.product_weight_g as double) as weight_g,
    try_cast(p.product_length_cm as double) as length_cm,
    try_cast(p.product_height_cm as double) as height_cm,
    try_cast(p.product_width_cm as double) as width_cm
from {{ source('olist', 'raw_products') }} p
left join {{ source('olist', 'raw_product_category_name_translation') }} t
    on p.product_category_name = t.product_category_name

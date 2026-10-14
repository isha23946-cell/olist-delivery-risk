# Olist raw tables

## Joins
- orders is the center: customers via customer_id
- order_items via order_id, then products via product_id and sellers via seller_id
- order_payments and order_reviews via order_id
- geolocation via zip code prefix (customers and sellers)
- product_category_name_translation maps Portuguese category names to English

## To handle in dbt
- Target: late delivery = delivered_customer_date after estimated_delivery_date (delivered orders only)
- order_items and order_payments have several rows per order, so aggregate to one row per order
- geolocation has many rows per zip prefix, so average lat/lng per prefix
- Fix misspelled product columns (lenght) in staging
- Raw layer is loaded as text, so cast types in staging

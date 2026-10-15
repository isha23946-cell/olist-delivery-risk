import duckdb

NUM_COLS = ["n_items", "n_sellers", "items_price", "items_freight", "freight_ratio",
            "total_weight_g", "total_volume_cm3", "estimated_days", "purchase_month",
            "purchase_weekday", "purchase_hour", "approval_hours", "distance_km",
            "same_state", "max_installments", "seller_prev_orders", "seller_prev_late_rate"]
CAT_COLS = ["primary_payment_type", "seller_state", "customer_state", "primary_category"]
FEATURES = NUM_COLS + CAT_COLS


def load_split(train_frac=0.8):
    con = duckdb.connect("warehouse/olist.duckdb", read_only=True)
    df = con.execute("""
        select f.*, h.seller_prev_orders, h.seller_prev_late_rate
        from features_orders f
        join seller_history h on f.order_id = h.order_id
    """).df()
    con.close()
    df[NUM_COLS] = df[NUM_COLS].astype("float64")
    df["is_late"] = df["is_late"].astype(int)
    df = df.sort_values("purchased_at").reset_index(drop=True)
    cut = int(len(df) * train_frac)
    return df.iloc[:cut], df.iloc[cut:]

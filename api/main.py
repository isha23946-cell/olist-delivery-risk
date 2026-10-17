import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = "warehouse/olist.duckdb"
app = FastAPI(title="Olist Delivery Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def query(sql, params=None):
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return con.execute(sql, params or []).df()
    finally:
        con.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/kpis")
def kpis():
    summary = query("""
        select count(*) as delivered_orders,
               round(1 - avg(is_late), 4) as on_time_rate,
               round(avg(review_score), 2) as avg_review_score,
               round(avg(delivery_days), 1) as avg_delivery_days
        from fact_orders where is_late is not null
    """)
    states = query("""
        select customer_state, count(*) as orders,
               round(avg(is_late), 4) as late_rate
        from order_risk_scores
        group by customer_state order by orders desc limit 10
    """)
    return {"summary": summary.to_dict("records")[0],
            "by_state": states.to_dict("records")}


from typing import Optional
from fastapi import Query


@app.get("/high-risk")
def high_risk(limit: int = Query(20, ge=1, le=100), state: Optional[str] = None):
    sql = """
        select order_id, purchased_at, customer_state, seller_state,
               primary_category, estimated_days, round(distance_km, 0) as distance_km,
               items_price, items_freight, round(risk_score, 3) as risk_score, is_late
        from order_risk_scores
        where split = 'test' and flagged = 1
    """
    params = []
    if state:
        sql += " and customer_state = ?"
        params.append(state.upper())
    sql += " order by risk_score desc limit ?"
    params.append(limit)
    df = query(sql, params)
    df["purchased_at"] = df["purchased_at"].astype(str)
    df = df.astype(object).where(df.notna(), None)
    return df.to_dict("records")


import json
import joblib
import pandas as pd
from pydantic import BaseModel, Field

from ml.data import CAT_COLS, FEATURES, NUM_COLS, load_split

model = joblib.load("models/late_delivery_model.joblib")
THRESHOLD = json.load(open("models/threshold.json"))["threshold"]
_train, _ = load_split()
DEFAULTS = _train[NUM_COLS].median().to_dict()


class OrderIn(BaseModel):
    customer_state: str = Field(pattern="^[A-Za-z]{2}$")
    seller_state: str = Field(pattern="^[A-Za-z]{2}$")
    primary_category: str = Field(min_length=1, max_length=60)
    estimated_days: float = Field(gt=0, le=120)
    distance_km: float = Field(ge=0, le=5000)
    items_price: float = Field(gt=0, le=20000)
    items_freight: float = Field(ge=0, le=5000)
    primary_payment_type: str = "credit_card"
    total_weight_g: float = Field(1000, ge=0, le=100000)
    n_items: int = Field(1, ge=1, le=50)
    max_installments: int = Field(1, ge=1, le=24)
    purchase_month: int = Field(6, ge=1, le=12)
    purchase_weekday: int = Field(2, ge=0, le=6)
    seller_prev_late_rate: float = Field(0.05, ge=0, le=1)


GROUPS = {
    "customer_state": ["customer_state", "same_state"],
    "seller_state": ["seller_state", "same_state"],
    "items_price": ["items_price", "freight_ratio"],
    "items_freight": ["items_freight", "freight_ratio"],
}


def build_row(o):
    row = dict(DEFAULTS)
    row.update(o.model_dump())
    row["customer_state"] = o.customer_state.upper()
    row["seller_state"] = o.seller_state.upper()
    row["same_state"] = 1.0 if row["customer_state"] == row["seller_state"] else 0.0
    row["freight_ratio"] = o.items_freight / o.items_price if o.items_price else None
    return row


def score_row(row):
    df = pd.DataFrame([row])[FEATURES]
    df[NUM_COLS] = df[NUM_COLS].astype("float64")
    return float(model.predict_proba(df)[0, 1])


@app.post("/predict")
def predict(order: OrderIn):
    row = build_row(order)
    score = score_row(row)
    effects = []
    for field in order.model_dump():
        alt = dict(row)
        for f in GROUPS.get(field, [field]):
            alt[f] = "unknown" if f in CAT_COLS else DEFAULTS[f]
        effects.append({"factor": field, "value": row[field],
                        "effect": round(score - score_row(alt), 3)})
    effects.sort(key=lambda e: abs(e["effect"]), reverse=True)
    return {"risk_score": round(score, 3), "flagged": score >= THRESHOLD,
            "top_factors": effects[:5]}

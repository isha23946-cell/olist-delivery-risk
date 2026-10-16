import json
import joblib
import duckdb
import pandas as pd

from data import FEATURES, load_split

model = joblib.load("models/late_delivery_model.joblib")
threshold = json.load(open("models/threshold.json"))["threshold"]

train, test = load_split()
cut = int(len(train) * 0.85)
parts = [train.iloc[:cut].assign(split="train"),
         train.iloc[cut:].assign(split="validation"),
         test.assign(split="test")]
df = pd.concat(parts, ignore_index=True)
df["risk_score"] = model.predict_proba(df[FEATURES])[:, 1]
df["flagged"] = (df["risk_score"] >= threshold).astype(int)

cols = ["order_id", "purchased_at", "split", "is_late", "risk_score", "flagged",
        "customer_state", "seller_state", "primary_category", "estimated_days",
        "distance_km", "items_price", "items_freight"]
out = df[cols]

con = duckdb.connect("warehouse/olist.duckdb")
con.register("out_df", out)
con.execute("CREATE OR REPLACE TABLE order_risk_scores AS SELECT * FROM out_df")
print(con.execute("""
    select split, count(*) as orders, round(avg(is_late), 4) as late_rate,
           round(avg(flagged), 4) as flagged_share
    from order_risk_scores group by split order by split
""").df())
con.close()

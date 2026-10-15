import duckdb
import pandas as pd

con = duckdb.connect("warehouse/olist.duckdb", read_only=True)
df = con.execute("""
    select f.*, h.seller_prev_orders, h.seller_prev_late_rate
    from features_orders f
    join seller_history h on f.order_id = h.order_id
""").df()
con.close()

df["is_late"] = df["is_late"].astype(int)
df = df.sort_values("purchased_at").reset_index(drop=True)
cut = int(len(df) * 0.8)
train, test = df.iloc[:cut], df.iloc[cut:]

print("train:", len(train), "late rate", round(train.is_late.mean(), 4))
print("test:", len(test), "late rate", round(test.is_late.mean(), 4))
print("train period:", train.purchased_at.min(), "to", train.purchased_at.max())
print("test period:", test.purchased_at.min(), "to", test.purchased_at.max())

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

num_cols = ["n_items", "n_sellers", "items_price", "items_freight", "freight_ratio",
            "total_weight_g", "total_volume_cm3", "estimated_days", "purchase_month",
            "purchase_weekday", "purchase_hour", "approval_hours", "distance_km",
            "same_state", "max_installments", "seller_prev_orders", "seller_prev_late_rate"]
cat_cols = ["primary_payment_type", "seller_state", "customer_state", "primary_category"]

pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)),
                      ("sc", StandardScaler())]), num_cols),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="missing")),
                      ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=50))]), cat_cols),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))])

features = num_cols + cat_cols
model.fit(train[features], train["is_late"])
proba = model.predict_proba(test[features])[:, 1]
pred = (proba >= 0.5).astype(int)

print("\n--- Baseline: logistic regression ---")
print("no-skill PR-AUC (late rate):", round(test.is_late.mean(), 4))
print("PR-AUC:", round(average_precision_score(test["is_late"], proba), 4))
print("ROC-AUC:", round(roc_auc_score(test["is_late"], proba), 4))
print("precision @0.5:", round(precision_score(test["is_late"], pred), 4))
print("recall @0.5:", round(recall_score(test["is_late"], pred), 4))
print("confusion matrix [[TN, FP], [FN, TP]]:")
print(confusion_matrix(test["is_late"], pred))

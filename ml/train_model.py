from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from data import CAT_COLS, FEATURES, load_split

train, test = load_split()
cut = int(len(train) * 0.85)
fit_df, val_df = train.iloc[:cut], train.iloc[cut:]

pre = ColumnTransformer(
    [("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                            encoded_missing_value=-1), CAT_COLS)],
    remainder="passthrough",
)
model = Pipeline([
    ("pre", pre),
    ("clf", HistGradientBoostingClassifier(
        learning_rate=0.05, max_iter=300, max_leaf_nodes=15, min_samples_leaf=50,
        l2_regularization=1.0, class_weight="balanced",
        categorical_features=list(range(len(CAT_COLS))), random_state=42)),
])

model.fit(fit_df[FEATURES], fit_df["is_late"])
proba_test = model.predict_proba(test[FEATURES])[:, 1]

print("--- Gradient boosting ---")
print("no-skill PR-AUC:", round(test.is_late.mean(), 4))
print("PR-AUC:", round(average_precision_score(test["is_late"], proba_test), 4), "(baseline 0.1073)")
print("ROC-AUC:", round(roc_auc_score(test["is_late"], proba_test), 4), "(baseline 0.7118)")

import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_curve, precision_score, recall_score

proba_val = model.predict_proba(val_df[FEATURES])[:, 1]
prec, rec, thr = precision_recall_curve(val_df["is_late"], proba_val)
ok = np.where(rec[:-1] >= 0.5)[0]
threshold = float(thr[ok[-1]])

pred = (proba_test >= threshold).astype(int)
print("\n--- Threshold chosen on validation (recall >= 0.5) ---")
print("threshold:", round(threshold, 4))
print("test precision:", round(precision_score(test["is_late"], pred), 4))
print("test recall:", round(recall_score(test["is_late"], pred), 4))
print("share of orders flagged:", round(pred.mean(), 4))
print(confusion_matrix(test["is_late"], pred))

import json
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

Path("models").mkdir(exist_ok=True)
Path("images").mkdir(exist_ok=True)
joblib.dump(model, "models/late_delivery_model.joblib")
json.dump({"threshold": threshold}, open("models/threshold.json", "w"))

p, r, _ = precision_recall_curve(test["is_late"], proba_test)
plt.figure(figsize=(6, 4))
plt.plot(r, p, label="Gradient boosting")
plt.axhline(test["is_late"].mean(), color="gray", linestyle="--", label="No skill")
plt.scatter([recall_score(test["is_late"], pred)], [precision_score(test["is_late"], pred)],
            color="red", zorder=5, label="Chosen threshold")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-recall (test set)")
plt.legend()
plt.tight_layout()
plt.savefig("images/pr_curve.png", dpi=150)
print("saved model and chart")

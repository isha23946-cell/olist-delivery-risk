import joblib
import numpy as np
import pandas as pd
import shap

from data import CAT_COLS, FEATURES, NUM_COLS, load_split

model = joblib.load("models/late_delivery_model.joblib")
pre = model.named_steps["pre"]
clf = model.named_steps["clf"]
names = CAT_COLS + NUM_COLS

train, test = load_split()
background = pre.transform(train[FEATURES].sample(50, random_state=0))
sample = pre.transform(test[FEATURES].sample(200, random_state=0))


def predict(x):
    return clf.predict_proba(x)[:, 1]


explainer = shap.Explainer(predict, background, feature_names=names)
sv = explainer(sample, max_evals=200)

mean_abs = pd.Series(np.abs(sv.values).mean(axis=0), index=names).sort_values(ascending=False)
print("Top factors (mean absolute SHAP, in probability points):")
print(mean_abs.head(10).round(4))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

top = mean_abs.head(10)[::-1]
plt.figure(figsize=(7, 4))
plt.barh(top.index, top.values)
plt.xlabel("Mean absolute SHAP (probability points)")
plt.title("Top factors behind late-delivery risk")
plt.tight_layout()
plt.savefig("images/shap_top_factors.png", dpi=150)

raw = test[FEATURES].sample(200, random_state=0).reset_index(drop=True)
scores = predict(sample)
i = int(np.argmax(scores))
print("\nHighest-risk sampled order, predicted risk:", round(float(scores[i]), 3))
contrib = pd.Series(sv.values[i], index=names).sort_values(key=np.abs, ascending=False).head(5)
for f, v in contrib.items():
    print(f, "=", raw.loc[i, f], "| effect:", round(float(v), 3))

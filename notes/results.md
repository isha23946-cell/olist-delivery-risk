# Model results

## Setup
- Target: is_late (delivered after the estimated date), delivered orders only
- Time-based split: train 77,180 orders (Sep 2016 to May 2018, 8.8% late), test 19,296 orders (May to Aug 2018, 5.3% late)
- Seller history feature uses only orders delivered before each purchase (no future information)

## Baseline: logistic regression (class_weight balanced)
- PR-AUC 0.107 (no-skill level 0.053)
- ROC-AUC 0.712
- At threshold 0.5: precision 0.087, recall 0.819 (836 of 1,021 late orders caught, 8,808 false alarms)

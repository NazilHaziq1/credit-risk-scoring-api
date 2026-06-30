# Model Card: Credit Default Risk Classifier

## Model Details
- **Architecture:** XGBoost gradient-boosted trees
- **Task:** Binary classification — predict probability of serious delinquency (90+ days late) within 2 years
- **Training data:** Kaggle "Give Me Some Credit" (~150k US consumer loan applicants, anonymised)
- **Features:** 10 (utilisation ratio, age, delinquency history counts, debt ratio, monthly income, open credit lines, real estate loans, dependents)
- **Output:** Probability in [0, 1]; threshold at 0.5 maps to binary flag

## Intended Use
Portfolio / demonstration only. Not intended for any real lending decision.

## Performance
| Metric | Value |
|---|---|
| AUC-ROC | ~0.86–0.87 (expected; update after training) |
| Average Precision | ~0.48–0.52 |

AUC-ROC measures discrimination across all thresholds. Average Precision (area under the precision-recall curve) is the primary metric here because the positive rate is only ~6.7% — a model predicting "no default" for everyone achieves 93% accuracy while being completely useless.

## Class Imbalance Handling
`scale_pos_weight` is set to `(# negatives) / (# positives)` ≈ 14. This reweights the XGBoost loss function so the minority class (defaults) is treated with proportional importance during training.

## Data Preprocessing
- **MonthlyIncome:** Imputed with median grouped by age bracket (20s, 30s, 40s, 50s, 60+). Bracket median is preferred over global median because income increases with age through most of working life.
- **NumberOfDependents:** Imputed with 0 (the mode across all age groups).
- **Utilisation ratio:** Clipped to [0, 1]; values above 1 represent over-limit cards, which carry the same signal.
- **Age:** Clipped to [18, 100] to remove data entry errors (age=0).
- **DebtRatio:** Clipped at 99th percentile to reduce effect of extreme outliers.
- **Delinquency counts:** Clipped at 15 — values above this are indistinguishable from "chronic".

## Limitations

### Proxy Dataset
This dataset is from a Kaggle competition (~2011 US data). It is not representative of any specific lender's population, time period, or geography. Real credit models are trained on proprietary, continuously updated data.

### Potential Fairness Issues
The feature set includes `MonthlyIncome` and `NumberOfDependents`, which may correlate with protected attributes (gender, race, family status). Disparate impact analysis has not been performed. **Do not use for any real credit decision.**

### Missing Context
No bureau data, employment type, loan purpose, or loan-to-value ratio — variables that real underwriting models rely on heavily. The model's discrimination ability is therefore a ceiling, not a floor, for production systems.

### Static Model
There is no model monitoring, retraining pipeline, or drift detection. Model degradation over time is expected in any deployment.

## Ethical Considerations
Credit scoring directly affects people's access to financial products. Even portfolio/demo models should be understood in this context. Key concerns:
- Feedback loops: deploying a biased model creates biased outcomes which feed back into future training data.
- Explainability obligation: lenders in many jurisdictions are legally required to give applicants adverse-action reasons. This model's SHAP integration addresses the technical side; the legal side requires much more.
- This demo uses SHAP to surface the *model's* reasoning, not an *objective* measure of creditworthiness.

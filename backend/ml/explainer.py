"""
Phase 2: SHAP explainability layer.

Provides:
  - load_model_and_explainer()  — loads XGBoost model + builds TreeExplainer
  - explain_prediction()        — per-applicant risk score + top SHAP factors
  - plot_global_importance()    — saves a global feature importance PNG

Usage:
    from backend.ml.explainer import load_model_and_explainer, explain_prediction
    model, explainer = load_model_and_explainer()
    result = explain_prediction(model, explainer, applicant_features_dict)
"""

import json
import pathlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
import shap

MODEL_DIR = pathlib.Path(__file__).parent

# Human-readable labels for the API/frontend
FEATURE_LABELS = {
    "credit_limit":    "Credit Limit",
    "sex":             "Sex",
    "education":       "Education Level",
    "marriage":        "Marital Status",
    "age":             "Age",
    "pay_0":           "Repayment Status (Sep)",
    "pay_2":           "Repayment Status (Aug)",
    "pay_3":           "Repayment Status (Jul)",
    "pay_4":           "Repayment Status (Jun)",
    "pay_5":           "Repayment Status (May)",
    "pay_6":           "Repayment Status (Apr)",
    "bill_amt1":       "Bill Amount (Sep)",
    "bill_amt2":       "Bill Amount (Aug)",
    "bill_amt3":       "Bill Amount (Jul)",
    "bill_amt4":       "Bill Amount (Jun)",
    "bill_amt5":       "Bill Amount (May)",
    "bill_amt6":       "Bill Amount (Apr)",
    "pay_amt1":        "Payment Made (Sep)",
    "pay_amt2":        "Payment Made (Aug)",
    "pay_amt3":        "Payment Made (Jul)",
    "pay_amt4":        "Payment Made (Jun)",
    "pay_amt5":        "Payment Made (May)",
    "pay_amt6":        "Payment Made (Apr)",
}


@dataclass
class SHAPFactor:
    feature: str          # raw feature name
    label: str            # human-readable label
    value: float          # applicant's actual value for this feature
    shap_value: float     # SHAP contribution (positive = increases default risk)
    direction: str        # "increases_risk" | "decreases_risk"


@dataclass
class PredictionExplanation:
    risk_score: float           # probability of default [0, 1]
    risk_label: str             # "Low" | "Medium" | "High"
    top_factors: list[SHAPFactor]
    base_value: float           # model's average prediction (log-odds)
    all_shap_values: dict       # full map of feature → shap_value (for storage)


def load_model_and_explainer():
    """Load trained XGBoost model and build SHAP TreeExplainer."""
    import xgboost as xgb

    model_path = MODEL_DIR / "model.ubj"
    feature_path = MODEL_DIR / "feature_names.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run backend/ml/train.py first."
        )

    model = xgb.XGBClassifier()
    model.load_model(model_path)

    with open(feature_path) as f:
        feature_names = json.load(f)

    # TreeExplainer is exact (not approximate) for tree models — fast and consistent.
    # model_output="raw" gives SHAP values in log-odds space. Probability-space output
    # requires a background dataset (interventional perturbation) which adds ~100ms per call.
    # For explaining direction and relative magnitude, log-odds is sufficient.
    explainer = shap.TreeExplainer(
        model,
        feature_names=feature_names,
    )

    return model, explainer, feature_names


def explain_prediction(
    model,
    explainer: shap.TreeExplainer,
    feature_names: list[str],
    applicant: dict,
    top_n: int = 5,
) -> PredictionExplanation:
    """
    Score one applicant and return risk probability + top SHAP factors.

    applicant: dict mapping feature name → value (all 23 features required)
    top_n: how many factors to surface (3–5 recommended for UI)
    """
    df = pd.DataFrame([applicant])[feature_names]

    # Risk score: probability of default
    risk_score = float(model.predict_proba(df)[0, 1])

    if risk_score < 0.3:
        risk_label = "Low"
    elif risk_score < 0.6:
        risk_label = "Medium"
    else:
        risk_label = "High"

    # SHAP explanation — returns Explanation object with .values shape (1, n_features)
    shap_explanation = explainer(df)
    shap_values = shap_explanation.values[0]        # shape: (n_features,)
    base_value = float(shap_explanation.base_values[0])

    # Build factor list sorted by absolute SHAP value (most impactful first)
    factors = []
    for i, feat in enumerate(feature_names):
        sv = float(shap_values[i])
        factors.append(
            SHAPFactor(
                feature=feat,
                label=FEATURE_LABELS.get(feat, feat),
                value=float(df[feat].iloc[0]),
                shap_value=sv,
                direction="increases_risk" if sv > 0 else "decreases_risk",
            )
        )

    factors.sort(key=lambda f: abs(f.shap_value), reverse=True)

    all_shap = {f.feature: f.shap_value for f in factors}

    return PredictionExplanation(
        risk_score=risk_score,
        risk_label=risk_label,
        top_factors=factors[:top_n],
        base_value=base_value,
        all_shap_values=all_shap,
    )


def plot_global_importance(
    explainer: shap.TreeExplainer,
    feature_names: list[str],
    sample_data: pd.DataFrame,
    out_path: pathlib.Path = None,
) -> pathlib.Path:
    """
    Compute SHAP values over a sample of the training data and save a
    beeswarm summary plot (shows both magnitude and direction per feature).

    sample_data: DataFrame with columns matching feature_names (use test set)
    """
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend for server-side rendering
    import matplotlib.pyplot as plt

    if out_path is None:
        out_path = MODEL_DIR / "global_importance.png"

    # Sample up to 500 rows — enough for a stable global importance estimate
    sample = sample_data[feature_names].sample(
        n=min(500, len(sample_data)), random_state=42
    )

    shap_vals = explainer(sample)

    # Rename for display
    shap_vals.feature_names = [FEATURE_LABELS.get(f, f) for f in feature_names]

    plt.figure(figsize=(10, 7))
    shap.plots.beeswarm(shap_vals, max_display=15, show=False)
    plt.title("Global Feature Importance (SHAP beeswarm)", fontsize=13, pad=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Global importance plot saved → {out_path}")
    return out_path


if __name__ == "__main__":
    # Quick smoke test using a synthetic applicant
    import pandas as pd

    model, explainer, feature_names = load_model_and_explainer()

    test_applicant = {
        "credit_limit": 20000,
        "sex": 2,
        "education": 2,
        "marriage": 1,
        "age": 35,
        "pay_0": 2,    # 2 months late in Sep
        "pay_2": 0,
        "pay_3": 0,
        "pay_4": 0,
        "pay_5": 0,
        "pay_6": 0,
        "bill_amt1": 18000,
        "bill_amt2": 16000,
        "bill_amt3": 14000,
        "bill_amt4": 12000,
        "bill_amt5": 10000,
        "bill_amt6": 8000,
        "pay_amt1": 500,
        "pay_amt2": 500,
        "pay_amt3": 500,
        "pay_amt4": 500,
        "pay_amt5": 500,
        "pay_amt6": 500,
    }

    result = explain_prediction(model, explainer, feature_names, test_applicant)

    print(f"\nRisk Score: {result.risk_score:.3f}  ({result.risk_label})")
    print(f"Base value: {result.base_value:.3f}")
    print("\nTop contributing factors:")
    for f in result.top_factors:
        arrow = "▲" if f.direction == "increases_risk" else "▼"
        print(f"  {arrow} {f.label:<30} value={f.value:>10.1f}  SHAP={f.shap_value:+.4f}")

    # Generate global importance plot from test set
    test_df = pd.read_csv(
        pathlib.Path(__file__).resolve().parents[2] / "data" / "processed" / "test_clean.csv"
    )
    plot_global_importance(explainer, feature_names, test_df)

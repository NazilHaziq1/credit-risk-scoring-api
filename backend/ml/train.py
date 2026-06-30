"""
Phase 1: Data cleaning, feature engineering, and XGBoost training.

Dataset: UCI "Default of Credit Card Clients" (Taiwan, 2005)
  30,000 credit card holders, binary target = default payment next month.
  No missing values — but outliers and categorical encoding need attention.

Run from project root:
    python -m backend.ml.train

Expects: data/raw/default of credit card clients.xls  (from UCI zip)
Outputs: backend/ml/model.ubj
         backend/ml/feature_names.json
         data/processed/train_clean.csv
         data/processed/test_clean.csv
"""

import json
import pathlib
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, average_precision_score
import xgboost as xgb

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
MODEL_DIR = pathlib.Path(__file__).parent

TARGET_COL = "default_payment"

# The 23 features we keep after renaming (drop ID)
FEATURE_COLS = [
    "credit_limit",
    "sex",               # 1=male, 2=female
    "education",         # 1=grad, 2=university, 3=high school, 4=other
    "marriage",          # 1=married, 2=single, 3=other
    "age",
    "pay_0",             # repayment status Sep (-2=no consumption, -1=paid duly, 0=minimum paid, 1..8=months late)
    "pay_2",
    "pay_3",
    "pay_4",
    "pay_5",
    "pay_6",
    "bill_amt1",         # bill statement amount Sep (NTD)
    "bill_amt2",
    "bill_amt3",
    "bill_amt4",
    "bill_amt5",
    "bill_amt6",
    "pay_amt1",          # previous payment amount Sep (NTD)
    "pay_amt2",
    "pay_amt3",
    "pay_amt4",
    "pay_amt5",
    "pay_amt6",
]

RENAME_MAP = {
    "LIMIT_BAL": "credit_limit",
    "SEX": "sex",
    "EDUCATION": "education",
    "MARRIAGE": "marriage",
    "AGE": "age",
    "PAY_0": "pay_0",
    "PAY_2": "pay_2",
    "PAY_3": "pay_3",
    "PAY_4": "pay_4",
    "PAY_5": "pay_5",
    "PAY_6": "pay_6",
    "BILL_AMT1": "bill_amt1",
    "BILL_AMT2": "bill_amt2",
    "BILL_AMT3": "bill_amt3",
    "BILL_AMT4": "bill_amt4",
    "BILL_AMT5": "bill_amt5",
    "BILL_AMT6": "bill_amt6",
    "PAY_AMT1": "pay_amt1",
    "PAY_AMT2": "pay_amt2",
    "PAY_AMT3": "pay_amt3",
    "PAY_AMT4": "pay_amt4",
    "PAY_AMT5": "pay_amt5",
    "PAY_AMT6": "pay_amt6",
    "default payment next month": "default_payment",
}


def find_raw_file() -> pathlib.Path:
    candidates = [
        RAW_DIR / "default of credit card clients.xls",
        RAW_DIR / "default_of_credit_card_clients.xls",
        RAW_DIR / "UCI_Credit_Card.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    # also check any .xls in raw dir
    xls_files = list(RAW_DIR.glob("*.xls")) + list(RAW_DIR.glob("*.xlsx"))
    if xls_files:
        return xls_files[0]
    return None


def load_raw(path: pathlib.Path) -> pd.DataFrame:
    print(f"Loading {path.name} ...")
    if path.suffix in (".xls", ".xlsx"):
        # Row 0 is a descriptive header ("X1", "X2" etc.); real column names are row 1
        df = pd.read_excel(path, header=1, index_col=0)
    else:
        df = pd.read_csv(path, index_col=0)

    df = df.rename(columns=RENAME_MAP)
    print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
    print(f"Target distribution:\n{df[TARGET_COL].value_counts()}\n")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Fix undocumented categorical values ---
    # EDUCATION: codebook says 1-4, but dataset has 0, 5, 6 (undocumented → lump into "other")
    df["education"] = df["education"].replace({0: 4, 5: 4, 6: 4})

    # MARRIAGE: codebook says 1-3, but 0 appears → lump into "other" (3)
    df["marriage"] = df["marriage"].replace({0: 3})

    # PAY_* columns: -2 means "no consumption" (not in the original codebook but present)
    # Keep as-is — XGBoost handles arbitrary integer codes fine; -2 is meaningfully different
    # from -1 (paid duly) or 0 (revolving credit used), so don't collapse them.

    # --- Clip extreme outliers ---
    # Bill and payment amounts: clip at 99.9th percentile to reduce leverage of extreme values
    for col in [c for c in FEATURE_COLS if c.startswith("bill_amt") or c.startswith("pay_amt")]:
        upper = df[col].quantile(0.999)
        df[col] = df[col].clip(upper=upper)

    # Age: dataset range is 21-79, looks clean — no clip needed
    # Credit limit: clip at 99.9th percentile
    df["credit_limit"] = df["credit_limit"].clip(upper=df["credit_limit"].quantile(0.999))

    print(f"Missing values after cleaning: {df[FEATURE_COLS + [TARGET_COL]].isnull().sum().sum()}")
    return df


def split_and_save(df: pd.DataFrame):
    X = df[FEATURE_COLS]
    y = df[TARGET_COL].astype(int)

    # Stratified split preserves the ~22% positive rate in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_df = X_train.copy(); train_df[TARGET_COL] = y_train
    test_df = X_test.copy(); test_df[TARGET_COL] = y_test
    train_df.to_csv(PROCESSED_DIR / "train_clean.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test_clean.csv", index=False)

    print(f"Train: {len(train_df):,} rows | Test: {len(test_df):,} rows")
    print(f"Positive rate — Train: {y_train.mean():.3f} | Test: {y_test.mean():.3f}\n")
    return X_train, X_test, y_train, y_test


def compute_scale_pos_weight(y_train: pd.Series) -> float:
    # XGBoost's scale_pos_weight = (# negatives) / (# positives).
    # This reweights the loss so the minority class (defaults) contributes proportionally.
    # Without it, the model learns to always predict "no default" and achieves ~78% accuracy
    # on this dataset while being useless — accuracy is misleading with class imbalance.
    neg = (y_train == 0).sum()
    pos = (y_train == 1).sum()
    spw = neg / pos
    print(f"Class distribution — Negative: {neg:,} | Positive: {pos:,}")
    print(f"scale_pos_weight = {spw:.2f}\n")
    return spw


def train_model(X_train, y_train, scale_pos_weight: float) -> xgb.XGBClassifier:
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
    )

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        early_stopping_rounds=30,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=50)
    print(f"\nBest iteration: {model.best_iteration}")
    return model


def evaluate(model, X_test, y_test):
    # Primary metrics: AUC-ROC and Average Precision (area under PR curve).
    # NOT accuracy — with ~22% positives, a naive "never default" model gets 78% accuracy
    # but has zero recall on the class that actually matters for a lender.
    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, proba)
    ap = average_precision_score(y_test, proba)

    print("=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    print(f"AUC-ROC:           {auc:.4f}")
    print(f"Average Precision: {ap:.4f}  (area under PR curve)")
    print()
    print("Classification report (threshold=0.5):")
    print(classification_report(y_test, preds, target_names=["No Default", "Default"]))
    print("=" * 50)
    return auc, ap


def save_model(model: xgb.XGBClassifier):
    model_path = MODEL_DIR / "model.ubj"
    feature_path = MODEL_DIR / "feature_names.json"
    model.save_model(model_path)
    with open(feature_path, "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)
    size_mb = model_path.stat().st_size / 1_048_576
    print(f"\nModel saved → {model_path} ({size_mb:.2f} MB)")


def main():
    raw_path = find_raw_file()
    if raw_path is None:
        print(f"ERROR: No raw data file found in {RAW_DIR}")
        print("Expected: 'default of credit card clients.xls' (extracted from UCI zip)")
        sys.exit(1)

    df = load_raw(raw_path)
    df = clean(df)
    X_train, X_test, y_train, y_test = split_and_save(df)

    spw = compute_scale_pos_weight(y_train)
    model = train_model(X_train, y_train, spw)
    auc, ap = evaluate(model, X_test, y_test)
    save_model(model)

    print("\nPhase 1 complete.")
    return auc, ap


if __name__ == "__main__":
    main()

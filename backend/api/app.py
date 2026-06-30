"""FastAPI application — model and DB pool are loaded once at startup."""

import pathlib
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import predict as predict_router
from backend.api.routes import model as model_router
from backend.db.database import close_pool, create_pool
from backend.ml.explainer import load_model_and_explainer

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEST_CSV = ROOT / "data" / "processed" / "test_clean.csv"


def _compute_global_importance(explainer, feature_names: list[str], n_samples: int = 500) -> list[dict]:
    """Mean |SHAP| over a sample of the test set, sorted descending."""
    test_df = pd.read_csv(TEST_CSV)[feature_names].sample(n=n_samples, random_state=42)
    shap_vals = explainer(test_df).values  # shape: (n_samples, n_features)
    mean_abs = np.abs(shap_vals).mean(axis=0)
    items = [
        {"feature": f, "mean_abs_shap": float(v)}
        for f, v in zip(feature_names, mean_abs)
    ]
    return sorted(items, key=lambda x: x["mean_abs_shap"], reverse=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Loading model and explainer...")
    model, explainer, feature_names = load_model_and_explainer()
    app.state.model = model
    app.state.explainer = explainer
    app.state.feature_names = feature_names

    print("Precomputing global feature importance...")
    app.state.global_importance = _compute_global_importance(explainer, feature_names)

    print("Connecting to database...")
    await create_pool()

    print("Ready.")
    yield

    # Shutdown
    await close_pool()


app = FastAPI(
    title="Credit Risk Scoring API",
    description="XGBoost + SHAP credit default prediction with plain-English explanations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router.router)
app.include_router(model_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

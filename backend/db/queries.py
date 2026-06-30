"""Typed asyncpg query functions — one function per DB operation."""

import json
from datetime import datetime

import asyncpg

from backend.db.database import get_pool


async def insert_prediction(
    features: dict,
    risk_score: float,
    risk_label: str,
    shap_factors: list[dict],
    all_shap_values: dict,
    llm_explanation: str | None = None,
) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO predictions
            (features, risk_score, risk_label, shap_factors, all_shap_values, llm_explanation)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at
        """,
        json.dumps(features),
        risk_score,
        risk_label,
        json.dumps(shap_factors),
        json.dumps(all_shap_values),
        llm_explanation,
    )
    return dict(row)


async def get_prediction(prediction_id: int) -> dict | None:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        SELECT id, created_at, features, risk_score, risk_label,
               shap_factors, llm_explanation
        FROM predictions
        WHERE id = $1
        """,
        prediction_id,
    )
    if row is None:
        return None
    r = dict(row)
    r["features"] = json.loads(r["features"])
    r["shap_factors"] = json.loads(r["shap_factors"])
    return r


async def update_llm_explanation(prediction_id: int, explanation: str) -> None:
    pool = get_pool()
    await pool.execute(
        "UPDATE predictions SET llm_explanation = $1 WHERE id = $2",
        explanation,
        prediction_id,
    )

"""POST /predict and GET /predictions/{id}"""

import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request

from backend.api.schemas import ApplicantFeatures, PredictResponse, PredictionRecord, SHAPFactorOut
from backend.db import queries
from backend.ml.explainer import explain_prediction
from backend.ml.narrator import narrate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictResponse, status_code=201)
async def predict(request: Request, body: ApplicantFeatures):
    model = request.app.state.model
    explainer = request.app.state.explainer
    feature_names = request.app.state.feature_names

    features = body.to_feature_dict()
    explanation = explain_prediction(model, explainer, feature_names, features)

    shap_factors_serialisable = [asdict(f) for f in explanation.top_factors]

    # Get LLM explanation — if Groq is unavailable, degrade gracefully
    llm_explanation: str | None = None
    try:
        llm_explanation = await narrate(
            risk_score=explanation.risk_score,
            risk_label=explanation.risk_label,
            top_factors=explanation.top_factors,
        )
    except Exception as exc:
        logger.warning("LLM narration failed: %s", exc)

    row = await queries.insert_prediction(
        features=features,
        risk_score=explanation.risk_score,
        risk_label=explanation.risk_label,
        shap_factors=shap_factors_serialisable,
        all_shap_values=explanation.all_shap_values,
        llm_explanation=llm_explanation,
    )

    return PredictResponse(
        id=row["id"],
        created_at=row["created_at"],
        risk_score=explanation.risk_score,
        risk_label=explanation.risk_label,
        top_factors=[SHAPFactorOut(**f) for f in shap_factors_serialisable],
        llm_explanation=llm_explanation,
    )


@router.get("/predictions/{prediction_id}", response_model=PredictionRecord)
async def get_prediction(prediction_id: int):
    row = await queries.get_prediction(prediction_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return PredictionRecord(
        id=row["id"],
        created_at=row["created_at"],
        risk_score=row["risk_score"],
        risk_label=row["risk_label"],
        top_factors=[SHAPFactorOut(**f) for f in row["shap_factors"]],
        llm_explanation=row["llm_explanation"],
        features=ApplicantFeatures(**row["features"]),
    )

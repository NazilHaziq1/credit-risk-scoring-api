"""GET /model/feature-importance — global SHAP importance as JSON for Recharts."""

from fastapi import APIRouter, Request

from backend.api.schemas import FeatureImportanceItem, FeatureImportanceResponse
from backend.ml.explainer import FEATURE_LABELS

router = APIRouter()


@router.get("/model/feature-importance", response_model=FeatureImportanceResponse)
async def feature_importance(request: Request):
    # Precomputed at startup in app.py lifespan; shape: list of (feature, mean_abs_shap)
    importance = request.app.state.global_importance
    return FeatureImportanceResponse(
        features=[
            FeatureImportanceItem(
                feature=item["feature"],
                label=FEATURE_LABELS.get(item["feature"], item["feature"]),
                mean_abs_shap=item["mean_abs_shap"],
            )
            for item in importance
        ]
    )

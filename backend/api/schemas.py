"""Pydantic request/response schemas for the API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ApplicantFeatures(BaseModel):
    """23 features from the UCI credit card default dataset."""

    credit_limit: float = Field(..., gt=0, description="Credit limit in NTD")
    sex: Literal[1, 2] = Field(..., description="1=male, 2=female")
    education: Literal[1, 2, 3, 4] = Field(..., description="1=grad school, 2=university, 3=high school, 4=other")
    marriage: Literal[1, 2, 3] = Field(..., description="1=married, 2=single, 3=other")
    age: int = Field(..., ge=18, le=100)

    # Repayment status: -2=no consumption, -1=paid duly, 0=revolving credit,
    # 1–8 = months late
    pay_0: int = Field(..., ge=-2, le=8, description="Repayment status Sep")
    pay_2: int = Field(..., ge=-2, le=8, description="Repayment status Aug")
    pay_3: int = Field(..., ge=-2, le=8, description="Repayment status Jul")
    pay_4: int = Field(..., ge=-2, le=8, description="Repayment status Jun")
    pay_5: int = Field(..., ge=-2, le=8, description="Repayment status May")
    pay_6: int = Field(..., ge=-2, le=8, description="Repayment status Apr")

    # Bill statement amounts (NTD) — can be negative (credit balance)
    bill_amt1: float = Field(..., description="Bill amount Sep (NTD)")
    bill_amt2: float = Field(..., description="Bill amount Aug (NTD)")
    bill_amt3: float = Field(..., description="Bill amount Jul (NTD)")
    bill_amt4: float = Field(..., description="Bill amount Jun (NTD)")
    bill_amt5: float = Field(..., description="Bill amount May (NTD)")
    bill_amt6: float = Field(..., description="Bill amount Apr (NTD)")

    # Previous payment amounts (NTD) — cannot be negative
    pay_amt1: float = Field(..., ge=0, description="Payment made Sep (NTD)")
    pay_amt2: float = Field(..., ge=0, description="Payment made Aug (NTD)")
    pay_amt3: float = Field(..., ge=0, description="Payment made Jul (NTD)")
    pay_amt4: float = Field(..., ge=0, description="Payment made Jun (NTD)")
    pay_amt5: float = Field(..., ge=0, description="Payment made May (NTD)")
    pay_amt6: float = Field(..., ge=0, description="Payment made Apr (NTD)")

    def to_feature_dict(self) -> dict:
        return self.model_dump()


# ---------------------------------------------------------------------------
# Response building blocks
# ---------------------------------------------------------------------------

class SHAPFactorOut(BaseModel):
    feature: str
    label: str
    value: float
    shap_value: float
    direction: Literal["increases_risk", "decreases_risk"]


class PredictResponse(BaseModel):
    id: int
    created_at: datetime
    risk_score: float
    risk_label: Literal["Low", "Medium", "High"]
    top_factors: list[SHAPFactorOut]
    llm_explanation: str | None = None


class PredictionRecord(PredictResponse):
    """Full record including stored features."""
    features: ApplicantFeatures


class FeatureImportanceItem(BaseModel):
    feature: str
    label: str
    mean_abs_shap: float


class FeatureImportanceResponse(BaseModel):
    features: list[FeatureImportanceItem]

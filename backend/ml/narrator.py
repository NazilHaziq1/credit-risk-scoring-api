"""
Phase 4: LLM narration of SHAP output via Groq/Llama 3.1.

Takes structured SHAP factors and returns 2-3 plain-English sentences
explaining the risk score. The prompt is tightly constrained so the model
can only use the provided factors — it cannot invent reasons.
"""

from groq import AsyncGroq

from backend.config import settings
from backend.ml.explainer import SHAPFactor

_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY not set in .env")
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


def _build_prompt(
    risk_score: float,
    risk_label: str,
    top_factors: list[SHAPFactor],
) -> str:
    factor_lines = []
    for f in top_factors:
        direction_phrase = "increases default risk" if f.direction == "increases_risk" else "decreases default risk"
        factor_lines.append(f"  - {f.label}: value={f.value}, this {direction_phrase} (SHAP={f.shap_value:+.3f})")
    factors_block = "\n".join(factor_lines)

    return f"""You are a credit risk analyst writing a plain-English explanation for a loan officer.

A machine learning model has assessed an applicant and produced these results:
- Risk score: {risk_score:.1%} probability of default
- Risk level: {risk_label}

The top factors driving this score are:
{factors_block}

Write exactly 2-3 sentences explaining this score to the loan officer. Rules:
1. Use ONLY the factors listed above — do not mention any other reasons.
2. Be specific: name the actual factors and whether they increase or decrease risk.
3. Write in plain English, no jargon, no bullet points.
4. Do not recommend approve or deny — just explain the score.
5. Do not start with "The applicant" — vary your opening."""


async def narrate(
    risk_score: float,
    risk_label: str,
    top_factors: list[SHAPFactor],
) -> str:
    """Call Groq/Llama 3.1 and return a plain-English explanation string."""
    client = get_client()
    prompt = _build_prompt(risk_score, risk_label, top_factors)

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,   # low temperature: factual, not creative
        max_tokens=150,    # 2-3 sentences never needs more
    )

    return response.choices[0].message.content.strip()

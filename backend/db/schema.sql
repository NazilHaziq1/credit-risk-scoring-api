-- Credit Risk Scoring API schema
-- Run once against your Postgres database:
--   psql $DATABASE_URL -f backend/db/schema.sql

CREATE TABLE IF NOT EXISTS predictions (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Raw applicant features stored as submitted
    features    JSONB NOT NULL,

    -- Model output
    risk_score  REAL NOT NULL,          -- probability [0, 1]
    risk_label  TEXT NOT NULL,          -- Low | Medium | High

    -- SHAP factors: array of {feature, label, value, shap_value, direction}
    shap_factors JSONB NOT NULL,

    -- Full SHAP map for audit / future use
    all_shap_values JSONB NOT NULL,

    -- LLM plain-English explanation (populated in Phase 4)
    llm_explanation TEXT
);

CREATE INDEX IF NOT EXISTS predictions_created_at_idx ON predictions (created_at DESC);

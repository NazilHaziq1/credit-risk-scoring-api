import { useState } from 'react'
import PredictForm from './components/PredictForm'
import RiskGauge from './components/RiskGauge'
import ShapChart from './components/ShapChart'
import Explanation from './components/Explanation'
import { predict } from './api'

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(features) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await predict(features)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '32px 16px' }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#1a1a2e' }}>
          Credit Risk Scorer
        </h1>
        <p style={{ marginTop: 6, fontSize: 14, color: '#666' }}>
          XGBoost + SHAP explainability · UCI Credit Card Default dataset ·{' '}
          <em>Portfolio demo — not for real credit decisions</em>
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: 24 }}>
        {/* Left: form */}
        <div>
          <PredictForm onSubmit={handleSubmit} loading={loading} />
          {error && (
            <div style={{
              marginTop: 12, padding: '12px 16px', background: '#ffebee',
              border: '1px solid #ef9a9a', borderRadius: 8, color: '#b71c1c', fontSize: 14,
            }}>
              Error: {error}
            </div>
          )}
        </div>

        {/* Right: results */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <RiskGauge score={result.risk_score} label={result.risk_label} />
            <ShapChart factors={result.top_factors} />
            <Explanation text={result.llm_explanation} loading={false} />
            <div style={{ fontSize: 11, color: '#999', textAlign: 'right' }}>
              Prediction #{result.id} · {new Date(result.created_at).toLocaleString()}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

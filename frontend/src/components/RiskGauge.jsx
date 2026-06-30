const COLOURS = {
  Low:    { bg: '#e8f5e9', border: '#43a047', text: '#2e7d32', badge: '#43a047' },
  Medium: { bg: '#fff8e1', border: '#fb8c00', text: '#e65100', badge: '#fb8c00' },
  High:   { bg: '#ffebee', border: '#e53935', text: '#b71c1c', badge: '#e53935' },
}

export default function RiskGauge({ score, label }) {
  const c = COLOURS[label] ?? COLOURS.Medium
  const pct = (score * 100).toFixed(1)

  return (
    <div style={{
      background: c.bg,
      border: `2px solid ${c.border}`,
      borderRadius: 12,
      padding: '24px 32px',
      display: 'flex',
      alignItems: 'center',
      gap: 24,
    }}>
      {/* Big percentage */}
      <div style={{ textAlign: 'center', minWidth: 110 }}>
        <div style={{ fontSize: 52, fontWeight: 700, color: c.text, lineHeight: 1 }}>
          {pct}%
        </div>
        <div style={{ fontSize: 12, color: c.text, marginTop: 4, opacity: 0.75 }}>
          default probability
        </div>
      </div>

      <div style={{ width: 2, height: 64, background: c.border, opacity: 0.3 }} />

      <div>
        <span style={{
          display: 'inline-block',
          background: c.badge,
          color: '#fff',
          borderRadius: 6,
          padding: '4px 14px',
          fontWeight: 700,
          fontSize: 18,
          letterSpacing: 1,
        }}>
          {label.toUpperCase()} RISK
        </span>
        <div style={{ marginTop: 8, fontSize: 13, color: c.text, opacity: 0.8 }}>
          {label === 'Low' && 'Applicant shows strong repayment indicators.'}
          {label === 'Medium' && 'Some risk factors present — review explanation below.'}
          {label === 'High' && 'Multiple elevated risk factors detected.'}
        </div>
      </div>
    </div>
  )
}

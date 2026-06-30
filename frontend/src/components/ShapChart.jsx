import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, Cell, ResponsiveContainer,
} from 'recharts'

const RED   = '#e53935'
const BLUE  = '#1e88e5'

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: '#fff', border: '1px solid #ddd',
      borderRadius: 6, padding: '8px 12px', fontSize: 13,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{d.label}</div>
      <div>Value: <strong>{d.value}</strong></div>
      <div>SHAP: <strong style={{ color: d.shap_value >= 0 ? RED : BLUE }}>
        {d.shap_value >= 0 ? '+' : ''}{d.shap_value.toFixed(4)}
      </strong></div>
      <div style={{ marginTop: 4, fontSize: 11, color: '#666' }}>
        {d.direction === 'increases_risk' ? '▲ Increases default risk' : '▼ Decreases default risk'}
      </div>
    </div>
  )
}

export default function ShapChart({ factors }) {
  // Recharts horizontal bar: largest absolute value at top
  const data = [...factors].sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))

  return (
    <div>
      <h3 style={{ marginBottom: 12, fontSize: 15, fontWeight: 600 }}>
        Contributing Factors
        <span style={{ marginLeft: 10, fontSize: 12, fontWeight: 400, color: '#666' }}>
          <span style={{ color: RED }}>■</span> increases risk &nbsp;
          <span style={{ color: BLUE }}>■</span> decreases risk
        </span>
      </h3>
      <ResponsiveContainer width="100%" height={data.length * 52 + 40}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={v => v.toFixed(2)}
            tick={{ fontSize: 12 }}
            label={{ value: 'SHAP value (log-odds)', position: 'insideBottom', offset: -2, fontSize: 12 }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={180}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={0} stroke="#333" strokeWidth={1.5} />
          <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.direction === 'increases_risk' ? RED : BLUE}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function Explanation({ text, loading }) {
  if (loading) {
    return (
      <div style={{ padding: '16px 20px', background: '#f5f5f5', borderRadius: 8, color: '#999', fontSize: 14 }}>
        Generating explanation…
      </div>
    )
  }
  if (!text) return null
  return (
    <div style={{
      padding: '16px 20px',
      background: '#fff',
      border: '1px solid #e0e0e0',
      borderLeft: '4px solid #5c6bc0',
      borderRadius: 8,
      lineHeight: 1.65,
      fontSize: 14,
      color: '#333',
    }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: '#5c6bc0', letterSpacing: 1, marginBottom: 8 }}>
        AI EXPLANATION
      </div>
      {text}
    </div>
  )
}

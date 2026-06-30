const BASE = ''  // proxied through Vite to localhost:8000

export async function predict(features) {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(features),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getFeatureImportance() {
  const res = await fetch(`${BASE}/model/feature-importance`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

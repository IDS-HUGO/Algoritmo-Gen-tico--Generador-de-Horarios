const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchSampleData() {
  const response = await fetch(`${API_BASE}/api/sample-data`)
  if (!response.ok) {
    throw new Error('No fue posible cargar la data de ejemplo')
  }
  return response.json()
}

export async function optimizeSchedule(payload) {
  const response = await fetch(`${API_BASE}/api/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || 'No fue posible ejecutar la optimizacion')
  }

  return response.json()
}

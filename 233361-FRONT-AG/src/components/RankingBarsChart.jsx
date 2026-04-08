import { useId } from 'react'

export function RankingBarsChart({ ranking }) {
  const gradientId = useId()
  const width = 960
  const height = 380
  const padding = 42
  const topItems = (ranking || []).slice(0, 10)
  const maxValue = Math.max(1, ...topItems.map((row) => row.aptitud || 0))
  const chartWidth = width - padding * 2
  const chartHeight = height - padding * 2
  const barGap = 10
  const barWidth = topItems.length ? (chartWidth - barGap * (topItems.length - 1)) / topItems.length : chartWidth

  return (
    <section className="chart-card chart-card--bars">
      <div className="chart-card__header">
        <h3>Evolución de la población</h3>
        <div className="chart-legend">
          <span>
            <i style={{ background: '#1a73e8' }} />
            Aptitud de individuos ordenados por ranking
          </span>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg" role="img" aria-label="Evolución de la población">
        <defs>
          <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.92" />
            <stop offset="100%" stopColor="#eef4ff" stopOpacity="0.9" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width={width} height={height} rx="22" fill={`url(#${gradientId})`} />
        {[0, 25, 50, 75, 100].map((tick) => {
          const y = padding + chartHeight - (tick / 100) * chartHeight
          return <line key={tick} x1={padding} y1={y} x2={width - padding} y2={y} className="chart-grid" />
        })}
        {topItems.map((row, index) => {
          const barScore = Math.max(0, Math.min(100, (row.aptitud / maxValue) * 100))
          const barHeight = (barScore / 100) * chartHeight
          const x = padding + index * (barWidth + barGap)
          const y = padding + chartHeight - barHeight
          const color = index === 0 ? '#1a73e8' : index === topItems.length - 1 ? '#ea4335' : '#188038'
          return (
            <g key={row.posicion}>
              <rect x={x} y={y} width={barWidth} height={barHeight} rx="10" fill={color} opacity="0.9" />
              <text x={x + barWidth / 2} y={y - 8} textAnchor="middle" className="chart-value-label">
                {row.aptitud.toFixed(4)}
              </text>
              <text x={x + barWidth / 2} y={height - 14} textAnchor="middle" className="chart-axis-label chart-axis-label--small">
                #{row.posicion}
              </text>
            </g>
          )
        })}
      </svg>
    </section>
  )
}

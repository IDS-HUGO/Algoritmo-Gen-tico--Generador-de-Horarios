import { useId } from 'react'

function scalePoints(points, width, height, padding) {
  const values = points.flatMap((series) => series.data.map((point) => point.value))
  if (!points.length || values.length === 0) {
    return points.map((series) => ({ ...series, path: '', dots: [] }))
  }
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const maxIndex = Math.max(1, ...points[0].data.map((point) => point.index))
  const range = maxValue - minValue || 1
  const innerWidth = width - padding * 2
  const innerHeight = height - padding * 2

  return points.map((series) => ({
    ...series,
    path: series.data
      .map((point, index) => {
        const x = padding + (point.index / maxIndex) * innerWidth
        const y = padding + innerHeight - ((point.value - minValue) / range) * innerHeight
        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
      })
      .join(' '),
    dots: series.data.map((point) => {
      const x = padding + (point.index / maxIndex) * innerWidth
      const y = padding + innerHeight - ((point.value - minValue) / range) * innerHeight
      return { x, y, value: point.value, index: point.index }
    }),
  }))
}

export function LineChart({ title, history, bestGeneration }) {
  const gradientId = useId()
  const width = 900
  const height = 360
  const padding = 40
  const toCost = (value) => 1 / (Number(value || 0) + 0.000001)
  const series = [
    {
      name: 'Mayor costo vs generación',
      color: '#ea4335',
      data: history.map((item) => ({ index: item.generacion - 1, value: toCost(item.peor) })),
    },
    {
      name: 'Costo promedio vs generación',
      color: '#188038',
      data: history.map((item) => ({ index: item.generacion - 1, value: toCost(item.promedio) })),
    },
    {
      name: 'Menor costo vs generación',
      color: '#1a73e8',
      data: history.map((item) => ({ index: item.generacion - 1, value: toCost(item.mejor) })),
    },
  ]
  const plotted = scalePoints(series, width, height, padding)
  const bestSeries = plotted[2]?.dots || []
  const bestPoint =
    bestGeneration && bestGeneration >= 1 && bestSeries[bestGeneration - 1]
      ? bestSeries[bestGeneration - 1]
      : null

  return (
    <section className="chart-card">
      <div className="chart-card__header">
        <h3>{title}</h3>
        <div className="chart-legend">
          {series.map((item) => (
            <span key={item.name}>
              <i style={{ background: item.color }} />
              {item.name}
            </span>
          ))}
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg" role="img" aria-label={title}>
        <defs>
          <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#eef4ff" stopOpacity="0.85" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width={width} height={height} rx="22" fill={`url(#${gradientId})`} />
        {[0, 1, 2, 3, 4].map((tick) => {
          const y = padding + ((height - padding * 2) / 4) * tick
          return <line key={tick} x1={padding} y1={y} x2={width - padding} y2={y} className="chart-grid" />
        })}
        {[0, 1, 2, 3, 4, 5, 6].map((tick) => {
          const x = padding + ((width - padding * 2) / 6) * tick
          return <line key={tick} x1={x} y1={padding} x2={x} y2={height - padding} className="chart-grid chart-grid--vertical" />
        })}
        {plotted.map((item) => (
          <g key={item.name}>
            <path d={item.path} fill="none" stroke={item.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            {item.dots.map((dot) => (
              <circle key={`${item.name}-${dot.index}`} cx={dot.x} cy={dot.y} r="3.4" fill={item.color} />
            ))}
          </g>
        ))}
        {bestPoint ? (
          <g>
            <circle cx={bestPoint.x} cy={bestPoint.y} r="7" fill="#0b57d0" stroke="#ffffff" strokeWidth="2" />
            <text x={Math.min(bestPoint.x + 12, width - 220)} y={Math.max(bestPoint.y - 12, 24)} className="chart-best-label">
              Mejor global G{bestGeneration}: {Number(bestPoint.value).toFixed(6)}
            </text>
          </g>
        ) : null}
        <text x={padding} y={height - 10} className="chart-axis-label">Generación (Ciclo Evolutivo)</text>
      </svg>
    </section>
  )
}

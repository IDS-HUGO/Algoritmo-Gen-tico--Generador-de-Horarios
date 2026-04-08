export function MetricCard({ title, value, subtitle, accent }) {
  return (
    <article className="metric-card" style={{ '--accent': accent }}>
      <div className="metric-card__title">{title}</div>
      <div className="metric-card__value">{value}</div>
      <div className="metric-card__subtitle">{subtitle}</div>
    </article>
  )
}

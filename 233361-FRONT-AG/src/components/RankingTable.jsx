export function RankingTable({ ranking }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h3>Tabla del mejor al peor individuo</h3>
        <span>Ordenada por aptitud final</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Pos</th>
              <th>Aptitud</th>
              <th>Déficit</th>
              <th>Horas extra</th>
              <th>Insatisfacción</th>
              <th>Violaciones</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((row) => (
              <tr key={row.posicion}>
                <td>{row.posicion}</td>
                <td>{row.aptitud}</td>
                <td>{row.deficit_cobertura}</td>
                <td>{row.horas_extra}</td>
                <td>{row.insatisfaccion}</td>
                <td>{row.violaciones_legales}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

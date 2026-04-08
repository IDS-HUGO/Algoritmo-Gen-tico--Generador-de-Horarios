const DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
const ETIQUETAS_DIA = {
  lunes: 'Lun',
  martes: 'Mar',
  miercoles: 'Mié',
  jueves: 'Jue',
  viernes: 'Vie',
  sabado: 'Sáb',
  domingo: 'Dom',
}

export function ScheduleTable({ schedule }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h3>Horario del perfil seleccionado</h3>
        <span>Turno por empleado y día</span>
      </div>
      <div className="table-wrap table-wrap--wide">
        <table>
          <thead>
            <tr>
              <th>Empleado</th>
              {DIAS.map((dia) => (
                <th key={dia}>{ETIQUETAS_DIA[dia]}</th>
              ))}
              <th>Horas</th>
              <th>Extra</th>
              <th>Insatisf.</th>
              <th>Legales</th>
            </tr>
          </thead>
          <tbody>
            {schedule.map((row) => (
              <tr key={row.id_empleado}>
                <td>{row.nombre_empleado}</td>
                {DIAS.map((dia) => (
                  <td key={dia}>
                    <span className={`shift-pill shift-pill--${row[dia]}`}>{row[dia]}</span>
                  </td>
                ))}
                <td>{row.horas}</td>
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

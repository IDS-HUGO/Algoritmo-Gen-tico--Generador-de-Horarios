export function CSVUploader({ onEmployeesLoaded, onDemandLoaded }) {
  const mapaDias = {
    monday: 'lunes',
    tuesday: 'martes',
    wednesday: 'miercoles',
    thursday: 'jueves',
    friday: 'viernes',
    saturday: 'sabado',
    sunday: 'domingo',
    lunes: 'lunes',
    martes: 'martes',
    miercoles: 'miercoles',
    jueves: 'jueves',
    viernes: 'viernes',
    sabado: 'sabado',
    domingo: 'domingo',
  }

  function normalizarTurno(turno) {
    const value = String(turno || '').toLowerCase().trim()
    if (['all', 'todos', 'todo'].includes(value)) return ['manana', 'tarde', 'noche', 'descanso']
    const mapped = {
      off: 'descanso',
      descanso: 'descanso',
      morning: 'manana',
      manana: 'manana',
      mañana: 'manana',
      afternoon: 'tarde',
      tarde: 'tarde',
      night: 'noche',
      noche: 'noche',
    }[value]
    return mapped ? [mapped] : [value]
  }

  function parseCSVText(text) {
    const lineas = text.trim().split('\n')
    if (lineas.length < 2) return []
    const encabezados = lineas[0].split(',').map((h) => h.trim())
    return lineas.slice(1).map((linea) => {
      const valores = linea.split(',').map((v) => v.trim())
      const fila = {}
      encabezados.forEach((encabezado, index) => {
        fila[encabezado] = valores[index]
      })
      return fila
    })
  }

  function parseEmployeesCSV(csv) {
    const rows = parseCSVText(csv)
    const employees = rows.map((row, index) => {
      const disponibilidad = {}
      const preferencias = {
        descanso: 5,
        manana: 4,
        tarde: 4,
        noche: 2,
      }

      for (const dia of ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']) {
        const diaIngles = Object.entries(mapaDias).find(([, value]) => value === dia)?.[0] || dia
        const disponibilidadCruda = row[dia] || row[diaIngles] || 'descanso'
        disponibilidad[dia] = disponibilidadCruda.includes('|')
          ? disponibilidadCruda.split('|').flatMap((part) => normalizarTurno(part))
          : normalizarTurno(disponibilidadCruda)

        if (row[`pref_${dia}`]) {
          const turnoPrincipal = disponibilidad[dia]?.find((s) => s !== 'descanso') || 'descanso'
          preferencias[turnoPrincipal] = Math.min(5, Math.max(1, parseInt(row[`pref_${dia}`]) || 3))
        }
      }

      return {
        id: index + 1,
        nombre: row.nombre || row.name || `Empleado ${index + 1}`,
        horas_contrato: parseInt(row.horas_contrato || row.contract_hours || 40),
        tarifa_horaria: parseFloat(row.tarifa_horaria || row.hourly_rate || 12),
        disponibilidad,
        preferencias,
        historial: [],
        notas_especiales: row.notas ? [row.notas] : row.notes ? [row.notes] : [],
      }
    })
    return employees
  }

  function parseDemandCSV(csv) {
    const rows = parseCSVText(csv)
    const demanda = {
      lunes: { manana: 0, tarde: 0, noche: 0 },
      martes: { manana: 0, tarde: 0, noche: 0 },
      miercoles: { manana: 0, tarde: 0, noche: 0 },
      jueves: { manana: 0, tarde: 0, noche: 0 },
      viernes: { manana: 0, tarde: 0, noche: 0 },
      sabado: { manana: 0, tarde: 0, noche: 0 },
      domingo: { manana: 0, tarde: 0, noche: 0 },
    }

    rows.forEach((row) => {
      const dia = mapaDias[row.dia?.toLowerCase() || row.day?.toLowerCase() || '']
      if (demanda[dia]) {
        demanda[dia].manana = parseInt(row.manana || row.morning || 0)
        demanda[dia].tarde = parseInt(row.tarde || row.afternoon || 0)
        demanda[dia].noche = parseInt(row.noche || row.night || 0)
      }
    })
    return demanda
  }

  function handleEmployeesUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const csv = e.target?.result || ''
        const employees = parseEmployeesCSV(csv)
        onEmployeesLoaded(employees)
      } catch (error) {
        console.error('Error parsing CSV:', error)
      }
    }
    reader.readAsText(file)
  }

  function handleDemandUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const csv = e.target?.result || ''
        const demand = parseDemandCSV(csv)
        onDemandLoaded(demand)
      } catch (error) {
        console.error('Error parsing CSV:', error)
      }
    }
    reader.readAsText(file)
  }

  return (
    <section className="csv-upload-section">
      <div className="section-title">Cargar datos desde CSV</div>
      <div className="csv-row">
        <label>
          Empleados
          <input type="file" accept=".csv" onChange={handleEmployeesUpload} />
        </label>
        <label>
          Demanda
          <input type="file" accept=".csv" onChange={handleDemandUpload} />
        </label>
      </div>
      <p className="csv-hint">
        <strong>Formato Empleados:</strong> nombre, horas_contrato, tarifa_horaria, lunes, martes, miercoles, jueves, viernes, sabado, domingo, notas
        <br />
        <strong>Formato Demanda:</strong> dia, mañana, tarde, noche
        <br />
        <strong>Disponibilidad:</strong> separa turnos con | (ej: "mañana|tarde", "todos", "descanso")
      </p>
    </section>
  )
}

import { useEffect, useState } from 'react'
import { optimizeSchedule, fetchSampleData } from './api'
import { defaultConfig, defaultWeights } from './sampleData'
import { MetricCard } from './components/MetricCard'
import { LineChart } from './components/LineChart'
import { RankingBarsChart } from './components/RankingBarsChart'
import { RankingTable } from './components/RankingTable'
import { ScheduleTable } from './components/ScheduleTable'
import { CSVUploader } from './components/CSVUploader'

const profileLabels = {
  A: 'Planificación A',
  B: 'Planificación B',
  C: 'Planificación C',
}

const selectionLabels = {
  torneo: 'Torneo',
  emparejamiento_ranking: 'Emparejamiento por ranking',
  emparejamiento_mitad_ordenada: 'Mitades ordenadas (1ro con 1ro)',
}

const crossoverLabels = {
  dos_puntos: 'Cruza de dos puntos',
  multipunto: 'Cruza multipunto',
  uniforme: 'Cruza uniforme',
}

const mutationLabels = {
  puntual: 'Mutación puntual',
  hibrida: 'Mutación híbrida',
  intercambio: 'Mutación por intercambio',
}

const initializationLabels = {
  aleatoria: 'Aleatoria',
  sesgada_preferencias: 'Sesgada por preferencias',
}

const pruningLabels = {
  elitismo: 'Elitismo',
  reemplazo_generacional: 'Reemplazo generacional total',
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function toAbsoluteUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return `${API_BASE}${path}`
}

function toJson(value) {
  return JSON.stringify(value, null, 2)
}

function safeParse(text, fallback) {
  try {
    return JSON.parse(text)
  } catch {
    return fallback
  }
}

export default function App() {
  const [employeesText, setEmployeesText] = useState('[]')
  const [demandText, setDemandText] = useState('{}')
  const [config, setConfig] = useState(defaultConfig)
  const [weights, setWeights] = useState(defaultWeights)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)
  const [selectedProfile, setSelectedProfile] = useState('A')

  useEffect(() => {
    fetchSampleData()
      .then((response) => {
        if (response?.empleados && response?.demanda) {
          setEmployeesText(toJson(response.empleados))
          setDemandText(toJson(response.demanda))
        }
      })
      .catch(() => {
        setEmployeesText('[]')
        setDemandText('{}')
      })
  }, [])

  const currentProfile = data?.perfiles?.[selectedProfile]
  const currentRanking = currentProfile?.ranking || []
  const bestByGeneration = currentProfile?.mejores_por_generacion || []
  const configSummary = [
    ['Inicialización', initializationLabels[config.metodo_inicializacion]],
    ['Selección', selectionLabels[config.metodo_seleccion]],
    ['Cruza', crossoverLabels[config.metodo_cruce]],
    ['Mutación', mutationLabels[config.metodo_mutacion]],
    ['Poda', pruningLabels[config.metodo_poda]],
    ['Semilla', config.semilla ?? 'sin semilla'],
  ]

  async function handleOptimize(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    const employees = safeParse(employeesText, [])
    const demand = safeParse(demandText, {})

    if (!employees.length) {
      setError('Debes cargar al menos un empleado (JSON o CSV)')
      setLoading(false)
      return
    }

    if (!Object.keys(demand).length) {
      setError('Debes especificar la demanda semanal')
      setLoading(false)
      return
    }

    try {
      const response = await optimizeSchedule({
        empleados: employees,
        demanda: demand,
        pesos: weights,
        configuracion: config,
      })
      setData(response)
      setSelectedProfile('A')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  function loadExample() {
    setEmployeesText('[]')
    setDemandText('{}')
    setConfig(defaultConfig)
    setWeights(defaultWeights)
    setError('')
  }

  function handleEmployeesFromCSV(employees) {
    setEmployeesText(toJson(employees))
    setError('')
  }

  function handleDemandFromCSV(demand) {
    setDemandText(toJson(demand))
    setError('')
  }

  const summaryCards = currentProfile
    ? [
        {
          title: 'Aptitud',
          value: currentProfile.aptitud.toFixed(6),
          subtitle: profileLabels[selectedProfile],
          accent: '#1a73e8',
        },
        {
          title: 'Déficit cobertura',
          value: currentProfile.deficit_cobertura,
          subtitle: 'Menor es mejor',
          accent: '#ea4335',
        },
        {
          title: 'Horas extra',
          value: currentProfile.horas_extra,
          subtitle: 'Control presupuestario',
          accent: '#188038',
        },
        {
          title: 'Violaciones',
          value: currentProfile.violaciones_legales,
          subtitle: 'Cumplimiento legal',
          accent: '#f9ab00',
        },
        {
          title: 'Gen. mejor global',
          value: currentProfile.generacion_mejor_global ?? '-',
          subtitle: 'Menor costo encontrado',
          accent: '#0b57d0',
        },
      ]
    : []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__eyebrow">SHIFTPLANGA</div>
          <h1>Configuración y ejecución del AG</h1>
          <p>
            Ajusta parámetros, ejecuta y revisa las salidas.
          </p>
        </div>

        <form className="config-panel" onSubmit={handleOptimize}>
          <section>
            <div className="section-title">Configuración del AG</div>
            <div className="grid-2">
              <label>
                Población
                <input type="number" value={config.poblacion} onChange={(event) => setConfig({ ...config, poblacion: Number(event.target.value) })} />
              </label>
              <label>
                Generaciones
                <input type="number" value={config.generations} onChange={(event) => setConfig({ ...config, generations: Number(event.target.value) })} />
              </label>
              <label>
                Cruza
                <input type="number" step="0.01" value={config.probabilidad_cruce} onChange={(event) => setConfig({ ...config, probabilidad_cruce: Number(event.target.value) })} />
              </label>
              <label>
                Mutación
                <input type="number" step="0.01" value={config.probabilidad_mutacion} onChange={(event) => setConfig({ ...config, probabilidad_mutacion: Number(event.target.value) })} />
              </label>
              <label>
                Elitismo
                <input type="number" step="0.01" value={config.probabilidad_elitismo} onChange={(event) => setConfig({ ...config, probabilidad_elitismo: Number(event.target.value) })} />
              </label>
              <label>
                Torneo
                <input type="number" value={config.tamano_torneo} onChange={(event) => setConfig({ ...config, tamano_torneo: Number(event.target.value) })} />
              </label>
              <label>
                Semilla
                <input type="number" value={config.semilla} onChange={(event) => setConfig({ ...config, semilla: Number(event.target.value) })} />
              </label>
              <label>
                Inicialización
                <select value={config.metodo_inicializacion} onChange={(event) => setConfig({ ...config, metodo_inicializacion: event.target.value })}>
                  <option value="aleatoria">{initializationLabels.aleatoria}</option>
                  <option value="sesgada_preferencias">{initializationLabels.sesgada_preferencias}</option>
                </select>
              </label>
              <label>
                Selección
                <select value={config.metodo_seleccion} onChange={(event) => setConfig({ ...config, metodo_seleccion: event.target.value })}>
                  <option value="torneo">{selectionLabels.torneo}</option>
                  <option value="emparejamiento_ranking">{selectionLabels.emparejamiento_ranking}</option>
                  <option value="emparejamiento_mitad_ordenada">{selectionLabels.emparejamiento_mitad_ordenada}</option>
                </select>
              </label>
              <label>
                Cruza
                <select value={config.metodo_cruce} onChange={(event) => setConfig({ ...config, metodo_cruce: event.target.value })}>
                  <option value="dos_puntos">{crossoverLabels.dos_puntos}</option>
                  <option value="multipunto">{crossoverLabels.multipunto}</option>
                  <option value="uniforme">{crossoverLabels.uniforme}</option>
                </select>
              </label>
              <label>
                Mutación
                <select value={config.metodo_mutacion} onChange={(event) => setConfig({ ...config, metodo_mutacion: event.target.value })}>
                  <option value="puntual">{mutationLabels.puntual}</option>
                  <option value="hibrida">{mutationLabels.hibrida}</option>
                  <option value="intercambio">{mutationLabels.intercambio}</option>
                </select>
              </label>
              <label>
                Poda
                <select value={config.metodo_poda} onChange={(event) => setConfig({ ...config, metodo_poda: event.target.value })}>
                  <option value="elitismo">{pruningLabels.elitismo}</option>
                  <option value="reemplazo_generacional">{pruningLabels.reemplazo_generacional}</option>
                </select>
              </label>
              <label>
                Sesgo inicial (0-1)
                <input
                  type="number"
                  step="0.01"
                  value={config.fraccion_sesgo_preferencias}
                  onChange={(event) => setConfig({ ...config, fraccion_sesgo_preferencias: Number(event.target.value) })}
                />
              </label>
              <label>
                Cortes mín (multi)
                <input
                  type="number"
                  value={config.cortes_minimos_multipunto}
                  onChange={(event) => setConfig({ ...config, cortes_minimos_multipunto: Number(event.target.value) })}
                />
              </label>
              <label>
                Cortes máx (multi)
                <input
                  type="number"
                  value={config.cortes_maximos_multipunto}
                  onChange={(event) => setConfig({ ...config, cortes_maximos_multipunto: Number(event.target.value) })}
                />
              </label>
              <label>
                Prob. reinicio (híbrida)
                <input
                  type="number"
                  step="0.01"
                  value={config.probabilidad_reinicio_hibrida}
                  onChange={(event) => setConfig({ ...config, probabilidad_reinicio_hibrida: Number(event.target.value) })}
                />
              </label>
            </div>
          </section>

          <section>
            <div className="section-title">Pesos de optimización</div>
            <div className="grid-2">
              {Object.entries(weights).map(([key, value]) => (
                <label key={key}>
                  {key}
                  <input
                    type="number"
                    step="0.01"
                    value={value}
                    onChange={(event) => setWeights({ ...weights, [key]: Number(event.target.value) })}
                  />
                </label>
              ))}
            </div>
          </section>

          <CSVUploader onEmployeesLoaded={handleEmployeesFromCSV} onDemandLoaded={handleDemandFromCSV} />

          <section>
            <div className="section-title">Empleados</div>
            <textarea rows="14" value={employeesText} onChange={(event) => setEmployeesText(event.target.value)} />
          </section>

          <section>
            <div className="section-title">Demanda semanal</div>
            <textarea rows="10" value={demandText} onChange={(event) => setDemandText(event.target.value)} />
          </section>

          <div className="button-row">
            <button type="button" className="secondary" onClick={loadExample}>Cargar ejemplo</button>
            <button type="submit" disabled={loading}>{loading ? 'Optimizando...' : 'Ejecutar AG'}</button>
          </div>

          <p className="hint">
            El backend calcula tres perfiles: cobertura/costo, satisfacción laboral y cumplimiento legal.
          </p>
          {error ? <div className="error-box">{error}</div> : null}
        </form>
      </aside>

      <main className="content">
        <header className="hero">
          <div>
            <div className="hero__eyebrow">Salidas del sistema</div>
            <h2>Resultados del algoritmo genético</h2>
            <p>Selecciona perfil y revisa gráficas y tablas.</p>
          </div>
        </header>

        {data ? (
          <>
            <section className="profile-tabs">
              {Object.entries(data.perfiles).map(([key, profile]) => (
                <button
                  key={key}
                  type="button"
                  className={selectedProfile === key ? 'tab tab--active' : 'tab'}
                  onClick={() => setSelectedProfile(key)}
                >
                  <strong>{profileLabels[key]}</strong>
                  <span>Aptitud {profile.aptitud.toFixed(6)}</span>
                </button>
              ))}
            </section>

            <section className="metrics-grid">
              {summaryCards.map((card) => (
                <MetricCard key={card.title} {...card} />
              ))}
            </section>

            <section className="panel panel--project">
              <div className="panel__header">
                <h3>Salidas de gráfica y video</h3>
                <span>Mejor configuración encontrada y evolución del costo</span>
              </div>
              <LineChart
                title="Evolución del costo de optimización"
                history={currentProfile?.historial || []}
                bestGeneration={currentProfile?.generacion_mejor_global || null}
              />
              <RankingBarsChart ranking={currentRanking} />
              {currentProfile?.artefactos ? (
                <div className="artifacts-layout">
                  <video
                    className="result-video"
                    controls
                    preload="metadata"
                    src={toAbsoluteUrl(currentProfile.artefactos.video_resumen)}
                  />
                  <div className="artifact-links">
                    <a href={toAbsoluteUrl(currentProfile.artefactos.grafica_aptitud)} target="_blank" rel="noreferrer">Abrir gráfica exportada</a>
                    <a href={toAbsoluteUrl(currentProfile.artefactos.video_resumen)} target="_blank" rel="noreferrer">Abrir video resumen</a>
                  </div>
                </div>
              ) : null}
            </section>

            <section className="panel panel--project">
              <div className="panel__header">
                <h3>Salidas de tablas</h3>
                <span>Mejor por generación, horario y ranking final</span>
              </div>
              <div className="table-stack">
                <div>
                  <h4>Tabla del mejor individuo por generación</h4>
                  <p>Se toma después de mutación y antes de poda.</p>
                  <div className="table-wrap table-wrap--wide">
                    <table>
                      <thead>
                        <tr>
                          <th>Gen</th>
                          <th>Aptitud</th>
                          <th>Déficit</th>
                          <th>Horas extra</th>
                          <th>Insatisfacción</th>
                          <th>Violaciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {bestByGeneration.map((row) => (
                          <tr key={row.generacion}>
                            <td>{row.generacion}</td>
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
                </div>

                <div className="config-summary-layout">
                  <table className="config-summary-table">
                    <tbody>
                      {configSummary.map(([label, value]) => (
                        <tr key={label}>
                          <th>{label}</th>
                          <td>{value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="config-summary-diagram" aria-label="Diagrama de pasos del algoritmo genético">
                    <span>Inicialización</span>
                    <span>Selección</span>
                    <span>Cruza</span>
                    <span>Mutación</span>
                    <span>Poda</span>
                  </div>
                </div>
              </div>
            </section>

            <section className="panel panel--project">
              <div className="panel__header">
                <h3>Horario y ranking final</h3>
                <span>Configuración del mejor perfil seleccionado</span>
              </div>
              <div className="panel__header">
                <h3>Resumen de la solución</h3>
                <span>{profileLabels[selectedProfile]}</span>
              </div>
              <div className="solution-grid">
                <div><strong>Déficit</strong><span>{currentProfile.deficit_cobertura}</span></div>
                <div><strong>Horas extra</strong><span>{currentProfile.horas_extra}</span></div>
                <div><strong>Insatisfacción</strong><span>{currentProfile.insatisfaccion}</span></div>
                <div><strong>Violaciones</strong><span>{currentProfile.violaciones_legales}</span></div>
              </div>
              <ScheduleTable schedule={currentProfile.horario} />
              <RankingTable ranking={currentProfile.ranking} />
            </section>
          </>
        ) : (
          <section className="empty-state">
            <h3>Listo para ejecutar la optimización</h3>
            <p>
              Carga los datos o usa el ejemplo y presiona <strong>Ejecutar AG</strong> para obtener las tres planificaciones.
            </p>
          </section>
        )}
      </main>
    </div>
  )
}

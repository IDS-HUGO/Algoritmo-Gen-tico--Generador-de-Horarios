export const defaultConfig = {
  poblacion: 60,
  generations: 60,
  probabilidad_cruce: 0.85,
  probabilidad_mutacion: 0.08,
  probabilidad_elitismo: 0.15,
  tamano_torneo: 3,
  semilla: 42,
  metodo_inicializacion: 'aleatoria',
  metodo_seleccion: 'torneo',
  metodo_cruce: 'dos_puntos',
  metodo_mutacion: 'puntual',
  metodo_poda: 'elitismo',
  fraccion_sesgo_preferencias: 0.7,
  cortes_minimos_multipunto: 1,
  cortes_maximos_multipunto: 3,
  probabilidad_reinicio_hibrida: 0.7,
}

export const defaultWeights = {
  cobertura: 0.35,
  horas_extra: 0.25,
  insatisfaccion: 0.2,
  legal: 0.2,
}

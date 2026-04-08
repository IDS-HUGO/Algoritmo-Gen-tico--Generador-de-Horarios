from dataclasses import dataclass


@dataclass
class GAConfig:
    # Core loop
    poblacion: int = 60
    generations: int = 60
    probabilidad_cruce: float = 0.85
    probabilidad_mutacion: float = 0.08
    probabilidad_elitismo: float = 0.15
    tamano_torneo: int = 3
    semilla: int | None = 42

    # Operator strategies
    metodo_inicializacion: str = "aleatoria"  # aleatoria | sesgada_preferencias
    metodo_seleccion: str = "torneo"  # torneo | emparejamiento_ranking | emparejamiento_mitad_ordenada
    metodo_cruce: str = "dos_puntos"  # dos_puntos | multipunto | uniforme
    metodo_mutacion: str = "puntual"  # puntual | hibrida | intercambio
    metodo_poda: str = "elitismo"  # elitismo | reemplazo_generacional

    # Initialization tuning
    fraccion_sesgo_preferencias: float = 0.70

    # Multi-point crossover tuning
    cortes_minimos_multipunto: int = 1
    cortes_maximos_multipunto: int = 3

    # Hybrid mutation tuning
    probabilidad_reinicio_hibrida: float = 0.70

    # Labor constraints
    horas_descanso_minimas: int = 12
    horas_semanales_maximas: int = 48
    dias_descanso_minimos: int = 1
    noches_consecutivas_maximas: int = 3

    # Shift durations
    horas_manana: int = 8
    horas_tarde: int = 8
    horas_noche: int = 8

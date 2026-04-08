DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
TURNOS = ["descanso", "manana", "tarde", "noche"]
HORAS_TURNO = {"descanso": 0, "manana": 8, "tarde": 8, "noche": 8}
INICIO_FIN_TURNO = {
    "descanso": (None, None),
    "manana": (6, 14),
    "tarde": (14, 22),
    "noche": (22, 30),
}

from __future__ import annotations

from typing import Any

from ..config import GAConfig
from .constants import DIAS, HORAS_TURNO, INICIO_FIN_TURNO


def build_default_demand() -> dict[str, dict[str, int]]:
    return {dia: {"manana": 0, "tarde": 0, "noche": 0} for dia in DIAS}


def total_weekly_hours(schedule: list[str]) -> int:
    return sum(HORAS_TURNO[turno] for turno in schedule)


def count_consecutive_nights(schedule: list[str]) -> int:
    streak = 0
    max_streak = 0
    for turno in schedule:
        if turno == "noche":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def rest_hours_between(prev_shift: str, next_shift: str) -> int:
    prev_end = INICIO_FIN_TURNO[prev_shift][1]
    next_start = INICIO_FIN_TURNO[next_shift][0]
    if prev_end is None or next_start is None:
        return 24
    return (24 - prev_end) + next_start


def evaluate_individual(
    individual: list[list[str]],
    employees: list[dict[str, Any]],
    demand: dict[str, dict[str, int]],
    weights: dict[str, float],
    config: GAConfig,
) -> dict[str, Any]:
    coverage_deficit = 0
    overtime_hours = 0
    dissatisfaction = 0
    legal_violations = 0

    cobertura_por_dia: dict[str, dict[str, int]] = {dia: {"manana": 0, "tarde": 0, "noche": 0} for dia in DIAS}
    employee_summaries: list[dict[str, Any]] = []

    for employee_index, employee in enumerate(employees):
        schedule = individual[employee_index]
        weekly_hours = total_weekly_hours(schedule)
        overtime_hours += max(0, weekly_hours - employee["horas_contrato"])

        employee_violations = 0
        employee_dissatisfaction = 0

        dias_descanso = sum(1 for turno in schedule if turno == "descanso")
        if dias_descanso < config.dias_descanso_minimos:
            employee_violations += 1

        if weekly_hours > config.horas_semanales_maximas:
            employee_violations += 1

        if count_consecutive_nights(schedule) > config.noches_consecutivas_maximas:
            employee_violations += 1

        for indice_dia, dia in enumerate(DIAS):
            turno = schedule[indice_dia]
            preferences = employee["preferencias"]
            employee_dissatisfaction += max(0, 5 - preferences.get(turno, 1))

            if turno != "descanso":
                if turno not in employee["disponibilidad"].get(dia, ["descanso"]):
                    employee_violations += 1
                cobertura_por_dia[dia][turno] += 1

            if indice_dia > 0:
                turno_anterior = schedule[indice_dia - 1]
                if turno_anterior != "descanso" and turno != "descanso":
                    if rest_hours_between(turno_anterior, turno) < config.horas_descanso_minimas:
                        employee_violations += 1

        dissatisfaction += employee_dissatisfaction
        legal_violations += employee_violations

        employee_summaries.append(
            {
                "id_empleado": employee["id"],
                "nombre_empleado": employee["nombre"],
                "horas": weekly_hours,
                "horas_extra": max(0, weekly_hours - employee["horas_contrato"]),
                "insatisfaccion": employee_dissatisfaction,
                "violaciones_legales": employee_violations,
                "horario": schedule,
            }
        )

    for dia in DIAS:
        for turno in ("manana", "tarde", "noche"):
            coverage_deficit += max(0, demand[dia][turno] - cobertura_por_dia[dia][turno])

    coverage_score = 1.0 / (1.0 + coverage_deficit)
    overtime_score = 1.0 / (1.0 + overtime_hours)
    dissatisfaction_score = 1.0 / (1.0 + dissatisfaction)
    legal_score = 1.0 / (1.0 + legal_violations)

    fitness = (
        coverage_score ** weights["cobertura"]
        * overtime_score ** weights["horas_extra"]
        * dissatisfaction_score ** weights["insatisfaccion"]
        * legal_score ** weights["legal"]
    )

    return {
        "fitness": fitness,
        "deficit_cobertura": coverage_deficit,
        "overtime_hours": overtime_hours,
        "insatisfaccion": dissatisfaction,
        "violaciones_legales": legal_violations,
        "resumenes_empleados": employee_summaries,
        "cobertura_por_dia": cobertura_por_dia,
    }

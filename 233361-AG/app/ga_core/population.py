from __future__ import annotations

import random
from typing import Any

from ..config import GAConfig
from .constants import DIAS


def build_random_individual(num_employees: int, rng: random.Random, employees: list[dict[str, Any]]) -> list[list[str]]:
    individual: list[list[str]] = []
    for employee_index in range(num_employees):
        employee = employees[employee_index]
        row: list[str] = []
        for dia in DIAS:
            allowed = employee["disponibilidad"].get(dia, ["descanso"])
            row.append(rng.choice(allowed))
        individual.append(row)
    return individual


def build_preference_biased_individual(
    num_employees: int,
    rng: random.Random,
    employees: list[dict[str, Any]],
    fraccion_sesgo_preferencias: float,
) -> list[list[str]]:
    individual: list[list[str]] = []
    for employee_index in range(num_employees):
        employee = employees[employee_index]
        preferencias = employee.get("preferencias", {})
        row: list[str] = []
        for dia in DIAS:
            allowed = employee["disponibilidad"].get(dia, ["descanso"])
            if not allowed:
                row.append("descanso")
                continue

            turno_preferido = max(allowed, key=lambda turno: preferencias.get(turno, 1))
            if rng.random() < fraccion_sesgo_preferencias:
                row.append(turno_preferido)
            else:
                row.append(rng.choice(allowed))
        individual.append(row)
    return individual


def initialize_population(
    num_employees: int,
    employees: list[dict[str, Any]],
    population_size: int,
    rng: random.Random,
    config: GAConfig,
) -> list[list[list[str]]]:
    if config.metodo_inicializacion == "sesgada_preferencias":
        return [
            build_preference_biased_individual(
                num_employees,
                rng,
                employees,
                config.fraccion_sesgo_preferencias,
            )
            for _ in range(population_size)
        ]
    return [build_random_individual(num_employees, rng, employees) for _ in range(population_size)]

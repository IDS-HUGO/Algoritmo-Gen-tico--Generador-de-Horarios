from __future__ import annotations

import copy
import random
from typing import Any

from ..config import GAConfig
from .fitness import build_default_demand, evaluate_individual
from .operators import (
    apply_elitism,
    build_ranking,
    crossover_multi_point,
    crossover_two_point,
    crossover_uniform,
    mutate_hybrid,
    mutate_point,
    mutate_swap,
    ordered_half_pairing,
    ranking_pairing,
    tournament_selection,
)
from .population import initialize_population
from .weights import blend_profile_weights, default_profiles, normalize_weights


def build_schedule_rows(employee_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in employee_summaries:
        row = {
            "id_empleado": summary["id_empleado"],
            "nombre_empleado": summary["nombre_empleado"],
            "horas": summary["horas"],
            "horas_extra": summary["horas_extra"],
            "insatisfaccion": summary["insatisfaccion"],
            "violaciones_legales": summary["violaciones_legales"],
        }
        for dia, turno in zip(["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"], summary["horario"]):
            row[dia] = turno
        rows.append(row)
    return rows


def build_solution_summary(label: str, result: dict[str, Any]) -> dict[str, Any]:
    best_evaluation = result["best_evaluation"]
    return {
        "etiqueta": label,
        "aptitud": round(best_evaluation["fitness"], 8),
        "generacion_mejor_global": result["best_generation"],
        "deficit_cobertura": best_evaluation["deficit_cobertura"],
        "horas_extra": best_evaluation["overtime_hours"],
        "insatisfaccion": best_evaluation["insatisfaccion"],
        "violaciones_legales": best_evaluation["violaciones_legales"],
        "horario": build_schedule_rows(best_evaluation["resumenes_empleados"]),
        "historial": result["historial"],
        "mejores_por_generacion": result["mejores_por_generacion"],
        "ranking": result["ranking"],
    }


def _crossover(parent_a: list[list[str]], parent_b: list[list[str]], config: GAConfig, rng: random.Random) -> tuple[list[list[str]], list[list[str]]]:
    if config.metodo_cruce == "multipunto":
        return crossover_multi_point(parent_a, parent_b, config, rng)
    if config.metodo_cruce == "uniforme":
        return crossover_uniform(parent_a, parent_b, rng)
    return crossover_two_point(parent_a, parent_b, rng)


def _mutate(individual: list[list[str]], employees: list[dict[str, Any]], config: GAConfig, rng: random.Random) -> list[list[str]]:
    if config.metodo_mutacion == "hibrida":
        return mutate_hybrid(individual, employees, config, rng)
    if config.metodo_mutacion == "intercambio":
        return mutate_swap(individual, config, rng)
    return mutate_point(individual, employees, config, rng)


def _parents_from_selection(
    population: list[list[list[str]]],
    evaluations: list[dict[str, Any]],
    config: GAConfig,
    rng: random.Random,
) -> list[tuple[list[list[str]], list[list[str]]]]:
    if config.metodo_seleccion == "emparejamiento_mitad_ordenada":
        pairs = ordered_half_pairing(population, evaluations)
        if pairs:
            return pairs

    if config.metodo_seleccion == "emparejamiento_ranking":
        pairs = ranking_pairing(population, evaluations, rng)
        if pairs:
            return pairs

    pairs: list[tuple[list[list[str]], list[list[str]]]] = []
    pair_count = max(1, len(population) // 2)
    for _ in range(pair_count):
        parent_a = tournament_selection(population, evaluations, config.tamano_torneo, rng)
        parent_b = tournament_selection(population, evaluations, config.tamano_torneo, rng)
        pairs.append((parent_a, parent_b))
    return pairs


def run_genetic_algorithm(
    employees: list[dict[str, Any]],
    demand: dict[str, dict[str, int]],
    weights: dict[str, float],
    config: GAConfig,
) -> dict[str, Any]:
    if not employees:
        return {
            "best_individual": [],
            "best_generation": None,
            "best_evaluation": {
                "fitness": 0,
                "deficit_cobertura": 0,
                "overtime_hours": 0,
                "insatisfaccion": 0,
                "violaciones_legales": 0,
                "resumenes_empleados": [],
            },
            "historial": [],
            "ranking": [],
            "final_population": [],
            "final_evaluations": [],
            "normalized_weights": normalize_weights(weights),
        }

    if not demand:
        demand = build_default_demand()

    rng = random.Random(config.semilla)
    normalized_weights = normalize_weights(weights)
    population = initialize_population(len(employees), employees, config.poblacion, rng, config)

    historial: list[dict[str, float]] = []
    mejores_por_generacion: list[dict[str, Any]] = []
    best_individual: list[list[str]] | None = None
    best_evaluation: dict[str, Any] | None = None
    best_generation: int | None = None

    for generation in range(config.generations):
        evaluations = [evaluate_individual(individual, employees, demand, normalized_weights, config) for individual in population]
        pairs = _parents_from_selection(population, evaluations, config, rng)

        offspring: list[list[list[str]]] = []
        target_offspring = max(1, config.poblacion)

        pair_idx = 0
        while len(offspring) < target_offspring and pairs:
            parent_a, parent_b = pairs[pair_idx % len(pairs)]
            pair_idx += 1

            if rng.random() < config.probabilidad_cruce:
                child_a, child_b = _crossover(parent_a, parent_b, config, rng)
            else:
                child_a, child_b = copy.deepcopy(parent_a), copy.deepcopy(parent_b)

            offspring.append(_mutate(child_a, employees, config, rng))
            if len(offspring) < target_offspring:
                offspring.append(_mutate(child_b, employees, config, rng))

        # Se evalua en el punto requerido: despues de mutacion y antes de la poda.
        population_total = population + offspring
        total_evaluations = [
            evaluate_individual(individual, employees, demand, normalized_weights, config)
            for individual in population_total
        ]
        total_ranking_indices = sorted(
            range(len(population_total)), key=lambda idx: total_evaluations[idx]["fitness"], reverse=True
        )
        best_total_idx = total_ranking_indices[0]
        current_best = total_evaluations[best_total_idx]

        historial.append(
            {
                "generacion": generation + 1,
                "mejor": round(current_best["fitness"], 8),
                "promedio": round(sum(item["fitness"] for item in total_evaluations) / len(total_evaluations), 8),
                "peor": round(total_evaluations[total_ranking_indices[-1]]["fitness"], 8),
            }
        )

        if best_evaluation is None or current_best["fitness"] > best_evaluation["fitness"]:
            best_evaluation = copy.deepcopy(current_best)
            best_individual = copy.deepcopy(population_total[best_total_idx])
            best_generation = generation + 1

        mejores_por_generacion.append(
            {
                "generacion": generation + 1,
                "aptitud": round(current_best["fitness"], 8),
                "deficit_cobertura": current_best["deficit_cobertura"],
                "horas_extra": current_best["overtime_hours"],
                "insatisfaccion": current_best["insatisfaccion"],
                "violaciones_legales": current_best["violaciones_legales"],
                "horario": build_schedule_rows(current_best["resumenes_empleados"]),
            }
        )

        if config.metodo_poda == "reemplazo_generacional":
            if offspring:
                population = offspring[: config.poblacion]
            else:
                population = [copy.deepcopy(population[total_ranking_indices[0]]) for _ in range(config.poblacion)]
        else:
            population = apply_elitism(population_total, total_evaluations, config.poblacion)

    final_evaluations = [evaluate_individual(individual, employees, demand, normalized_weights, config) for individual in population]

    if best_individual is None or best_evaluation is None:
        best_individual = population[0]
        best_evaluation = final_evaluations[0]

    return {
        "best_individual": best_individual,
        "best_generation": best_generation,
        "best_evaluation": best_evaluation,
        "historial": historial,
        "mejores_por_generacion": mejores_por_generacion,
        "ranking": build_ranking(population, final_evaluations),
        "final_population": population,
        "final_evaluations": final_evaluations,
        "normalized_weights": normalized_weights,
    }


def run_profiles(employees: list[dict[str, Any]], demand: dict[str, dict[str, int]], config: GAConfig, base_weights: dict[str, float]) -> dict[str, Any]:
    solutions: dict[str, Any] = {}
    for profile_name, profile_weights in default_profiles().items():
        effective_weights = blend_profile_weights(base_weights, profile_weights)
        result = run_genetic_algorithm(employees, demand, effective_weights, config)
        solutions[profile_name] = build_solution_summary(profile_name, result)
    return solutions

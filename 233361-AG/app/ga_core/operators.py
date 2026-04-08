from __future__ import annotations

import copy
import random
from typing import Any

from ..config import GAConfig
from .constants import DIAS


def tournament_selection(population: list[list[list[str]]], evaluations: list[dict[str, Any]], tournament_size: int, rng: random.Random) -> list[list[str]]:
    contenders = rng.sample(list(enumerate(population)), k=min(tournament_size, len(population)))
    best_index = max(contenders, key=lambda item: evaluations[item[0]]["fitness"])[0]
    return copy.deepcopy(population[best_index])


def ranking_pairing(population: list[list[list[str]]], evaluations: list[dict[str, Any]], rng: random.Random) -> list[tuple[list[list[str]], list[list[str]]]]:
    ranked = sorted(zip(population, evaluations), key=lambda item: item[1]["fitness"], reverse=True)
    ordered_population = [item[0] for item in ranked]
    half = len(ordered_population) // 2
    best = ordered_population[:half]
    rest = ordered_population[half:]
    rng.shuffle(rest)
    return [(copy.deepcopy(best[i]), copy.deepcopy(rest[i])) for i in range(min(len(best), len(rest)))]


def ordered_half_pairing(population: list[list[list[str]]], evaluations: list[dict[str, Any]]) -> list[tuple[list[list[str]], list[list[str]]]]:
    ranked = sorted(zip(population, evaluations), key=lambda item: item[1]["fitness"], reverse=True)
    ordered_population = [item[0] for item in ranked]
    half = len(ordered_population) // 2
    first_half = ordered_population[:half]
    second_half = ordered_population[half:]
    return [(copy.deepcopy(first_half[i]), copy.deepcopy(second_half[i])) for i in range(min(len(first_half), len(second_half)))]


def crossover_two_point(parent_a: list[list[str]], parent_b: list[list[str]], rng: random.Random) -> tuple[list[list[str]], list[list[str]]]:
    child_a = copy.deepcopy(parent_a)
    child_b = copy.deepcopy(parent_b)
    if not parent_a:
        return child_a, child_b

    start = rng.randint(0, len(DIAS) - 2)
    end = rng.randint(start + 1, len(DIAS) - 1)

    for employee_index in range(len(parent_a)):
        slice_a = child_a[employee_index][start:end]
        slice_b = child_b[employee_index][start:end]
        child_a[employee_index][start:end] = slice_b
        child_b[employee_index][start:end] = slice_a

    return child_a, child_b


def crossover_multi_point(parent_a: list[list[str]], parent_b: list[list[str]], config: GAConfig, rng: random.Random) -> tuple[list[list[str]], list[list[str]]]:
    child_a = copy.deepcopy(parent_a)
    child_b = copy.deepcopy(parent_b)
    if not parent_a:
        return child_a, child_b

    max_cuts = min(config.cortes_maximos_multipunto, len(DIAS) - 1)
    min_cuts = min(config.cortes_minimos_multipunto, max_cuts)
    num_cuts = rng.randint(min_cuts, max_cuts)
    cuts = sorted(rng.sample(range(1, len(DIAS)), k=num_cuts))
    slices = [0] + cuts + [len(DIAS)]

    for employee_index in range(len(parent_a)):
        segments_a: list[str] = []
        segments_b: list[str] = []
        for segment_index in range(len(slices) - 1):
            left = slices[segment_index]
            right = slices[segment_index + 1]
            if segment_index % 2 == 0:
                segments_a.extend(parent_a[employee_index][left:right])
                segments_b.extend(parent_b[employee_index][left:right])
            else:
                segments_a.extend(parent_b[employee_index][left:right])
                segments_b.extend(parent_a[employee_index][left:right])
        child_a[employee_index] = segments_a
        child_b[employee_index] = segments_b

    return child_a, child_b


def crossover_uniform(parent_a: list[list[str]], parent_b: list[list[str]], rng: random.Random) -> tuple[list[list[str]], list[list[str]]]:
    child_a = copy.deepcopy(parent_a)
    child_b = copy.deepcopy(parent_b)
    if not parent_a:
        return child_a, child_b

    for employee_index in range(len(parent_a)):
        for indice_dia in range(len(DIAS)):
            if rng.random() < 0.5:
                child_a[employee_index][indice_dia], child_b[employee_index][indice_dia] = (
                    child_b[employee_index][indice_dia],
                    child_a[employee_index][indice_dia],
                )

    return child_a, child_b


def mutate_point(individual: list[list[str]], employees: list[dict[str, Any]], config: GAConfig, rng: random.Random) -> list[list[str]]:
    mutated = copy.deepcopy(individual)
    for employee_index, employee in enumerate(employees):
        for indice_dia, dia in enumerate(DIAS):
            if rng.random() < config.probabilidad_mutacion:
                allowed = employee["disponibilidad"].get(dia, ["descanso"])
                mutated[employee_index][indice_dia] = rng.choice(allowed)
    return mutated


def mutate_hybrid(individual: list[list[str]], employees: list[dict[str, Any]], config: GAConfig, rng: random.Random) -> list[list[str]]:
    mutated = copy.deepcopy(individual)
    if not mutated:
        return mutated

    if rng.random() <= config.probabilidad_mutacion:
        employee_index = rng.randrange(len(mutated))
        if rng.random() <= config.probabilidad_reinicio_hibrida:
            indice_dia = rng.randrange(len(DIAS))
            dia = DIAS[indice_dia]
            allowed = employees[employee_index]["disponibilidad"].get(dia, ["descanso"])
            mutated[employee_index][indice_dia] = rng.choice(allowed)
        else:
            indice_a, indice_b = rng.sample(range(len(DIAS)), k=2)
            mutated[employee_index][indice_a], mutated[employee_index][indice_b] = (
                mutated[employee_index][indice_b],
                mutated[employee_index][indice_a],
            )

    return mutated


def mutate_swap(individual: list[list[str]], config: GAConfig, rng: random.Random) -> list[list[str]]:
    mutated = copy.deepcopy(individual)
    if not mutated:
        return mutated

    for employee_index in range(len(mutated)):
        if rng.random() < config.probabilidad_mutacion:
            indice_a, indice_b = rng.sample(range(len(DIAS)), k=2)
            mutated[employee_index][indice_a], mutated[employee_index][indice_b] = (
                mutated[employee_index][indice_b],
                mutated[employee_index][indice_a],
            )
    return mutated


def apply_elitism(population: list[list[list[str]]], evaluations: list[dict[str, Any]], elite_count: int) -> list[list[list[str]]]:
    ranked = sorted(zip(population, evaluations), key=lambda item: item[1]["fitness"], reverse=True)
    return [copy.deepcopy(individual) for individual, _ in ranked[:elite_count]]


def build_ranking(population: list[list[list[str]]], evaluations: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(zip(population, evaluations), key=lambda item: item[1]["fitness"], reverse=True)
    table: list[dict[str, Any]] = []
    for position, (_, evaluation) in enumerate(ranked[:limit], start=1):
        table.append(
            {
                "posicion": position,
                "aptitud": round(evaluation["fitness"], 6),
                "deficit_cobertura": evaluation["deficit_cobertura"],
                "horas_extra": evaluation["overtime_hours"],
                "insatisfaccion": evaluation["insatisfaccion"],
                "violaciones_legales": evaluation["violaciones_legales"],
            }
        )
    return table

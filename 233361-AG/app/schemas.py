from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ShiftName = Literal["descanso", "manana", "tarde", "noche"]


class EmployeeInput(BaseModel):
    id: int
    nombre: str
    horas_contrato: int = Field(ge=0, le=48)
    tarifa_horaria: float = Field(ge=0)
    disponibilidad: dict[str, list[ShiftName]]
    preferencias: dict[ShiftName, int]
    historial: list[ShiftName] = Field(default_factory=list)
    notas_especiales: list[str] = Field(default_factory=list)


class DemandShift(BaseModel):
    manana: int = Field(ge=0)
    tarde: int = Field(ge=0)
    noche: int = Field(ge=0)


class OptimizationWeights(BaseModel):
    cobertura: float = Field(default=0.35, ge=0)
    horas_extra: float = Field(default=0.25, ge=0)
    insatisfaccion: float = Field(default=0.20, ge=0)
    legal: float = Field(default=0.20, ge=0)


class GAInput(BaseModel):
    empleados: list[EmployeeInput]
    demanda: dict[str, DemandShift]
    pesos: OptimizationWeights = OptimizationWeights()
    configuracion: dict[str, Any] = Field(default_factory=dict)


class ScheduleCell(BaseModel):
    dia: str
    turno: ShiftName


class EmployeeSchedule(BaseModel):
    id_empleado: int
    nombre_empleado: str
    celdas: list[ScheduleCell]
    horas: int
    horas_extra: int
    insatisfaccion: int
    violaciones_legales: int


class GenerationPoint(BaseModel):
    generacion: int
    mejor: float
    promedio: float
    peor: float


class SolutionSummary(BaseModel):
    etiqueta: str
    aptitud: float
    generacion_mejor_global: int | None = None
    deficit_cobertura: int
    horas_extra: int
    insatisfaccion: int
    violaciones_legales: int
    cumplimiento_legal: dict[str, Any] = Field(default_factory=dict)
    representacion_genetica: dict[str, Any] = Field(default_factory=dict)
    horario: list[dict[str, Any]]
    historial: list[GenerationPoint]
    mejores_por_generacion: list[dict[str, Any]]
    ranking: list[dict[str, Any]]
    artefactos: dict[str, str] = Field(default_factory=dict)


class OptimizationResponse(BaseModel):
    perfiles: dict[str, SolutionSummary]
    titulo_grafica: str
    titulo_ranking: str
    configuracion_usada: dict[str, Any]

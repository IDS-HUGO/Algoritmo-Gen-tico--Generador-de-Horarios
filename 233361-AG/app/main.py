from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import GAConfig
from .ga import run_profiles
from .reporting import build_run_id, generate_profile_artifacts
from .sample_data import SAMPLE_DEMAND, SAMPLE_EMPLOYEES
from .schemas import GAInput, OptimizationResponse

app = FastAPI(title="SHIFTPLANGA API", version="1.0.0")
OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config-template")
def config_template() -> dict[str, object]:
    return {
        "defaults": GAConfig().__dict__,
        "choices": {
            "metodo_inicializacion": ["aleatoria", "sesgada_preferencias"],
            "metodo_seleccion": ["torneo", "emparejamiento_ranking", "emparejamiento_mitad_ordenada"],
            "metodo_cruce": ["dos_puntos", "multipunto", "uniforme"],
            "metodo_mutacion": ["puntual", "hibrida", "intercambio"],
            "metodo_poda": ["elitismo", "reemplazo_generacional"],
        },
    }


@app.get("/api/sample-data")
def sample_data() -> dict[str, object]:
    return {
        "empleados": SAMPLE_EMPLOYEES,
        "demanda": SAMPLE_DEMAND,
    }


@app.post("/api/optimize", response_model=OptimizationResponse)
def optimize(payload: GAInput) -> dict[str, object]:
    config_values = {**GAConfig().__dict__, **payload.configuracion}
    if "generaciones" in config_values and "generations" not in payload.configuracion:
        config_values["generations"] = config_values.pop("generaciones")
    elif "generaciones" in config_values:
        config_values.pop("generaciones")
    config = GAConfig(**config_values)
    employees = [employee.model_dump() for employee in payload.empleados]
    demand = {day: shift.model_dump() for day, shift in payload.demanda.items()}
    weights = payload.pesos.model_dump()

    profiles = run_profiles(employees, demand, config, weights)
    run_id = build_run_id()
    for profile_name, profile_data in profiles.items():
        profile_data["artefactos"] = generate_profile_artifacts(
            outputs_root=OUTPUTS_DIR,
            run_id=run_id,
            profile_name=profile_name,
            profile_data=profile_data,
        )

    return {
        "perfiles": profiles,
        "titulo_grafica": "Evolución de la Aptitud Genética",
        "titulo_ranking": "Tabla del Mejor al Peor Individuo",
        "configuracion_usada": config_values,
    }

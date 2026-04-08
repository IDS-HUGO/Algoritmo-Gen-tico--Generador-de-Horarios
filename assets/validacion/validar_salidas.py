from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "233361-AG"
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import optimize  # noqa: E402
from app.schemas import DemandShift, EmployeeInput, GAInput, OptimizationWeights  # noqa: E402


TURNOS_VALIDOS = {"descanso", "manana", "tarde", "noche"}
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


def parse_turnos(texto: str) -> list[str]:
    partes = [p.strip().lower() for p in (texto or "descanso").split("|")]
    valores = [p if p != "manana" else "manana" for p in partes if p]
    if not valores:
        return ["descanso"]
    limpios = [v for v in valores if v in TURNOS_VALIDOS]
    return limpios or ["descanso"]


def cargar_empleados(csv_path: Path) -> list[EmployeeInput]:
    empleados: list[EmployeeInput] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disponibilidad = {dia: parse_turnos(row.get(dia, "descanso")) for dia in DIAS}
            preferencias = {
                "descanso": int(row.get("pref_descanso", 5)),
                "manana": int(row.get("pref_manana", 3)),
                "tarde": int(row.get("pref_tarde", 3)),
                "noche": int(row.get("pref_noche", 2)),
            }
            empleados.append(
                EmployeeInput(
                    id=int(row["id"]),
                    nombre=row["nombre"],
                    horas_contrato=int(row["horas_contrato"]),
                    tarifa_horaria=float(row["tarifa_horaria"]),
                    disponibilidad=disponibilidad,
                    preferencias=preferencias,
                    historial=[],
                    notas_especiales=[],
                )
            )
    return empleados


def cargar_demanda(csv_path: Path) -> dict[str, DemandShift]:
    demanda: dict[str, DemandShift] = {}
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dia = row["dia"].strip().lower()
            demanda[dia] = DemandShift(
                manana=int(row["manana"]),
                tarde=int(row["tarde"]),
                noche=int(row["noche"]),
            )
    return demanda


def main() -> None:
    base = Path(__file__).resolve().parent
    empleados_csv = base / "empleados_validacion.csv"
    demanda_csv = base / "demanda_validacion.csv"
    payload_json = base / "payload_validacion.json"

    payload_cfg = json.loads(payload_json.read_text(encoding="utf-8"))
    empleados = cargar_empleados(empleados_csv)
    demanda = cargar_demanda(demanda_csv)

    payload = GAInput(
        empleados=empleados,
        demanda=demanda,
        pesos=OptimizationWeights(**payload_cfg["pesos"]),
        configuracion=payload_cfg["configuracion"],
    )

    resultado = optimize(payload)

    evidencia = {
        "escenario": "validacion_csv_json_alterno",
        "entrada": {
            "empleados_csv": str(empleados_csv),
            "demanda_csv": str(demanda_csv),
            "payload_json": str(payload_json),
        },
        "salida": {},
    }

    for perfil, datos in resultado["perfiles"].items():
        evidencia["salida"][perfil] = {
            "aptitud": datos["aptitud"],
            "generacion_mejor_global": datos.get("generacion_mejor_global"),
            "variables_optimizadas": {
                "deficit_cobertura": datos["deficit_cobertura"],
                "horas_extra": datos["horas_extra"],
                "insatisfaccion": datos["insatisfaccion"],
                "violaciones_legales": datos["violaciones_legales"],
            },
            "cumplimiento_legal": datos.get("cumplimiento_legal", {}),
            "representacion_genetica": {
                "tipo_cromosoma": datos.get("representacion_genetica", {}).get("tipo_cromosoma"),
                "longitud_cromosoma": datos.get("representacion_genetica", {}).get("longitud_cromosoma"),
                "gen_por_posicion": datos.get("representacion_genetica", {}).get("gen_por_posicion"),
                "alelos_posibles": datos.get("representacion_genetica", {}).get("alelos_posibles"),
                "locus": datos.get("representacion_genetica", {}).get("locus"),
                "primer_cromosoma_ejemplo": (datos.get("representacion_genetica", {}).get("cromosoma") or [None])[0],
            },
            "evidencias_exportadas": datos.get("artefactos", {}),
        }

    salida_json = base / "evidencia_validacion_salidas.json"
    salida_txt = base / "evidencia_validacion_salidas.txt"
    salida_json.write_text(json.dumps(evidencia, indent=2, ensure_ascii=False), encoding="utf-8")

    lineas: list[str] = []
    lineas.append("EVIDENCIA DE SALIDAS OPTIMIZADAS\n")
    for perfil, datos in evidencia["salida"].items():
        lineas.append(f"Perfil {perfil}")
        lineas.append(f"  Aptitud: {datos['aptitud']}")
        lineas.append(f"  Gen mejor global: {datos['generacion_mejor_global']}")
        lineas.append(f"  Deficit cobertura: {datos['variables_optimizadas']['deficit_cobertura']}")
        lineas.append(f"  Horas extra: {datos['variables_optimizadas']['horas_extra']}")
        lineas.append(f"  Insatisfaccion: {datos['variables_optimizadas']['insatisfaccion']}")
        lineas.append(f"  Violaciones legales: {datos['variables_optimizadas']['violaciones_legales']}")
        lineas.append(f"  Desglose legal: {datos['cumplimiento_legal'].get('desglose', {})}")
        lineas.append(f"  Reglas legales: {datos['cumplimiento_legal'].get('reglas', [])}")
        lineas.append(f"  Representacion genetica: {datos['representacion_genetica']}")
        lineas.append(f"  Artefactos: {datos['evidencias_exportadas']}")
        lineas.append("")

    salida_txt.write_text("\n".join(lineas), encoding="utf-8")

    print(f"OK: evidencia JSON -> {salida_json}")
    print(f"OK: evidencia TXT  -> {salida_txt}")


if __name__ == "__main__":
    main()
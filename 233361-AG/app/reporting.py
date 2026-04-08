from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

from .ga_core.constants import DIAS

_SHIFT_TO_INT = {
    "descanso": 0,
    "manana": 1,
    "tarde": 2,
    "noche": 3,
}


def _configure_ffmpeg() -> None:
    try:
        import imageio_ffmpeg

        plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        # Matplotlib intentara resolver ffmpeg con PATH si no se pudo configurar aqui.
        pass


def build_run_id() -> str:
    return datetime.now().strftime("run_%Y%m%d_%H%M%S")


def _write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerows(rows)


def _export_aptitude_plot(historial: list[dict[str, Any]], out_path: Path) -> None:
    generations = [item["generacion"] for item in historial]
    best_values = [item["mejor"] for item in historial]
    avg_values = [item["promedio"] for item in historial]
    worst_values = [item["peor"] for item in historial]

    plt.figure(figsize=(11, 6))
    plt.plot(generations, best_values, color="#1a73e8", linewidth=2.2, label="Mejor Aptitud vs Generación")
    plt.plot(generations, worst_values, color="#ea4335", linewidth=1.8, linestyle=":", label="Peor Aptitud vs Generación")
    plt.plot(generations, avg_values, color="#188038", linewidth=1.8, linestyle="--", label="Aptitud Promedio vs Generación")

    if best_values:
        best_index = max(range(len(best_values)), key=lambda idx: best_values[idx])
        plt.scatter(generations[best_index], best_values[best_index], color="#0b57d0", s=80, zorder=5)
        plt.annotate(
            f"Mejor global: G{generations[best_index]} = {best_values[best_index]:.6f}",
            xy=(generations[best_index], best_values[best_index]),
            xytext=(20, 20),
            textcoords="offset points",
            arrowprops={"arrowstyle": "->", "color": "#0b57d0", "lw": 1.2},
            fontsize=10,
            color="#0b57d0",
        )

    plt.title("Evolución de la Aptitud (Después de Mutación y Antes de Poda)", fontweight="bold")
    plt.xlabel("Generación")
    plt.ylabel("Aptitud")
    plt.grid(True, alpha=0.28)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    plt.close()


def _export_best_by_generation_csv(best_by_generation: list[dict[str, Any]], out_path: Path) -> None:
    headers = ["generacion", "aptitud", "deficit_cobertura", "horas_extra", "insatisfaccion", "violaciones_legales"]
    rows = [
        [
            item["generacion"],
            item["aptitud"],
            item["deficit_cobertura"],
            item["horas_extra"],
            item["insatisfaccion"],
            item["violaciones_legales"],
        ]
        for item in best_by_generation
    ]
    _write_csv(out_path, headers, rows)


def _export_ranking_csv(ranking: list[dict[str, Any]], out_path: Path) -> None:
    headers = ["posicion", "aptitud", "deficit_cobertura", "horas_extra", "insatisfaccion", "violaciones_legales"]
    rows = [
        [
            item["posicion"],
            item["aptitud"],
            item["deficit_cobertura"],
            item["horas_extra"],
            item["insatisfaccion"],
            item["violaciones_legales"],
        ]
        for item in ranking
    ]
    _write_csv(out_path, headers, rows)


def _export_schedule_csv(schedule: list[dict[str, Any]], out_path: Path) -> None:
    headers = [
        "id_empleado",
        "nombre_empleado",
        *DIAS,
        "horas",
        "horas_extra",
        "insatisfaccion",
        "violaciones_legales",
    ]
    rows: list[list[Any]] = []
    for item in schedule:
        rows.append(
            [
                item["id_empleado"],
                item["nombre_empleado"],
                *(item[dia] for dia in DIAS),
                item["horas"],
                item["horas_extra"],
                item["insatisfaccion"],
                item["violaciones_legales"],
            ]
        )
    _write_csv(out_path, headers, rows)


def _frame_matrix(best_by_generation: list[dict[str, Any]], frame_index: int) -> list[list[int]]:
    frame_data = best_by_generation[frame_index]["horario"]
    matrix: list[list[int]] = []
    for employee in frame_data:
        matrix.append([_SHIFT_TO_INT.get(employee[dia], 0) for dia in DIAS])
    return matrix


def _export_evolution_video(historial: list[dict[str, Any]], best_by_generation: list[dict[str, Any]], out_path: Path) -> None:
    if not historial or not best_by_generation:
        return

    _configure_ffmpeg()

    generations = [item["generacion"] for item in historial]
    best_values = [item["mejor"] for item in historial]
    avg_values = [item["promedio"] for item in historial]
    worst_values = [item["peor"] for item in historial]

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [1.15, 1.0]})
    fig.text(0.82, 0.44, "0=Descanso\n1=Mañana\n2=Tarde\n3=Noche", fontsize=8)

    def update(frame: int) -> None:
        ax_top.clear()
        ax_bottom.clear()

        end = frame + 1
        ax_top.plot(generations[:end], best_values[:end], color="#1a73e8", linewidth=2.1, label="Mejor Aptitud")
        ax_top.plot(generations[:end], worst_values[:end], color="#ea4335", linewidth=1.5, linestyle=":", label="Peor Aptitud")
        ax_top.plot(generations[:end], avg_values[:end], color="#188038", linewidth=1.5, linestyle="--", label="Aptitud Promedio")
        ax_top.scatter(generations[frame], best_values[frame], s=60, color="#0b57d0")
        ax_top.set_title(f"Evolución de la Aptitud - Generación {generations[frame]}", fontweight="bold")
        ax_top.set_xlabel("Generación")
        ax_top.set_ylabel("Aptitud")
        ax_top.grid(True, alpha=0.25)
        ax_top.legend(loc="best", fontsize=9)

        matrix = _frame_matrix(best_by_generation, frame)
        ax_bottom.imshow(matrix, aspect="auto", cmap="viridis", vmin=0, vmax=3)
        ax_bottom.set_title("Fenotipo del Mejor Individuo de la Generación", fontweight="bold")
        ax_bottom.set_xlabel("Día")
        ax_bottom.set_ylabel("Empleado")
        ax_bottom.set_xticks(range(len(DIAS)))
        ax_bottom.set_xticklabels(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"])

        info = best_by_generation[frame]
        ax_bottom.text(
            0.01,
            -0.22,
            (
                f"Aptitud={info['aptitud']:.6f} | Déficit={info['deficit_cobertura']} | "
                f"Extra={info['horas_extra']} | Insatisfacción={info['insatisfaccion']} | "
                f"Violaciones={info['violaciones_legales']}"
            ),
            transform=ax_bottom.transAxes,
            fontsize=9,
        )

    anim = FuncAnimation(fig, update, frames=len(historial), interval=280, repeat=False)
    writer = FFMpegWriter(fps=4)
    anim.save(str(out_path), writer=writer)
    plt.close(fig)


def generate_profile_artifacts(
    outputs_root: Path,
    run_id: str,
    profile_name: str,
    profile_data: dict[str, Any],
) -> dict[str, str]:
    run_dir = outputs_root / run_id / f"perfil_{profile_name.lower()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    aptitud_png = run_dir / "evolucion_aptitud.png"
    best_csv = run_dir / "mejor_por_generacion.csv"
    ranking_csv = run_dir / "ranking_final.csv"
    schedule_csv = run_dir / "horario_mejor_global.csv"
    video_mp4 = run_dir / "resumen_optimizacion.mp4"

    _export_aptitude_plot(profile_data["historial"], aptitud_png)
    _export_best_by_generation_csv(profile_data["mejores_por_generacion"], best_csv)
    _export_ranking_csv(profile_data["ranking"], ranking_csv)
    _export_schedule_csv(profile_data["horario"], schedule_csv)
    _export_evolution_video(profile_data["historial"], profile_data["mejores_por_generacion"], video_mp4)

    base = f"/outputs/{run_id}/perfil_{profile_name.lower()}"
    return {
        "grafica_aptitud": f"{base}/evolucion_aptitud.png",
        "tabla_mejor_por_generacion": f"{base}/mejor_por_generacion.csv",
        "tabla_ranking": f"{base}/ranking_final.csv",
        "tabla_horario": f"{base}/horario_mejor_global.csv",
        "video_resumen": f"{base}/resumen_optimizacion.mp4",
    }
"""Export results; no epidemiological logic belongs in this module."""

from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import uuid

import pandas as pd

from src import __version__
from src.config import SimulationConfig


def summarize(history: pd.DataFrame) -> dict:
    peak_row = history.loc[history["I"].idxmax()]
    final = history.iloc[-1]
    return {
        "simulated_days": float(final["day"]),
        "peak_infectious": int(peak_row["I"]),
        "peak_day": float(peak_row["day"]),
        "cumulative_infections": int(final["cumulative_infections"]),
        "new_infections": int(history["new_infections"].sum()),
        "final_states": {state: int(final[state]) for state in "SEIR"},
    }


def _git_metadata() -> dict:
    root = Path(__file__).resolve().parents[1]
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        ).stdout.strip())
        return {"commit": commit, "dirty": dirty}
    except (OSError, subprocess.SubprocessError):
        return {"commit": None, "dirty": None}


def save_plot(history: pd.DataFrame, path: Path) -> None:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(10, 5.5), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    labels = {"S": "S — podatni", "E": "E — zakażeni, niezakaźni", "I": "I — zakaźni", "R": "R — ozdrowiali"}
    colors = {"S": "#3673a5", "E": "#e3a526", "I": "#d34f4f", "R": "#418a67"}
    for state in "SEIR":
        axes.plot(history["day"], history[state], label=labels[state], color=colors[state], linewidth=2)
    axes.set(title="Przebieg symulacji SEIR — model bazowy", xlabel="Dzień symulacji", ylabel="Liczba osób")
    axes.set_ylim(bottom=0)
    axes.grid(alpha=0.2)
    axes.legend(frameon=False)
    figure.savefig(path, dpi=160)


def save_results(
    history: pd.DataFrame,
    config: SimulationConfig,
    output_root: Path,
    elapsed_seconds: float,
    *,
    plot: bool = True,
    components: dict[str, str] | None = None,
) -> Path:
    now = datetime.now(timezone.utc)
    run_name = f"{now:%Y%m%d_%H%M%S}_seed{config.seed}_{uuid.uuid4().hex[:8]}"
    output = output_root / run_name
    output.mkdir(parents=True, exist_ok=False)
    history.to_csv(output / "metrics.csv", index=False, encoding="utf-8")
    payloads = {
        "config.json": config.to_dict(),
        "summary.json": summarize(history),
        "metadata.json": {
            "created_utc": now.isoformat(),
            "application_version": __version__,
            "python": platform.python_version(),
            "packages": {name: version(name) for name in ("mesa", "numpy", "scipy", "pandas", "matplotlib")},
            "git": _git_metadata(),
            "simulation_seconds": elapsed_seconds,
            "components": components or {},
        },
    }
    for name, payload in payloads.items():
        (output / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if plot:
        save_plot(history, output / "seir.png")
    return output

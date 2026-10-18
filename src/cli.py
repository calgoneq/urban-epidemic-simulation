"""Command-line entry point, independent of the future Streamlit dashboard."""

import argparse
from dataclasses import replace
from pathlib import Path
import time

from src.config import SimulationConfig
from src.model import EpidemicModel
from src.results import save_results, summarize


ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Uruchom bazową symulację epidemii SEIR.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "default.json")
    parser.add_argument("--days", type=int, help="Nadpisz liczbę dni z konfiguracji.")
    parser.add_argument("--population", type=int, help="Nadpisz wielkość populacji.")
    parser.add_argument("--seed", type=int, help="Ziarno generatora losowego.")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "runs", help="Katalog nadrzędny wyników; każdy przebieg ma własny podkatalog.")
    parser.add_argument("--no-plot", action="store_true", help="Zapisz dane bez pliku PNG.")
    args = parser.parse_args(argv)
    try:
        config = SimulationConfig.from_json(args.config)
        overrides = {name: getattr(args, name) for name in ("days", "population", "seed") if getattr(args, name) is not None}
        config = replace(config, **overrides)
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))

    print(f"SEIR | populacja={config.population} | dni={config.days} | seed={config.seed}")
    start = time.perf_counter()
    model = EpidemicModel(config)
    history = model.run()
    elapsed = time.perf_counter() - start
    try:
        output = save_results(
            history, config, args.output, elapsed, plot=not args.no_plot,
            components={"city": type(model.city).__name__, "policy": type(model.policy).__name__, "behavior": type(model.behavior).__name__},
        )
    except OSError as error:
        parser.exit(1, f"Nie udało się zapisać wyników: {error}\n")
    summary = summarize(history)
    print("Koniec:", " | ".join(f"{key}={value}" for key, value in summary["final_states"].items()))
    print(f"Nowe zakażenia: {summary['new_infections']}; szczyt I: {summary['peak_infectious']} (dzień {summary['peak_day']:.2f})")
    print(f"Czas obliczeń: {elapsed:.2f} s")
    print(f"Wyniki: {output.resolve()}")
    return 0

import json

import pytest

from src.config import SimulationConfig


@pytest.mark.parametrize("changes", [
    {"population": 0}, {"population": True}, {"population": 2.5},
    {"initial_infected": -1}, {"initial_exposed": -1},
    {"population": 2, "initial_infected": 2, "initial_exposed": 1},
    {"days": 0}, {"days": 1.5}, {"latent_hours": 0}, {"infectious_hours": 0},
    {"contacts_per_day": -1}, {"contacts_per_day": float("nan")},
    {"transmission_probability": 1.01}, {"transmission_probability": float("inf")},
    {"transmission_probability": True}, {"seed": -1},
])
def test_invalid_parameters_are_rejected(changes):
    with pytest.raises(ValueError):
        SimulationConfig(**changes)


def test_config_round_trip(tmp_path):
    original = SimulationConfig(population=30, days=2, seed=0)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(original.to_dict()), encoding="utf-8")
    assert SimulationConfig.from_json(path) == original


def test_config_rejects_typo_in_field_name(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"populationn": 500}', encoding="utf-8")
    with pytest.raises(ValueError, match="populationn"):
        SimulationConfig.from_json(path)


def test_config_accepts_windows_utf8_bom(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"seed": 7}', encoding="utf-8-sig")
    assert SimulationConfig.from_json(path).seed == 7

"""Validated, JSON-serializable simulation settings."""

from dataclasses import asdict, dataclass, fields
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class SimulationConfig:
    population: int = 500
    initial_infected: int = 5
    initial_exposed: int = 0
    days: int = 120
    latent_hours: int = 48
    infectious_hours: int = 120
    contacts_per_day: float = 12.0
    transmission_probability: float = 0.04
    seed: int = 42

    def __post_init__(self) -> None:
        positive_ints = ("population", "days", "latent_hours", "infectious_hours")
        nonnegative_ints = ("initial_infected", "initial_exposed", "seed")
        for name in positive_ints + nonnegative_ints:
            value = getattr(self, name)
            minimum = 1 if name in positive_ints else 0
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} must be an integer >= {minimum}.")
        if self.initial_infected + self.initial_exposed > self.population:
            raise ValueError("initial_infected + initial_exposed exceeds population.")
        for name in ("contacts_per_day", "transmission_probability"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a finite number.")
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and >= 0.")
        if self.transmission_probability > 1:
            raise ValueError("transmission_probability must be in [0, 1].")

    @property
    def total_hours(self) -> int:
        return self.days * 24

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, path: str | Path) -> "SimulationConfig":
        with Path(path).open(encoding="utf-8-sig") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object.")
        unknown = set(data) - {field.name for field in fields(cls)}
        if unknown:
            raise ValueError(f"Unknown configuration fields: {', '.join(sorted(unknown))}")
        return cls(**data)

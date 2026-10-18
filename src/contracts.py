"""Shared interfaces. Coordinate changes to this file before implementation."""

from dataclasses import dataclass
from enum import Enum
import math
from random import Random
from typing import Mapping, Protocol, Sequence


class HealthState(str, Enum):
    SUSCEPTIBLE = "S"
    EXPOSED = "E"
    INFECTIOUS = "I"
    RECOVERED = "R"


def _unit_interval(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number in [0, 1].")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a number in [0, 1].")


@dataclass(frozen=True)
class AgentView:
    unique_id: int
    state: HealthState
    location_id: str


@dataclass(frozen=True)
class PolicyRules:
    name: str = "no_restrictions"
    contact_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Policy name must be a non-empty string.")
        _unit_interval("contact_multiplier", self.contact_multiplier)


@dataclass(frozen=True)
class BehaviorDecision:
    contact_multiplier: float = 1.0
    transmission_multiplier: float = 1.0

    def __post_init__(self) -> None:
        _unit_interval("contact_multiplier", self.contact_multiplier)
        _unit_interval("transmission_multiplier", self.transmission_multiplier)


@dataclass(frozen=True)
class MetricsSnapshot:
    hour: int
    day: float
    S: int
    E: int
    I: int
    R: int
    new_infections: int
    cumulative_infections: int
    policy_name: str
    policy_contact_multiplier: float
    mean_behavior_contact_multiplier: float


class PolicyModel(Protocol):
    def decide(self, metrics: MetricsSnapshot, day: int) -> PolicyRules:
        """Return rules for the next day; do not mutate the epidemic model."""
        ...


class BehaviorModel(Protocol):
    def decide(
        self, agent: AgentView, rules: PolicyRules, public_risk: float, rng: Random
    ) -> BehaviorDecision:
        """Return this agent's decision for one hour."""
        ...


class CityModel(Protocol):
    def locate(
        self,
        agents: Sequence[AgentView],
        rules: PolicyRules,
        decisions: Mapping[int, BehaviorDecision],
        hour: int,
        rng: Random,
    ) -> Mapping[int, str]:
        """Return one location ID per agent, without changing health states."""
        ...

"""City environments: the baseline placeholder and a synthetic city (L-01).

``SyntheticCity`` implements the ``CityModel`` protocol from ``src/contracts.py``.
It builds households, workplaces, schools and leisure venues for the agents it is
asked to locate and moves them according to the daily rhythm of ``src/mobility.py``.
Place IDs are strings such as ``home-0``, ``work-3``, ``school-1``, ``leisure-2``.

Agents are created by the model (Mesa assigns ``unique_id``), so the city does not
know their IDs when it is constructed. It assigns homes and activities lazily on the
first ``locate`` call, drawing only from the ``rng`` passed by the model. Create a
new ``SyntheticCity`` for every independent run.
"""

import math
from collections import Counter
from dataclasses import dataclass, field
from random import Random
from typing import Iterable, Mapping, Sequence

from src.contracts import AgentView, BehaviorDecision, PolicyRules
from src.mobility import HOURS_PER_DAY, PlaceKind, Role, ScheduleConfig, daily_plan


class BaselineCity:
    """One well-mixed location; this is not yet an urban mobility model."""

    def locate(
        self,
        agents: Sequence[AgentView],
        rules: PolicyRules,
        decisions: Mapping[int, BehaviorDecision],
        hour: int,
        rng: Random,
    ) -> Mapping[int, str]:
        return {agent.unique_id: "community" for agent in agents}


@dataclass(frozen=True)
class CityConfig:
    """Demonstration demography; not calibrated to any real city."""

    child_fraction: float = 0.2  # share of people who go to school
    worker_fraction: float = 0.65  # share of non-children who work outside the home
    # Weight of a household of size k + 1 is household_size_weights[k].
    household_size_weights: tuple[float, ...] = (0.28, 0.34, 0.17, 0.13, 0.06, 0.02)
    mean_workplace_size: float = 15.0
    mean_school_size: float = 80.0
    people_per_leisure_venue: float = 50.0
    favorite_venues: int = 2  # leisure venues an agent chooses from
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)

    def __post_init__(self) -> None:
        for name in ("child_fraction", "worker_fraction"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be a number in [0, 1].")
        weights = self.household_size_weights
        if (
            not isinstance(weights, tuple) or not weights
            or any(isinstance(w, bool) or not isinstance(w, (int, float))
                   or not math.isfinite(w) or w < 0 for w in weights)
            or sum(weights) <= 0
        ):
            raise ValueError("household_size_weights must be non-negative with a positive sum.")
        for name in ("mean_workplace_size", "mean_school_size", "people_per_leisure_venue"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) \
                    or not math.isfinite(value) or value < 1:
                raise ValueError(f"{name} must be a finite number >= 1.")
        if type(self.favorite_venues) is not int or self.favorite_venues < 1:
            raise ValueError("favorite_venues must be an integer >= 1.")
        if not isinstance(self.schedule, ScheduleConfig):
            raise ValueError("schedule must be a ScheduleConfig.")


@dataclass(frozen=True)
class Resident:
    """Assignments of one agent; ``workplace``/``school`` are None when not applicable."""

    role: Role
    home: str
    workplace: str | None
    school: str | None
    work_start: int
    favorite_venues: tuple[str, ...]


class SyntheticCity:
    """Households, workplaces, schools and leisure venues with a day/night rhythm.

    ``rules`` and ``decisions`` are accepted for the ``CityModel`` contract but not
    used yet: the engine already applies contact and transmission multipliers, and
    closures of place types need the extended contracts planned for M3.
    """

    def __init__(self, config: CityConfig | None = None):
        self.config = config if config is not None else CityConfig()
        self._residents: dict[int, Resident] = {}
        self._counts = Counter()  # number of homes / works / schools / leisure so far
        self._plan_day: int | None = None
        self._plans: dict[int, tuple[str, ...]] = {}

    # ----------------------------------------------------------------- generation
    def generate(self, agent_ids: Iterable[int], rng: Random) -> None:
        """Assign roles, homes, workplaces, schools and venues to new agents.

        Every call creates new places, so agents added later never share a place
        with earlier ones. Agents that already have assignments are ignored.
        """
        ids = sorted(set(agent_ids) - set(self._residents))
        if not ids:
            return
        cfg = self.config

        roles: dict[int, Role] = {}
        for agent_id in ids:
            if rng.random() < cfg.child_fraction:
                roles[agent_id] = Role.CHILD
            elif rng.random() < cfg.worker_fraction:
                roles[agent_id] = Role.WORKER
            else:
                roles[agent_id] = Role.HOME

        homes = self._make_households(ids, roles, rng)
        workplaces = self._assign_groups(
            [i for i in ids if roles[i] is Role.WORKER], cfg.mean_workplace_size, "work", rng)
        schools = self._assign_groups(
            [i for i in ids if roles[i] is Role.CHILD], cfg.mean_school_size, "school", rng)

        venue_count = max(1, math.ceil(len(ids) / cfg.people_per_leisure_venue))
        first_venue = self._counts["leisure"]
        self._counts["leisure"] += venue_count
        venues = [f"leisure-{first_venue + k}" for k in range(venue_count)]

        for agent_id in ids:
            self._residents[agent_id] = Resident(
                role=roles[agent_id],
                home=homes[agent_id],
                workplace=workplaces.get(agent_id),
                school=schools.get(agent_id),
                work_start=rng.choice(cfg.schedule.work_start_hours),
                favorite_venues=tuple(rng.sample(venues, min(cfg.favorite_venues, venue_count))),
            )

    def _make_households(self, ids: list[int], roles: dict[int, Role], rng: Random) -> dict[int, str]:
        """Partition agents into households, each with an adult when one is available."""
        weights = self.config.household_size_weights
        sizes: list[int] = []
        total = 0
        while total < len(ids):
            size = min(rng.choices(range(1, len(weights) + 1), weights)[0], len(ids) - total)
            sizes.append(size)
            total += size

        adults = [i for i in ids if roles[i] is not Role.CHILD]
        others = [i for i in ids if roles[i] is Role.CHILD]
        rng.shuffle(adults)
        household_count = min(len(sizes), len(adults)) if adults else len(sizes)
        members: list[list[int]] = [[] for _ in range(household_count)]
        for index in range(min(household_count, len(adults))):
            members[index].append(adults.pop())

        rest = adults + others
        rng.shuffle(rest)
        open_slots = [index for index in range(household_count)
                      for _ in range(sizes[index] - len(members[index]))]
        open_slots.reverse()  # pop() from the end keeps household order and is O(1)
        for agent_id in rest:
            if open_slots:
                members[open_slots.pop()].append(agent_id)
            else:  # capacity exhausted because households were limited by adult count
                members[rng.randrange(household_count)].append(agent_id)

        first_home = self._counts["home"]
        self._counts["home"] += household_count
        return {
            agent_id: f"home-{first_home + index}"
            for index, group in enumerate(members) for agent_id in group
        }

    def _assign_groups(self, ids: list[int], mean_size: float, kind: str, rng: Random) -> dict[int, str]:
        """Spread agents over workplaces or schools of uneven (log-normal) sizes."""
        if not ids:
            return {}
        place_count = max(1, math.ceil(len(ids) / mean_size))
        first = self._counts[kind]
        self._counts[kind] += place_count
        weights = [rng.lognormvariate(0, 0.8) for _ in range(place_count)]
        choices = rng.choices(range(place_count), weights, k=len(ids))
        return {agent_id: f"{kind}-{first + index}" for agent_id, index in zip(ids, choices)}

    # ------------------------------------------------------------------- location
    def locate(
        self,
        agents: Sequence[AgentView],
        rules: PolicyRules,
        decisions: Mapping[int, BehaviorDecision],
        hour: int,
        rng: Random,
    ) -> Mapping[int, str]:
        ids = sorted({agent.unique_id for agent in agents})
        day = hour // HOURS_PER_DAY
        if day != self._plan_day:
            self._plan_day, self._plans = day, {}
        self.generate(ids, rng)
        for agent_id in ids:
            if agent_id not in self._plans:
                self._plans[agent_id] = self._plan_locations(agent_id, day, rng)
        return {agent_id: self._plans[agent_id][hour % HOURS_PER_DAY] for agent_id in ids}

    def _plan_locations(self, agent_id: int, day: int, rng: Random) -> tuple[str, ...]:
        resident = self._residents[agent_id]
        kinds = daily_plan(resident.role, resident.work_start, day, self.config.schedule, rng)
        venue = rng.choice(resident.favorite_venues)  # one venue per outing day
        places = {
            PlaceKind.HOME: resident.home,
            PlaceKind.WORK: resident.workplace,
            PlaceKind.SCHOOL: resident.school,
            PlaceKind.LEISURE: venue,
        }
        return tuple(places[kind] for kind in kinds)

    # ---------------------------------------------------------------- inspection
    def resident(self, agent_id: int) -> Resident:
        return self._residents[agent_id]

    def household(self, home_id: str) -> list[int]:
        return sorted(i for i, r in self._residents.items() if r.home == home_id)

    def summary(self) -> dict[str, int]:
        """Counts of people by role and of places that have at least one user."""
        people = Counter(r.role.value for r in self._residents.values())
        return {
            "agents": len(self._residents),
            "children": people["child"],
            "workers": people["worker"],
            "home_role": people["home"],
            "households": len({r.home for r in self._residents.values()}),
            "workplaces": len({r.workplace for r in self._residents.values() if r.workplace}),
            "schools": len({r.school for r in self._residents.values() if r.school}),
            "leisure_venues": self._counts["leisure"],
        }


def _demo(population: int = 500, days: int = 60, seed: int = 42) -> None:
    from src.config import SimulationConfig
    from src.model import EpidemicModel

    config = SimulationConfig(population=population, days=days, seed=seed)
    for name, city in (("BaselineCity", BaselineCity()), ("SyntheticCity", SyntheticCity())):
        last = EpidemicModel(config, city=city).run().iloc[-1]
        print(f"{name:14s} dzień {days}: S={last['S']:.0f} E={last['E']:.0f} "
              f"I={last['I']:.0f} R={last['R']:.0f} "
              f"zakażenia łącznie={last['cumulative_infections']:.0f}")
        if isinstance(city, SyntheticCity):
            print("  struktura miasta:", city.summary())


if __name__ == "__main__":
    _demo()

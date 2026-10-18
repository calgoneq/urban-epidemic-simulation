"""Synchronous, hourly SEIR model with replaceable city, policy and behavior."""

from collections import Counter, defaultdict
from dataclasses import fields
import math

import mesa
from mesa.datacollection import DataCollector
import pandas as pd

from src.agent import PersonAgent
from src.behavior import NeutralBehavior
from src.city import BaselineCity
from src.config import SimulationConfig
from src.contracts import (
    BehaviorModel, CityModel, HealthState, MetricsSnapshot, PolicyModel, PolicyRules,
)
from src.policies import NoRestrictions


class EpidemicModel(mesa.Model):
    def __init__(
        self,
        config: SimulationConfig,
        *,
        city: CityModel | None = None,
        policy: PolicyModel | None = None,
        behavior: BehaviorModel | None = None,
    ):
        super().__init__(seed=config.seed)
        self.config = config
        self.city = city if city is not None else BaselineCity()
        self.policy = policy if policy is not None else NoRestrictions()
        self.behavior = behavior if behavior is not None else NeutralBehavior()
        self.elapsed_hours = 0
        self.cumulative_infections = config.initial_infected + config.initial_exposed
        self.rules = PolicyRules()
        self.mean_behavior_contact_multiplier = 1.0

        states = (
            [HealthState.INFECTIOUS] * config.initial_infected
            + [HealthState.EXPOSED] * config.initial_exposed
            + [HealthState.SUSCEPTIBLE] * (config.population - self.cumulative_infections)
        )
        self.random.shuffle(states)
        for state in states:
            PersonAgent(self, state)

        initial = self._snapshot(new_infections=0)
        self.rules = self.policy.decide(initial, day=0)
        self.metrics = self._snapshot(new_infections=0)
        self.datacollector = DataCollector(
            model_reporters={
                field.name: (lambda model, name=field.name: getattr(model.metrics, name))
                for field in fields(MetricsSnapshot)
            }
        )
        self.datacollector.collect(self)

    def _snapshot(self, new_infections: int) -> MetricsSnapshot:
        counts = Counter(agent.state for agent in self.agents)
        return MetricsSnapshot(
            hour=self.elapsed_hours,
            day=self.elapsed_hours / 24,
            S=counts[HealthState.SUSCEPTIBLE],
            E=counts[HealthState.EXPOSED],
            I=counts[HealthState.INFECTIOUS],
            R=counts[HealthState.RECOVERED],
            new_infections=new_infections,
            cumulative_infections=self.cumulative_infections,
            policy_name=self.rules.name,
            policy_contact_multiplier=self.rules.contact_multiplier,
            mean_behavior_contact_multiplier=self.mean_behavior_contact_multiplier,
        )

    def step(self) -> None:
        if self.elapsed_hours >= self.config.total_hours:
            self.running = False
            return
        hour = self.elapsed_hours
        if hour > 0 and hour % 24 == 0:
            self.rules = self.policy.decide(self.metrics, day=hour // 24)

        people = list(self.agents)
        views = tuple(agent.view() for agent in people)
        # No detection system exists yet: this is explicitly a true-prevalence
        # proxy. NeutralBehavior ignores it; see docs/MODEL.md before extending.
        public_risk = self.metrics.I / self.config.population
        decisions = {
            view.unique_id: self.behavior.decide(view, self.rules, public_risk, self.random)
            for view in views
        }
        locations = self.city.locate(views, self.rules, decisions, hour, self.random)
        if set(locations) != {agent.unique_id for agent in people}:
            raise ValueError("City must return exactly one location for every agent.")
        if any(not isinstance(place, str) or not place.strip() for place in locations.values()):
            raise ValueError("Location IDs must be non-empty strings.")

        groups = defaultdict(list)
        for agent in people:
            agent.location_id = locations[agent.unique_id]
            groups[agent.location_id].append(agent)

        # Calculate all exposures from the same state, then apply them together.
        newly_exposed = []
        rate = self.config.contacts_per_day / 24 * self.rules.contact_multiplier
        for group in groups.values():
            if len(group) < 2 or rate == 0 or self.config.transmission_probability == 0:
                continue
            infectious_weight = sum(
                decisions[agent.unique_id].contact_multiplier
                * decisions[agent.unique_id].transmission_multiplier
                for agent in group if agent.state is HealthState.INFECTIOUS
            )
            if infectious_weight == 0:
                continue
            for agent in group:
                if agent.state is not HealthState.SUSCEPTIBLE:
                    continue
                decision = decisions[agent.unique_id]
                hazard = (
                    rate * self.config.transmission_probability
                    * infectious_weight / (len(group) - 1)
                    * decision.contact_multiplier * decision.transmission_multiplier
                )
                probability = -math.expm1(-hazard)
                if self.random.random() < probability:
                    newly_exposed.append(agent)

        next_hour = hour + 1
        for agent in people:
            agent.advance_health(next_hour)
        for agent in newly_exposed:
            agent.expose(next_hour)

        self.elapsed_hours = next_hour
        self.cumulative_infections += len(newly_exposed)
        self.mean_behavior_contact_multiplier = (
            sum(item.contact_multiplier for item in decisions.values()) / len(people)
        )
        self.metrics = self._snapshot(new_infections=len(newly_exposed))
        self.datacollector.collect(self)
        self.running = self.elapsed_hours < self.config.total_hours

    def run(self) -> pd.DataFrame:
        """Finish the configured horizon, including any already completed hours."""
        while self.elapsed_hours < self.config.total_hours:
            self.step()
        return self.datacollector.get_model_vars_dataframe().copy()

import pytest

from src.config import SimulationConfig
from src.contracts import BehaviorDecision, PolicyRules
from src.model import EpidemicModel


class ZeroContactPolicy:
    def decide(self, metrics, day):
        return PolicyRules(name="zero_contacts", contact_multiplier=0)


class FullyProtectedBehavior:
    def decide(self, agent, rules, public_risk, rng):
        return BehaviorDecision(transmission_multiplier=0)


class SeparateLocations:
    def locate(self, agents, rules, decisions, hour, rng):
        return {agent.unique_id: f"place-{agent.unique_id}" for agent in agents}


@pytest.mark.parametrize("modules", [
    {"policy": ZeroContactPolicy()},
    {"behavior": FullyProtectedBehavior()},
    {"city": SeparateLocations()},
])
def test_modules_actually_change_transmission(modules):
    config = SimulationConfig(population=20, initial_infected=1, days=2,
                              contacts_per_day=1_000_000, transmission_probability=1)
    history = EpidemicModel(config, **modules).run()
    assert history["new_infections"].sum() == 0


def test_policy_is_evaluated_once_per_day():
    class RecordingPolicy:
        def __init__(self):
            self.days = []

        def decide(self, metrics, day):
            self.days.append(day)
            return PolicyRules(name=f"day-{day}")

    policy = RecordingPolicy()
    model = EpidemicModel(SimulationConfig(population=5, days=3), policy=policy)
    model.run()
    assert policy.days == [0, 1, 2]
    assert model.metrics.policy_name == "day-2"


def test_city_must_locate_every_agent():
    class IncompleteCity:
        def locate(self, agents, rules, decisions, hour, rng):
            return {}

    model = EpidemicModel(SimulationConfig(), city=IncompleteCity())
    with pytest.raises(ValueError, match="every agent"):
        model.step()


@pytest.mark.parametrize("factory", [PolicyRules, BehaviorDecision])
def test_multipliers_cannot_be_outside_unit_interval(factory):
    with pytest.raises(ValueError):
        factory(contact_multiplier=1.1)

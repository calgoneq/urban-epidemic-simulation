from dataclasses import replace

from pandas.testing import assert_frame_equal
import pytest

from src.config import SimulationConfig
from src.contracts import HealthState
from src.model import EpidemicModel


def test_population_and_infection_accounting_are_conserved():
    config = SimulationConfig(population=120, days=30, seed=8)
    history = EpidemicModel(config).run()
    assert len(history) == 30 * 24 + 1
    assert history["hour"].tolist() == list(range(30 * 24 + 1))
    assert (history[list("SEIR")].sum(axis=1) == config.population).all()
    assert (history[list("SEIR")] >= 0).all().all()
    assert (history["S"].diff().dropna() <= 0).all()
    assert (history["R"].diff().dropna() >= 0).all()
    assert (history["cumulative_infections"] == config.population - history["S"]).all()
    expected = history["new_infections"].cumsum() + config.initial_infected + config.initial_exposed
    assert (history["cumulative_infections"] == expected).all()


def test_no_initial_infection_means_no_epidemic():
    history = EpidemicModel(SimulationConfig(population=20, initial_infected=0, days=5)).run()
    assert (history["S"] == 20).all()
    assert (history[["E", "I", "R", "new_infections"]] == 0).all().all()


@pytest.mark.parametrize("change", [{"transmission_probability": 0}, {"contacts_per_day": 0}])
def test_zero_transmission_or_contacts_prevents_new_cases(change):
    history = EpidemicModel(SimulationConfig(population=20, initial_infected=2, days=10, **change)).run()
    assert history["new_infections"].sum() == 0
    assert history.iloc[-1]["R"] == 2
    assert history.iloc[-1]["S"] == 18


def test_progression_uses_exact_hour_boundaries():
    config = SimulationConfig(population=1, initial_infected=0, initial_exposed=1, latent_hours=2, infectious_hours=3, days=1)
    model = EpidemicModel(config)
    agent = next(iter(model.agents))
    states = [agent.state]
    for _ in range(5):
        model.step()
        states.append(agent.state)
    assert states == [HealthState.EXPOSED, HealthState.EXPOSED, HealthState.INFECTIOUS,
                      HealthState.INFECTIOUS, HealthState.INFECTIOUS, HealthState.RECOVERED]


def test_new_case_gets_full_latency_and_does_not_advance_twice():
    config = SimulationConfig(population=2, initial_infected=1, latent_hours=1, infectious_hours=1,
                              contacts_per_day=1_000_000, transmission_probability=1, days=1)
    model = EpidemicModel(config)
    susceptible = next(agent for agent in model.agents if agent.state is HealthState.SUSCEPTIBLE)
    model.step()
    assert susceptible.state is HealthState.EXPOSED
    assert model.metrics.R == 1
    model.step()
    assert susceptible.state is HealthState.INFECTIOUS
    model.step()
    assert susceptible.state is HealthState.RECOVERED


def test_exposed_agent_cannot_transmit_before_latency_ends():
    config = SimulationConfig(population=2, initial_infected=0, initial_exposed=1, latent_hours=2,
                              contacts_per_day=1_000_000, transmission_probability=1, days=1)
    model = EpidemicModel(config)
    model.step()
    model.step()
    assert model.metrics.S == 1
    assert model.metrics.I == 1
    model.step()
    assert model.metrics.S == 0
    assert model.metrics.E == 1


@pytest.mark.parametrize("draw, expected_exposed", [(0.39, 1), (0.40, 0)])
def test_hourly_exposure_probability_has_correct_scale(draw, expected_exposed):
    # One expected contact/hour and p=0.5 give P(exposure)=1-exp(-0.5), about 0.3935.
    config = SimulationConfig(population=2, initial_infected=1, contacts_per_day=24,
                              transmission_probability=0.5, days=1)
    model = EpidemicModel(config)
    model.random.random = lambda: draw
    model.step()
    assert model.metrics.E == expected_exposed


def test_seed_reproduces_full_history_and_run_is_idempotent():
    config = SimulationConfig(population=60, days=10, seed=123)
    first = EpidemicModel(config)
    expected = first.run()
    assert_frame_equal(expected, EpidemicModel(replace(config)).run())
    assert_frame_equal(expected, first.run())
    assert not first.running

import pandas as pd
import pytest

from src.config import SimulationConfig
from src.model import EpidemicModel
from src.policies import ConstantRestrictions, NoRestrictions, ScheduledRestrictions


def test_constant_policy_returns_same_rules_every_day():
    policy = ConstantRestrictions(0.5)
    for day in (0, 1, 30, 119):
        rules = policy.decide(None, day)
        assert rules.contact_multiplier == 0.5
        assert rules.name == "constant_0.5"


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), True])
def test_constant_policy_rejects_invalid_multiplier(value):
    with pytest.raises(ValueError):
        ConstantRestrictions(value)


@pytest.mark.parametrize("value", [0, 1, 0.5])
def test_constant_policy_accepts_boundary_values(value):
    assert ConstantRestrictions(value).decide(None, 0).contact_multiplier == value


def test_multiplier_one_matches_no_restrictions():
    config = SimulationConfig(population=50, initial_infected=2, days=5)
    baseline = EpidemicModel(config, policy=NoRestrictions()).run()
    constant = EpidemicModel(config, policy=ConstantRestrictions(1.0)).run()
    pd.testing.assert_frame_equal(
        baseline.drop(columns=["policy_name"]),
        constant.drop(columns=["policy_name"]),
    )


def test_multiplier_zero_stops_new_infections():
    config = SimulationConfig(population=20, initial_infected=1, days=3,
                              contacts_per_day=1_000_000, transmission_probability=1)
    history = EpidemicModel(config, policy=ConstantRestrictions(0)).run()
    assert history["new_infections"].sum() == 0



def test_schedule_half_open_boundaries():
    policy = ScheduledRestrictions([(5, 10, 0.3)])
    multipliers = {d: policy.decide(None, d).contact_multiplier for d in (4, 5, 9, 10)}
    assert multipliers == {4: 1.0, 5: 0.3, 9: 0.3, 10: 1.0}


def test_schedule_unrestricted_before_between_and_after():
    policy = ScheduledRestrictions([(5, 10, 0.3), (20, 25, 0.6)])
    for day in (0, 4, 10, 15, 19, 25, 100):
        rules = policy.decide(None, day)
        assert rules.contact_multiplier == 1.0
        assert rules.name == "no_restrictions"
    assert policy.decide(None, 22).contact_multiplier == 0.6


def test_schedule_empty_behaves_like_no_restrictions():
    policy = ScheduledRestrictions([])
    assert policy.decide(None, 3) == NoRestrictions().decide(None, 3)


def test_schedule_accepts_touching_and_unsorted_periods():
    policy = ScheduledRestrictions([(20, 30, 0.5), (10, 20, 0.3)])
    assert policy.decide(None, 19).contact_multiplier == 0.3
    assert policy.decide(None, 20).contact_multiplier == 0.5


@pytest.mark.parametrize("periods", [
    [(10, 20, 0.3), (15, 25, 0.5)],   # overlap
    [(10, 20, 0.3), (10, 12, 0.5)],   # same start
    [(-1, 5, 0.3)],                   # negative start
    [(5, 5, 0.3)],                    # empty period
    [(10, 5, 0.3)],                   # end before start
    [(1, 5, 1.5)],                    # bad multiplier
    [(1.5, 5, 0.3)],                  # non-integer day
    [(True, 5, 0.3)],                 # bool is not a day
    [(1, 5)],                         # wrong tuple length
])
def test_schedule_rejects_invalid_periods(periods):
    with pytest.raises(ValueError):
        ScheduledRestrictions(periods)


def test_schedule_in_model_history_is_shifted_by_one_day():
    # The CSV row at hour h describes the hour that just ended, so day 1
    # (hours 24-47) shows up in rows hour=25..48.
    config = SimulationConfig(population=30, initial_infected=2, days=3)
    history = EpidemicModel(config, policy=ScheduledRestrictions([(1, 2, 0.5)])).run()
    by_hour = history.set_index("hour")["policy_contact_multiplier"]
    assert by_hour[24] == 1.0
    assert by_hour[25] == 0.5
    assert by_hour[48] == 0.5
    assert by_hour[49] == 1.0
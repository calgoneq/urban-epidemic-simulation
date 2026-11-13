from dataclasses import replace
from random import Random

import pytest

from src.city import CityConfig, SyntheticCity
from src.config import SimulationConfig
from src.contracts import AgentView, HealthState, PolicyRules
from src.mobility import PlaceKind, Role, ScheduleConfig, daily_plan
from src.model import EpidemicModel

NO_LEISURE = ScheduleConfig(
    leisure_probability_weekday=0, leisure_probability_home_role=0, leisure_probability_weekend=0,
)


def views(count: int, first_id: int = 1) -> list[AgentView]:
    return [AgentView(i, HealthState.SUSCEPTIBLE, "community") for i in range(first_id, first_id + count)]


def trajectory(city: SyntheticCity, agents, hours: int, rng: Random) -> list[dict[int, str]]:
    return [dict(city.locate(agents, PolicyRules(), {}, hour, rng)) for hour in range(hours)]


def place(agent_id: int, history: list[dict[int, str]], hour: int) -> str:
    return history[hour][agent_id]


@pytest.fixture
def strict_city():
    """A city without leisure outings, so schedules are exactly work/school/home."""
    city = SyntheticCity(CityConfig(schedule=NO_LEISURE))
    agents = views(200)
    return city, agents, trajectory(city, agents, 14 * 24, Random(1))


# ------------------------------------------------------------------ assignments
def test_every_agent_has_a_home_and_exactly_one_location_each_hour():
    city = SyntheticCity()
    agents = views(150)
    history = trajectory(city, agents, 7 * 24, Random(3))
    for locations in history:
        assert set(locations) == {a.unique_id for a in agents}
        assert all(isinstance(p, str) and p.strip() for p in locations.values())
    for agent in agents:
        assert city.resident(agent.unique_id).home.startswith("home-")
    assert city.summary()["agents"] == 150


def test_roles_determine_workplace_and_school_assignments():
    city = SyntheticCity()
    agents = views(300)
    city.generate([a.unique_id for a in agents], Random(5))
    roles = {r: 0 for r in Role}
    for agent in agents:
        resident = city.resident(agent.unique_id)
        roles[resident.role] += 1
        assert (resident.workplace is not None) == (resident.role is Role.WORKER)
        assert (resident.school is not None) == (resident.role is Role.CHILD)
    assert all(count > 0 for count in roles.values())


def test_every_household_has_an_adult_when_adults_exist():
    city = SyntheticCity(CityConfig(child_fraction=0.4))
    ids = list(range(1, 301))
    city.generate(ids, Random(9))
    homes = {city.resident(i).home for i in ids}
    for home in homes:
        assert any(city.resident(i).role is not Role.CHILD for i in city.household(home))
    assert sum(len(city.household(home)) for home in homes) == len(ids)


def test_household_sizes_follow_configuration():
    city = SyntheticCity(CityConfig(household_size_weights=(0, 0, 1), child_fraction=0))
    city.generate(range(1, 31), Random(2))
    sizes = {len(city.household(f"home-{i}")) for i in range(city.summary()["households"])}
    assert sizes == {3}


# --------------------------------------------------------------------- schedule
def test_night_hours_are_spent_at_home(strict_city):
    city, agents, history = strict_city
    for day in range(14):
        for hour_of_day in (0, 1, 2, 3, 4, 5, 22, 23):
            for agent in agents:
                assert place(agent.unique_id, history, day * 24 + hour_of_day) == \
                    city.resident(agent.unique_id).home


def test_workers_and_children_follow_weekday_plan(strict_city):
    city, agents, history = strict_city
    cfg = city.config.schedule
    for day in range(14):
        weekday = day % 7 not in cfg.weekend_days
        for agent in agents:
            resident = city.resident(agent.unique_id)
            for hour_of_day in range(24):
                expected = resident.home
                if weekday and resident.role is Role.WORKER and \
                        resident.work_start <= hour_of_day < resident.work_start + cfg.work_hours:
                    expected = resident.workplace
                if weekday and resident.role is Role.CHILD and \
                        cfg.school_start_hour <= hour_of_day < cfg.school_start_hour + cfg.school_hours:
                    expected = resident.school
                assert place(agent.unique_id, history, day * 24 + hour_of_day) == expected


def test_people_return_home_after_work_and_school(strict_city):
    city, agents, history = strict_city
    for agent in agents:
        resident = city.resident(agent.unique_id)
        if resident.role is Role.WORKER:
            at_work = [h for h in range(24) if place(agent.unique_id, history, h) == resident.workplace]
            assert at_work == list(range(resident.work_start, resident.work_start + 8))
            assert place(agent.unique_id, history, at_work[-1] + 1) == resident.home
        if resident.role is Role.CHILD:
            at_school = [h for h in range(24) if place(agent.unique_id, history, h) == resident.school]
            assert at_school == list(range(8, 15))
            assert place(agent.unique_id, history, 15) == resident.home


def test_weekend_is_spent_at_home_without_leisure(strict_city):
    city, agents, history = strict_city
    for day in (5, 6, 12, 13):
        for agent in agents:
            home = city.resident(agent.unique_id).home
            assert all(place(agent.unique_id, history, day * 24 + h) == home for h in range(24))


def test_leisure_never_replaces_work_or_school_and_uses_favorite_venues():
    city = SyntheticCity(CityConfig(schedule=ScheduleConfig(
        leisure_probability_weekday=1, leisure_probability_home_role=1, leisure_probability_weekend=1)))
    agents = views(200)
    history = trajectory(city, agents, 7 * 24, Random(4))
    outings = 0
    for agent in agents:
        resident = city.resident(agent.unique_id)
        for hour in range(7 * 24):
            location = place(agent.unique_id, history, hour)
            if location.startswith("leisure-"):
                outings += 1
                assert location in resident.favorite_venues
            if resident.role is Role.WORKER and hour // 24 < 5 and 9 <= hour % 24 < 15:
                assert location == resident.workplace
            if resident.role is Role.CHILD and hour // 24 < 5 and 8 <= hour % 24 < 15:
                assert location == resident.school
    assert outings > 0


def test_daily_plan_has_24_hours_and_leisure_respects_probability():
    cfg = ScheduleConfig()
    rng = Random(0)
    plans = [daily_plan(Role.WORKER, 8, 0, cfg, rng) for _ in range(2000)]
    assert all(len(plan) == 24 for plan in plans)
    share = sum(PlaceKind.LEISURE in plan for plan in plans) / len(plans)
    assert abs(share - cfg.leisure_probability_weekday) < 0.05
    assert all(plan[8:16] == (PlaceKind.WORK,) * 8 for plan in plans)


def test_weekend_days_can_be_disabled():
    cfg = ScheduleConfig(weekend_days=(), leisure_probability_weekday=0)
    assert all(not cfg.is_weekend(day) for day in range(14))
    plan = daily_plan(Role.WORKER, 8, 5, cfg, Random(0))
    assert plan[8:16] == (PlaceKind.WORK,) * 8


# ----------------------------------------------------------- contract and rng
def test_plan_is_stable_within_a_day_and_reproducible_with_seed():
    agents = views(80)
    first = trajectory(SyntheticCity(), agents, 72, Random(11))
    assert first == trajectory(SyntheticCity(), agents, 72, Random(11))
    assert first != trajectory(SyntheticCity(), agents, 72, Random(12))

    city = SyntheticCity()
    again = dict(city.locate(agents, PolicyRules(), {}, 10, Random(1)))
    assert again == dict(city.locate(agents, PolicyRules(), {}, 10, Random(999)))


def test_city_does_not_use_global_random_state():
    import random
    random.seed(1)
    expected = random.random()
    random.seed(1)
    trajectory(SyntheticCity(), views(30), 48, Random(1))
    assert random.random() == expected


def test_agents_appearing_later_get_their_own_places():
    city = SyntheticCity()
    rng = Random(6)
    old = views(20)
    city.locate(old, PolicyRules(), {}, 0, rng)
    new = views(5, first_id=100)
    locations = city.locate(old + new, PolicyRules(), {}, 1, rng)
    assert set(locations) == {a.unique_id for a in old + new}
    old_places = {r.home for i in range(1, 21) for r in [city.resident(i)]}
    assert all(city.resident(i).home not in old_places for i in range(100, 105))


def test_empty_agent_list_returns_empty_mapping():
    assert dict(SyntheticCity().locate([], PolicyRules(), {}, 0, Random(0))) == {}


@pytest.mark.parametrize("bad", [
    {"child_fraction": 1.5}, {"worker_fraction": -0.1}, {"household_size_weights": ()},
    {"household_size_weights": (0, 0)}, {"household_size_weights": (1, -1)},
    {"mean_workplace_size": 0}, {"mean_school_size": float("nan")},
    {"people_per_leisure_venue": 0.5}, {"favorite_venues": 0}, {"schedule": None},
])
def test_city_config_rejects_invalid_values(bad):
    with pytest.raises(ValueError):
        CityConfig(**bad)


@pytest.mark.parametrize("bad", [
    {"work_start_hours": ()}, {"work_start_hours": (20,), "work_hours": 8},
    {"school_start_hour": 20}, {"leisure_probability_weekday": 2},
    {"weekend_days": (7,)}, {"evening_start_hours": (20, 18)},
    {"evening_start_hours": (18, 23)}, {"leisure_hours": 0},
])
def test_schedule_config_rejects_invalid_values(bad):
    with pytest.raises(ValueError):
        ScheduleConfig(**bad)


# --------------------------------------------------------------- with the engine
def test_engine_runs_with_synthetic_city_and_conserves_population():
    config = SimulationConfig(population=120, days=10, seed=8)
    history = EpidemicModel(config, city=SyntheticCity()).run()
    assert len(history) == 10 * 24 + 1
    assert (history[list("SEIR")].sum(axis=1) == config.population).all()


def test_engine_with_synthetic_city_is_reproducible():
    config = SimulationConfig(population=80, days=8, seed=5)
    first = EpidemicModel(config, city=SyntheticCity()).run()
    second = EpidemicModel(replace(config), city=SyntheticCity()).run()
    assert first.equals(second)


def test_separate_locations_stop_transmission_in_engine():
    """Everyone alone at home: no shared place, so no infection can happen."""
    city = SyntheticCity(CityConfig(
        household_size_weights=(1,), child_fraction=0, worker_fraction=0, schedule=NO_LEISURE))
    config = SimulationConfig(population=20, initial_infected=1, days=3,
                              contacts_per_day=1_000_000, transmission_probability=1)
    assert EpidemicModel(config, city=city).run()["new_infections"].sum() == 0


def test_shared_household_allows_transmission_in_engine():
    """Positive control: the same setup with one shared household does infect."""
    city = SyntheticCity(CityConfig(
        household_size_weights=(0, 0, 0, 0, 1), child_fraction=0, worker_fraction=0,
        schedule=NO_LEISURE))
    config = SimulationConfig(population=5, initial_infected=1, days=1,
                              contacts_per_day=1_000_000, transmission_probability=1)
    assert EpidemicModel(config, city=city).run()["new_infections"].sum() == 4


def test_workplaces_separate_contacts_during_the_day_in_engine():
    """Infection starts at home-less 'work' hours only: night mixing is household-only."""
    city = SyntheticCity(CityConfig(
        household_size_weights=(1,), child_fraction=0, worker_fraction=1,
        mean_workplace_size=1000, schedule=NO_LEISURE))
    config = SimulationConfig(population=30, initial_infected=1, days=1,
                              contacts_per_day=1_000_000, transmission_probability=1,
                              latent_hours=1, infectious_hours=100)
    history = EpidemicModel(config, city=city).run()
    infections = history.set_index("hour")["new_infections"]
    night = [h for h in range(1, 25) if (h - 1) % 24 < 7 or (h - 1) % 24 >= 17]
    assert infections.loc[night].sum() == 0
    assert infections.sum() > 0

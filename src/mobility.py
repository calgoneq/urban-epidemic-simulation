"""Daily schedules: which kind of place a person occupies in each hour.

The module is pure: it knows nothing about concrete place IDs or agents. It maps
a person's role and the day type to 24 symbolic place kinds, using only the
random generator it is given. ``src/city.py`` turns the kinds into place IDs.

Time convention (see docs/MODEL.md): ``hour`` counts full hours since the start,
the hour of the day is ``hour % 24`` and day 0 is a Monday.
"""

from dataclasses import dataclass
from enum import Enum
from random import Random

HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7


class Role(str, Enum):
    CHILD = "child"    # goes to school on weekdays
    WORKER = "worker"  # goes to a workplace on weekdays
    HOME = "home"      # no fixed daytime place (e.g. retired, not working)


class PlaceKind(str, Enum):
    HOME = "home"
    WORK = "work"
    SCHOOL = "school"
    LEISURE = "leisure"


def _check_hour(name: str, value: int, low: int = 0, high: int = HOURS_PER_DAY) -> None:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}].")


def _check_probability(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a number in [0, 1].")


@dataclass(frozen=True)
class ScheduleConfig:
    """Demonstration values of the daily rhythm; not calibrated to any real city."""

    work_start_hours: tuple[int, ...] = (7, 8, 9)  # one shift start drawn per worker
    work_hours: int = 8
    school_start_hour: int = 8
    school_hours: int = 7
    weekend_days: tuple[int, ...] = (5, 6)  # day % 7; day 0 is Monday
    leisure_hours: int = 2
    # Probability of one leisure outing per day, by role and day type.
    leisure_probability_weekday: float = 0.25  # workers and children, in the evening
    leisure_probability_home_role: float = 0.5  # non-working people, in the daytime
    leisure_probability_weekend: float = 0.5  # everyone
    evening_start_hours: tuple[int, int] = (18, 20)  # inclusive range of outing starts
    daytime_start_hours: tuple[int, int] = (9, 16)  # weekday outings of HOME role
    weekend_start_hours: tuple[int, int] = (10, 19)  # weekend outings

    def __post_init__(self) -> None:
        if not self.work_start_hours:
            raise ValueError("work_start_hours must not be empty.")
        for start in self.work_start_hours:
            _check_hour("work_start_hours item", start, 0, HOURS_PER_DAY - 1)
        _check_hour("work_hours", self.work_hours, 1, HOURS_PER_DAY)
        _check_hour("school_start_hour", self.school_start_hour, 0, HOURS_PER_DAY - 1)
        _check_hour("school_hours", self.school_hours, 1, HOURS_PER_DAY)
        _check_hour("leisure_hours", self.leisure_hours, 1, HOURS_PER_DAY)
        if max(self.work_start_hours) + self.work_hours > HOURS_PER_DAY:
            raise ValueError("Work shift must end by midnight.")
        if self.school_start_hour + self.school_hours > HOURS_PER_DAY:
            raise ValueError("School day must end by midnight.")
        if not isinstance(self.weekend_days, tuple) or any(
            type(day) is not int or not 0 <= day < DAYS_PER_WEEK for day in self.weekend_days
        ):
            raise ValueError("weekend_days must be a tuple of integers in [0, 6].")
        for name in ("leisure_probability_weekday", "leisure_probability_home_role",
                     "leisure_probability_weekend"):
            _check_probability(name, getattr(self, name))
        for name in ("evening_start_hours", "daytime_start_hours", "weekend_start_hours"):
            window = getattr(self, name)
            if not isinstance(window, tuple) or len(window) != 2:
                raise ValueError(f"{name} must be a (first, last) pair of hours.")
            first, last = window
            _check_hour(name, first, 0, HOURS_PER_DAY - 1)
            _check_hour(name, last, 0, HOURS_PER_DAY - 1)
            if first > last:
                raise ValueError(f"{name} must satisfy first <= last.")
            if last + self.leisure_hours > HOURS_PER_DAY:
                raise ValueError(f"A leisure outing in {name} must end by midnight.")

    def is_weekend(self, day: int) -> bool:
        return day % DAYS_PER_WEEK in self.weekend_days


def daily_plan(
    role: Role,
    work_start: int,
    day: int,
    config: ScheduleConfig,
    rng: Random,
) -> tuple[PlaceKind, ...]:
    """Return exactly 24 place kinds, one per hour of ``day``.

    Everyone sleeps at home. On weekdays workers and children spend a fixed
    block at work or school; on weekends and for the HOME role the day is spent at
    home except for an optional leisure outing. Randomness comes only from ``rng``:
    one draw decides whether there is an outing, a second one when its start hour
    is drawn.
    """
    plan = [PlaceKind.HOME] * HOURS_PER_DAY
    weekend = config.is_weekend(day)

    if not weekend and role is Role.WORKER:
        plan[work_start:work_start + config.work_hours] = (
            [PlaceKind.WORK] * config.work_hours
        )
    elif not weekend and role is Role.CHILD:
        plan[config.school_start_hour:config.school_start_hour + config.school_hours] = (
            [PlaceKind.SCHOOL] * config.school_hours
        )

    if weekend:
        probability, window = config.leisure_probability_weekend, config.weekend_start_hours
    elif role is Role.HOME:
        probability, window = config.leisure_probability_home_role, config.daytime_start_hours
    else:
        probability, window = config.leisure_probability_weekday, config.evening_start_hours

    if rng.random() < probability:
        start = rng.randint(*window)
        for hour in range(start, start + config.leisure_hours):
            if plan[hour] is PlaceKind.HOME:  # never overrides work or school
                plan[hour] = PlaceKind.LEISURE
    return tuple(plan)

"""Default policy and extension point for sanitary strategies."""

from typing import Sequence

from src.contracts import MetricsSnapshot, PolicyRules


class NoRestrictions:
    def decide(self, metrics: MetricsSnapshot, day: int) -> PolicyRules:
        return PolicyRules()


class ConstantRestrictions:
    """Apply the same contact multiplier every day.

    contact_multiplier is the share of normal contacts that remains:
    1.0 means no restrictions, 0.3 means a 70% reduction, 0.0 means no contacts.
    """

    def __init__(self, contact_multiplier: float) -> None:
        # Building the rules here validates the value at creation time.
        self.rules = PolicyRules(
            name=f"constant_{contact_multiplier}",
            contact_multiplier=contact_multiplier,
        )

    def decide(self, metrics: MetricsSnapshot, day: int) -> PolicyRules:
        return self.rules


class ScheduledRestrictions:
    """Apply restrictions on chosen days, no restrictions otherwise.

    periods is a sequence of (start_day, end_day, contact_multiplier).
    Days are counted from 0, as in the model. A period covers the half-open
    range [start_day, end_day), like range(start_day, end_day): the end day
    is NOT included, so (10, 20, ...) and (20, 30, ...) may touch.
    Periods must not overlap. Outside all periods the multiplier is 1.0.
    """

    def __init__(self, periods: Sequence[tuple[int, int, float]]) -> None:
        parsed = []
        for period in periods:
            if len(period) != 3:
                raise ValueError("Each period must be (start_day, end_day, multiplier).")
            start, end, multiplier = period
            for name, value in (("start_day", start), ("end_day", end)):
                if type(value) is not int:
                    raise ValueError(f"{name} must be an integer.")
            if start < 0:
                raise ValueError("start_day must be >= 0.")
            if end <= start:
                raise ValueError("end_day must be greater than start_day.")
            # Building the rules validates the multiplier immediately.
            rules = PolicyRules(
                name=f"scheduled_{multiplier}", contact_multiplier=multiplier
            )
            parsed.append((start, end, rules))

        parsed.sort(key=lambda item: item[0])
        for (_, prev_end, _), (next_start, _, _) in zip(parsed, parsed[1:]):
            if next_start < prev_end:
                raise ValueError("Periods must not overlap.")

        self._periods = tuple(parsed)
        self._no_restrictions = PolicyRules()

    def decide(self, metrics: MetricsSnapshot, day: int) -> PolicyRules:
        for start, end, rules in self._periods:
            if start <= day < end:
                return rules
        return self._no_restrictions
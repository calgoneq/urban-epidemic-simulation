"""Default policy and extension point for sanitary strategies."""

from src.contracts import MetricsSnapshot, PolicyRules


class NoRestrictions:
    def decide(self, metrics: MetricsSnapshot, day: int) -> PolicyRules:
        return PolicyRules()

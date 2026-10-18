"""Baseline environment. Replace with the city and mobility implementation."""

from random import Random
from typing import Mapping, Sequence

from src.contracts import AgentView, BehaviorDecision, PolicyRules


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

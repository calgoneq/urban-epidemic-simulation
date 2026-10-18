"""Neutral behavior used until the behavioral model is implemented."""

from random import Random

from src.contracts import AgentView, BehaviorDecision, PolicyRules


class NeutralBehavior:
    def decide(
        self, agent: AgentView, rules: PolicyRules, public_risk: float, rng: Random
    ) -> BehaviorDecision:
        return BehaviorDecision()

"""Mesa agent and the health-state transitions owned by the core engine."""

from mesa import Agent

from src.contracts import AgentView, HealthState


class PersonAgent(Agent):
    def __init__(self, model, state: HealthState = HealthState.SUSCEPTIBLE):
        super().__init__(model)
        self.state = state
        self.state_since_hour = 0
        self.location_id = "community"

    def view(self) -> AgentView:
        return AgentView(self.unique_id, self.state, self.location_id)

    def expose(self, hour: int) -> None:
        if self.state is not HealthState.SUSCEPTIBLE:
            raise ValueError("Only a susceptible agent can become exposed.")
        self.state = HealthState.EXPOSED
        self.state_since_hour = hour

    def advance_health(self, hour: int) -> None:
        elapsed = hour - self.state_since_hour
        if self.state is HealthState.EXPOSED and elapsed >= self.model.config.latent_hours:
            self.state = HealthState.INFECTIOUS
            self.state_since_hour = hour
        elif (
            self.state is HealthState.INFECTIOUS
            and elapsed >= self.model.config.infectious_hours
        ):
            self.state = HealthState.RECOVERED
            self.state_since_hour = hour

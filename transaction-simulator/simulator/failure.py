import random
from dataclasses import dataclass


@dataclass(slots=True)
class FailureProfile:
    success_rate: float
    failure_rate: float
    timeout_rate: float
    delay_rate: float
    duplicate_rate: float
    provider_unavailable_rate: float
    db_failure_rate: float


class FailureSimulator:
    def __init__(self, profile: FailureProfile):
        self.profile = profile

    def outcome(self) -> str:
        roll = random.random()
        if roll < self.profile.timeout_rate:
            return "timeout"

        roll = random.random()
        if roll < self.profile.provider_unavailable_rate:
            return "provider_unavailable"

        roll = random.random()
        if roll < self.profile.db_failure_rate:
            return "db_failure"

        roll = random.random()
        if roll < self.profile.failure_rate:
            return "failure"

        return "success"

    def should_delay(self) -> bool:
        return random.random() < self.profile.delay_rate

    def should_duplicate(self) -> bool:
        return random.random() < self.profile.duplicate_rate
